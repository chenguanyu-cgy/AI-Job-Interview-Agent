import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

import streamlit as st

st.set_page_config(
    page_title="AI智能求职助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

import os
from datetime import datetime
import json

try:
    from fpdf import FPDF
except Exception:
    pass

from core.ai_client import AIClient
from utils.rag_utils import build_knowledge_base, search_knowledge
from utils.agent_tools import tool_resume_analyze, tool_jd_match, tool_interview_generate
from utils.agent_core import JobAgent


# 初始化配置
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def save_session():
    if st.session_state.current_session:
        session_data = {
            "nick_name": "AI助手",
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }
        os.makedirs("sessions", exist_ok=True)
        with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)


def load_sessions():
    session_list = []
    if os.path.exists("sessions"):
        for f in os.listdir("sessions"):
            if f.endswith(".json"):
                session_list.append(f[:-5])
    return sorted(session_list, reverse=True)


def load_session(session_name):
    try:
        with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        st.session_state.messages = data["messages"]
        st.session_state.current_session = session_name
    except:
        st.error("加载失败")


def delete_session(session_name):
    try:
        os.remove(f"sessions/{session_name}.json")
        if session_name == st.session_state.current_session:
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
    except:
        st.error("删除失败")


# 业务初始化
if "ai_client" not in st.session_state:
    st.session_state.ai_client = AIClient()
    agent = JobAgent(st.session_state.ai_client)
    agent.register_tool("简历解析", tool_resume_analyze)
    agent.register_tool("JD匹配", tool_jd_match)
    agent.register_tool("生成面试题", tool_interview_generate)
    st.session_state.job_agent = agent
    st.session_state.resume_content = ""
    st.session_state.jd_content = ""

# 会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()

# 主界面
st.title("AI智能求职助手")
prompt = st.chat_input("请输入您要问的问题")
st.text(f"会话：{st.session_state.current_session}")

# 渲染消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.subheader("AI控制面板")
    st.subheader("求职Agent工具")

    if st.button("清空内容", use_container_width=True):
        st.session_state.resume_content = ""

    uploaded_file = st.file_uploader("上传简历PDF", type=["pdf", "txt"])
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            from pypdf import PdfReader

            st.session_state.resume_content = "\n".join(
                [page.extract_text() for page in PdfReader(uploaded_file).pages])
            st.success("✅ PDF解析完成")
        else:
            st.session_state.resume_content = uploaded_file.read().decode("utf-8")
            st.success("✅ TXT读取完成")

    # 简历解析
    with st.expander("简历智能解析", expanded=True):
        st.session_state.resume_content = st.text_area("简历文本", value=st.session_state.resume_content, height=150)
        if st.button("一键解析简历", use_container_width=True, type="primary"):
            with st.spinner("AI解析中..."):
                result = tool_resume_analyze(st.session_state.resume_content, st.session_state.ai_client)
                st.markdown(result)

    # JD匹配
    with st.expander("JD简历智能匹配", expanded=False):
        st.caption("粘贴岗位JD → 自动分析匹配度")
        st.session_state.jd_content = st.text_area("岗位JD", value=st.session_state.jd_content, height=120)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("开始匹配", use_container_width=True):
                if st.session_state.resume_content and st.session_state.jd_content:
                    with st.spinner("匹配中..."):
                        result = tool_jd_match(st.session_state.resume_content, st.session_state.jd_content,
                                               st.session_state.ai_client)
                        st.markdown(result)
        with col2:
            if st.button("清空JD", use_container_width=True):
                st.session_state.jd_content = ""

    # 面试题生成
    with st.expander("模拟面试题生成", expanded=False):
        if st.button("生成面试题", use_container_width=True):
            if st.session_state.resume_content and st.session_state.jd_content:
                with st.spinner("生成中..."):
                    result = tool_interview_generate(st.session_state.resume_content, st.session_state.jd_content,
                                                     st.session_state.ai_client)
                    st.markdown(result)

    # 会话管理
    st.divider()
    if st.button("新建会话", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_session = generate_session_name()
    if st.button("清空当前聊天", use_container_width=True):
        st.session_state.messages = []

    st.text("会话历史")
    for s in load_sessions():
        c1, c2 = st.columns([4, 1])
        with c1:
            if st.button(s, use_container_width=True, key=f"load_{s}"):
                load_session(s)
        with c2:
            if st.button("❌", use_container_width=True, key=f"del_{s}"):
                delete_session(s)

    st.divider()
    st.subheader("导出对话")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("导出 TXT", use_container_width=True):
            txt = f"会话：{st.session_state.current_session}\n\n"
            for msg in st.session_state.messages:
                txt += f"{msg['role']}：{msg['content']}\n\n"
            st.download_button("下载", txt, f"{st.session_state.current_session}.txt", use_container_width=True)
    with col2:
        if st.button("导出 PDF", use_container_width=True):
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 12)
                pdf.cell(200, 10, txt=st.session_state.current_session, ln=True)
                for msg in st.session_state.messages:
                    pdf.multi_cell(0, 10, f"{msg['role']}：{msg['content']}")
                st.download_button("下载", pdf.output(dest="S").encode("latin-1"),
                                   f"{st.session_state.current_session}.pdf", use_container_width=True)
            except:
                st.error("请安装 fpdf")

# ===================== 核心修改：删除流式输出，改为一次性输出 =====================
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("🤖 处理中..."):
        intent = st.session_state.job_agent.think_intent(prompt, st.session_state.resume_content,
                                                         st.session_state.jd_content)
        ok, tip = st.session_state.job_agent.check_params(intent, st.session_state.resume_content,
                                                          st.session_state.jd_content)
        full_response = ""

        if not ok:
            full_response = tip
        elif intent == "简历解析":
            full_response = tool_resume_analyze(st.session_state.resume_content, st.session_state.ai_client)
        elif intent == "JD匹配":
            full_response = tool_jd_match(st.session_state.resume_content, st.session_state.jd_content,
                                          st.session_state.ai_client)
        elif intent == "生成面试题":
            full_response = tool_interview_generate(st.session_state.resume_content, st.session_state.jd_content,
                                                    st.session_state.ai_client)
        else:
            docs = search_knowledge(prompt)
            final_prompt = f"问题：{prompt}\n资料：{[d.page_content for d in docs]}" if docs else prompt
            messages = [{"role": "system", "content": "专业友好，不编造"}, *st.session_state.messages[:-1],
                        {"role": "user", "content": final_prompt}]

            # 【已删除流式】一次性获取响应
            full_response = st.session_state.ai_client.get_response(messages)

    # 统一渲染回复
    with st.chat_message("assistant"):
        st.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    save_session()