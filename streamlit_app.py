# streamlit_app.py
import streamlit as st
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入项目核心模块
from utils.logger import logger
from core.ai_client import AIClient
from core.session_manager import SessionManager
from utils.rag_utils import build_knowledge_base, search_knowledge
from config import Config

# 初始化Streamlit页面配置
st.set_page_config(
    page_title="AI智能伴侣 (RAG增强版)",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 会话状态初始化
if "chatbot" not in st.session_state:
    # 初始化ChatBot核心组件
    st.session_state.session_manager = SessionManager()
    st.session_state.ai_client = AIClient()
    st.session_state.current_session_id = None
    st.session_state.knowledge_built = False

    # 构建知识库（仅首次运行）
    with st.spinner("正在初始化知识库..."):
        build_knowledge_base()
        st.session_state.knowledge_built = True

    # 初始化默认会话
    all_sessions = st.session_state.session_manager.list_all_sessions()
    if all_sessions:
        st.session_state.current_session_id = all_sessions[0]["session_id"]
    else:
        st.session_state.current_session_id = st.session_state.session_manager.create_new_session("默认会话")

# 侧边栏 - 会话管理
with st.sidebar:
    st.title("🤖 会话管理")

    # 显示当前会话
    st.info(f"当前会话：{st.session_state.current_session_id}")

    # 列出所有会话
    st.subheader("所有会话")
    all_sessions = st.session_state.session_manager.list_all_sessions()
    for session in all_sessions:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(session["session_id"], key=f"switch_{session['session_id']}"):
                st.session_state.current_session_id = session["session_id"]
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{session['session_id']}"):
                if session["session_id"] != st.session_state.current_session_id:
                    st.session_state.session_manager.delete_session(session["session_id"])
                    st.rerun()
                else:
                    st.error("无法删除当前会话！")

    # 新建会话
    new_session_name = st.text_input("新会话名称")
    if st.button("创建新会话"):
        if new_session_name.strip():
            new_id = st.session_state.session_manager.create_new_session(new_session_name.strip())
            st.session_state.current_session_id = new_id
            st.rerun()
        else:
            st.warning("请输入会话名称！")

# 主页面 - 聊天界面
st.title("AI智能伴侣 (RAG增强版)")


# 加载并显示聊天历史
def load_chat_history():
    """加载并过滤聊天历史（移除system消息和参考资料）"""
    history = st.session_state.session_manager.load_session(st.session_state.current_session_id)
    filtered_history = []
    for msg in history:
        if msg["role"] == "system":
            continue
        # 清理用户消息中的参考资料部分，只显示原始问题
        if msg["role"] == "user" and "\n\n参考资料：" in msg["content"]:
            original_question = msg["content"].split("\n\n参考资料：")[0]
            filtered_history.append({"role": msg["role"], "content": original_question})
        else:
            filtered_history.append(msg)
    return filtered_history


# 显示聊天历史
chat_history = load_chat_history()
for msg in chat_history:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])


# RAG提示词构建函数
def build_rag_prompt(user_input: str) -> str:
    """构建包含RAG检索结果的提示词"""
    final_question = user_input
    docs = search_knowledge(user_input)
    if docs:
        context = "\n---\n".join([
            f"【资料】{doc.page_content}"
            for doc in docs
        ])
        final_question = f"{user_input}\n\n参考资料：{context}"
    return final_question


# 聊天输入框
user_input = st.chat_input("请输入你的问题...")
if user_input:
    # 构建RAG增强的提示词
    final_prompt = build_rag_prompt(user_input)

    # 保存用户消息
    st.session_state.session_manager.append_message(
        st.session_state.current_session_id,
        "user",
        final_prompt
    )

    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(user_input)

    # 调用AI并显示回复
    with st.chat_message("assistant"):
        with st.spinner("AI正在思考中..."):
            # 获取完整会话历史
            messages = st.session_state.session_manager.load_session(st.session_state.current_session_id)
            # 调用AI接口
            response = st.session_state.ai_client.get_response(messages)
            # 保存回复
            st.session_state.session_manager.append_message(
                st.session_state.current_session_id,
                "assistant",
                response
            )
            # 显示回复
            st.markdown(response)

    # 重新加载页面以更新聊天历史
    st.rerun()

# 底部信息
with st.expander("ℹ️ 关于本系统"):
    st.markdown("""
    ### AI智能伴侣 (RAG增强版)
    - 基于LangChain + FAISS构建的本地RAG知识库系统
    - 支持多会话管理，会话自动持久化存储
    - 内置知识库检索功能，可回答项目相关问题
    - 使用DeepSeek大模型提供对话能力
    """)