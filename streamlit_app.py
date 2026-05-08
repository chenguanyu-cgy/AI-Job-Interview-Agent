import sys
from pathlib import Path

# 把项目根目录加入模块搜索路径
sys.path.append(str(Path(__file__).parent))
import streamlit as st
import os
from datetime import datetime
import json

try:
    from fpdf import FPDF
except:
    pass

from core.ai_client import AIClient
from utils.rag_utils import build_knowledge_base, search_knowledge
from utils.agent_tools import tool_resume_analyze, tool_jd_match, tool_interview_generate
from utils.agent_core import JobAgent

st.set_page_config(
    page_title="AI智能求职助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)


def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def save_session():
    if st.session_state.current_session:
        session_data = {
            "nick_name": st.session_state.nick_name if "nick_name" in st.session_state else "AI助手",
            "nature": st.session_state.nature if "nature" in st.session_state else "通用助手",
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }
        if not os.path.exists("sessions"):
            os.mkdir("sessions")
        with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)


def load_sessions():
    session_list = []
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    session_list.sort(reverse=True)
    return session_list


def load_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data.get("nick_name", "AI助手")
                st.session_state.nature = session_data.get("nature", "通用助手")
                st.session_state.current_session = session_name
    except Exception:
        st.error("加载会话失败!")


def delete_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            os.remove(f"sessions/{session_name}.json")
            if session_name == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_name()
    except Exception:
        st.error("删除会话失败!")


# 🔥 只初始化1次
if "app_init" not in st.session_state:
    st.session_state.ai_client = AIClient()
    # build_knowledge_base()   <--- 已注释，防止启动卡死
    agent = JobAgent(st.session_state.ai_client)
    agent.register_tool("简历解析", tool_resume_analyze)
    agent.register_tool("JD匹配", tool_jd_match)
    agent.register_tool("生成面试题", tool_interview_generate)
    st.session_state.job_agent = agent

    st.session_state.resume_content = ""
    st.session_state.trigger_parse = False
    st.session_state.resume_parsed = None
    st.session_state.jd_content = ""
    st.session_state.jd_match_result = None
    st.session_state.interview_qa = None
    st.session_state.app_init = True

st.title("AI智能伴侣")

system_prompt = """
你是专业友好的AI助手，有资料优先用资料回答，无资料正常回答，不编造。
"""

if "messages" not in st.session_state:
    st.session_state.messages = []
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "AI助手"
if "nature" not in st.session_state:
    st.session_state.nature = "通用助手"
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()

prompt = st.chat_input("请输入您要问的问题")
st.text(f"会话名称: {st.session_state.current_session}")

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

with st.sidebar:
    st.subheader("AI控制面板")
    st.subheader("💼 求职Agent工具")
    st.caption("基于大模型的求职全流程辅助工具")

    if st.button("清空内容", key="clear_btn"):
        st.session_state.resume_content = ""
        st.session_state.trigger_parse = False
        if 'resume_parsed' in st.session_state:
            del st.session_state.resume_parsed

    uploaded_file = st.file_uploader("上传简历PDF", type=["pdf", "txt"])

    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            from pypdf import PdfReader
            pdf_reader = PdfReader(uploaded_file)
            st.session_state.resume_content = "\n".join([page.extract_text() for page in pdf_reader.pages])
            st.success("✅ PDF已自动解析")
        else:
            st.session_state.resume_content = uploaded_file.read().decode("utf-8")
            st.success("✅ TXT已读取")

    with st.expander("📄 简历智能解析", expanded=True):
        resume_text = st.text_area("简历文本", height=150, value=st.session_state.resume_content)
        st.session_state.resume_content = resume_text

        if st.button("一键解析简历", use_container_width=True, type="primary"):
            st.session_state.trigger_parse = True

        if st.session_state.trigger_parse and st.session_state.resume_content.strip():
            with st.spinner("AI解析中..."):
                result = tool_resume_analyze(st.session_state.resume_content, st.session_state.ai_client)
                st.session_state.resume_parsed = result
                st.session_state.trigger_parse = False

        if st.session_state.get('resume_parsed'):
            st.divider()
            st.markdown(st.session_state.resume_parsed)

    with st.sidebar.expander("📌 JD简历智能匹配", expanded=False):
        st.caption("粘贴岗位JD → 自动分析匹配度/优势/短板/面试题")
        jd_text = st.text_area("粘贴岗位JD描述", height=120, value=st.session_state.jd_content)
        st.session_state.jd_content = jd_text

        col1, col2 = st.columns(2)
        with col1:
            match_run = st.button("🔍 开始匹配", use_container_width=True)
        with col2:
            clear_jd = st.button("🧹 清空JD", use_container_width=True)

        if clear_jd:
            st.session_state.jd_content = ""
            if 'jd_match_result' in st.session_state:
                del st.session_state.jd_match_result

        if match_run:
            if not st.session_state.resume_content:
                st.warning("❗请先上传/填写简历")
            elif not st.session_state.jd_content:
                st.warning("❗请粘贴岗位JD")
            else:
                with st.spinner("📊 AI正在分析简历与JD匹配度..."):
                    match_result = tool_jd_match(
                        resume_text=st.session_state.resume_content,
                        jd_text=st.session_state.jd_content,
                        ai_client=st.session_state.ai_client
                    )
                    st.session_state.jd_match_result = match_result

        if st.session_state.get('jd_match_result'):
            st.divider()
            st.markdown("### 📊 匹配分析结果")
            st.markdown(st.session_state.jd_match_result)

    with st.sidebar.expander("🎤 模拟面试题生成", expanded=False):
        st.caption("简历+JD生成专属面试题")
        col1, col2 = st.columns(2)
        with col1:
            generate_btn = st.button("🚀 生成面试题", use_container_width=True)
        with col2:
            clear_qa = st.button("🧹 清空题目", use_container_width=True)

        if clear_qa:
            if 'interview_qa' in st.session_state:
                del st.session_state.interview_qa

        if generate_btn:
            if not st.session_state.get('resume_content'):
                st.warning("请先上传简历")
            elif not st.session_state.get('jd_content'):
                st.warning("请先填写JD")
            else:
                with st.spinner("🧠 生成面试题中..."):
                    qa_result = tool_interview_generate(st.session_state.resume_content, st.session_state.jd_content,
                                                        st.session_state.ai_client)
                    st.session_state.interview_qa = qa_result

        if st.session_state.get('interview_qa'):
            st.divider()
            st.markdown("### 🎯 专属面试题")
            st.markdown(st.session_state.interview_qa)

    if st.button("新建会话", width="stretch", icon="✏️"):
        st.session_state.messages = []
        st.session_state.current_session = generate_session_name()
        save_session()

    if st.button("清空当前聊天", width="stretch", icon="🧹"):
        st.session_state.messages = []
        save_session()

    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(session, width="stretch", icon="📄", key=f"load_{session}",
                         type="primary" if session == st.session_state.current_session else "secondary"):
                load_session(session)
        with col2:
            if st.button("", width="stretch", icon="❌️", key=f"delete_{session}"):
                delete_session(session)

    st.divider()
    st.subheader("知识库管理")
    uploaded_files = st.file_uploader("上传文档到知识库", accept_multiple_files=True, type=["txt", "pdf", "docx", "md"])
    if uploaded_files:
        os.makedirs("knowledge", exist_ok=True)
        for file in uploaded_files:
            with open(f"knowledge/{file.name}", "wb") as f:
                f.write(file.getbuffer())
        st.success(f"✅ 已上传 {len(uploaded_files)} 个文件")
        with st.spinner("更新知识库..."):
            build_knowledge_base()
        st.success("✅ 知识库更新完成！")

    if os.path.exists("knowledge"):
        files = os.listdir("knowledge")
        st.caption(f"已上传：{len(files)} 个文件")

    st.divider()
    st.subheader("导出对话")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("导出 TXT", use_container_width=True):
            txt_content = f"会话：{st.session_state.current_session}\n\n"
            for msg in st.session_state.messages:
                role = "我" if msg["role"] == "user" else "AI"
                txt_content += f"{role}：{msg['content']}\n\n"
            st.download_button("下载 TXT", txt_content, f"{st.session_state.current_session}.txt", use_container_width=True)

    with col2:
        if st.button("导出 PDF", use_container_width=True):
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt=f"会话：{st.session_state.current_session}", ln=True, align='C')
                pdf.ln(10)
                for msg in st.session_state.messages:
                    role = "用户" if msg["role"] == "user" else "AI"
                    pdf.multi_cell(0, 10, txt=f"{role}：{msg['content']}")
                    pdf.ln(2)
                pdf_bytes = pdf.output(dest='S').encode('latin-1')
                st.download_button("下载 PDF", pdf_bytes, f"{st.session_state.current_session}.pdf", use_container_width=True)
            except:
                st.error("需要安装：pip install fpdf")

# 🔥 聊天逻辑（已优化Agent）
if prompt:
    # 1. 直接显示用户消息并保存
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. 处理逻辑
    resume_txt = st.session_state.get("resume_content", "")
    jd_txt = st.session_state.get("jd_content", "")
    agent = st.session_state.job_agent

    with st.spinner("🤖 处理中..."):
        intent = agent.think_intent(prompt, resume_txt, jd_txt)
        ok, tip = agent.check_params(intent, resume_txt, jd_txt)

    full_response = ""
    if not ok:
        full_response = tip
    elif intent == "简历解析":
        full_response = agent.tool_map["简历解析"](resume_txt, st.session_state.ai_client)
    elif intent == "JD匹配":
        full_response = agent.tool_map["JD匹配"](resume_txt, jd_txt, st.session_state.ai_client)
    elif intent == "生成面试题":
        full_response = agent.tool_map["生成面试题"](resume_txt, jd_txt, st.session_state.ai_client)
    else:
        docs = search_knowledge(prompt)
        final_prompt = f"用户问题：{prompt}\n参考资料：{chr(10).join([f'资料：{d.page_content}' for d in docs])}" if docs else prompt
        messages = [
            {"role": "system", "content": system_prompt},
            *st.session_state.messages[:-1],
            {"role": "user", "content": final_prompt}
        ]

        # 流式输出统一用st.chat_message包裹，避免DOM冲突
        with st.chat_message("assistant"):
            placeholder = st.empty()
            for chunk in st.session_state.ai_client.get_stream_response(messages):
                full_response += chunk
                placeholder.markdown(full_response)

    # 3. 非流式工具结果也统一用st.chat_message输出
    if intent != "直接回答":
        with st.chat_message("assistant"):
            st.markdown(full_response)

    # 4. 统一保存会话
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    save_session()