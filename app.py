from utils.logger import logger
from core.ai_client import AIClient
from core.session_manager import SessionManager
from utils.rag_utils import build_knowledge_base, search_knowledge
from config import Config


class ChatBot:
    def __init__(self):
        self.session = SessionManager()
        self.ai = AIClient()
        self.session_id = None

        # 启动时自动构建知识库
        logger.info("正在初始化知识库...")
        build_knowledge_base()
        logger.info("知识库初始化完成")

    def init_default_session(self):
        all_sessions = self.session.list_all_sessions()
        if all_sessions:
            self.session_id = all_sessions[0]["session_id"]
            logger.info(f"使用默认会话: {self.session_id}")
        else:
            try:
                self.session_id = self.session.create_new_session(self.session.config["default_session_name"])
                logger.info(f"创建默认会话: {self.session_id}")
            except Exception as e:
                logger.warning(f"创建会话失败: {e}，尝试获取现有会话")
                all_sessions = self.session.list_all_sessions()
                if all_sessions:
                    self.session_id = all_sessions[0]["session_id"]
                    logger.info(f"使用现有会话: {self.session_id}")
                else:
                    raise RuntimeError("无法创建或获取会话，请检查 session 目录权限")

        # 添加系统提示词（减少幻觉）
        history = self.session.load_session(self.session_id)
        if not any(msg["role"] == "system" for msg in history):
            self.session.append_message(
                self.session_id, "system", self.session.config["system_prompt"]
            )

    def list_all_sessions(self):
        """保留你原来的会话列表功能"""
        all_sessions = self.session.list_all_sessions()
        print("\n所有会话:")
        for i, session in enumerate(all_sessions, 1):
            mark = "← 当前会话" if self.session_id == session["session_id"] else ""
            print(f"{i}. {session['session_id']} {mark}")
        print()

    def handle_session_command(self, user_input: str) -> bool:
        """所有会话命令：list/new/del/switch"""
        cmd = user_input.strip().lower()
        if cmd == "list":
            self.list_all_sessions()
            return True

        elif cmd == "new":
            session_id = input("请输入新会话名称（留空自动生成）: ").strip()
            self.session_id = self.session.create_new_session(session_id if session_id else None)
            logger.info(f"创建并切换到新会话: {self.session_id}")
            print(f"已切换到会话: {self.session_id}")
            return True

        elif cmd.startswith("del "):
            parts = cmd.split(maxsplit=1)
            if len(parts) < 2:
                print("格式错误，正确格式: del <会话名>")
                return True
            target_id = parts[1]
            if target_id == self.session_id:
                print("无法删除当前会话，请先切换到其他会话")
                return True
            if self.session.delete_session(target_id):
                print(f"已删除会话: {target_id}")
            else:
                print("删除失败，会话不存在")
            return True

        elif cmd.startswith("switch "):
            parts = cmd.split(maxsplit=1)
            if len(parts) < 2:
                print("格式错误，正确格式: switch <会话名>")
                return True
            target_id = parts[1]
            if target_id == self.session_id:
                print("已经是当前会话了")
                return True
            try:
                self.session.switch_session(target_id)
                self.session_id = target_id
                logger.info(f"切换到会话: {self.session_id}")
                print(f"已切换到会话: {self.session_id}")
            except Exception as e:
                logger.error(f"切换会话失败: {e}")
                print("切换会话失败，请检查会话名称是否正确")
            return True

        return False

    def build_rag_prompt(self, user_input: str) -> str:
        # 永远、永远、永远优先把用户问题传出去！
        final_question = user_input

        # 只有找到资料，才加参考资料，绝不覆盖问题
        docs = search_knowledge(user_input)
        if docs:
            context = "\n---\n".join([
                f"【资料】{doc.page_content}"
                for doc in docs
            ])
            final_question = f"{user_input}\n\n参考资料：{context}"

        return final_question

    def start(self):
        logger.info("启动聊天机器人（RAG增强版）")
        print("=" * 60)
        print("🤖 AI 智能伴侣（LangChain RAG 版）| 命令：exit 退出 / list 查看会话 / new/del/switch 管理会话")
        print("=" * 60)

        self.init_default_session()

        while True:
            try:
                user_input = input("\n请输入信息: ").strip()
                if not user_input:
                    print("请输入有效的信息")
                    continue

                if user_input.lower() in ["exit", "quit"]:
                    print("已退出聊天，会话已自动保存")
                    break

                if self.handle_session_command(user_input):
                    continue

                # 关键：构建RAG提示词
                final_prompt = self.build_rag_prompt(user_input)
                # 添加用户消息
                self.session.append_message(self.session_id, "user", final_prompt)
                # 获取完整会话历史
                messages = self.session.load_session(self.session_id)
                # 调用AI
                print("正在思考...")
                response = self.ai.get_response(messages)
                # 保存回复
                self.session.append_message(self.session_id, "assistant", response)
                print(f"\nAI: {response}")

            except KeyboardInterrupt:
                print("\n收到退出信号，程序终止")
                break
            except Exception as e:
                logger.error(f"运行时错误: {e}")
                print(f"系统错误: {str(e)}，请查看日志获取详情")

if __name__ == "__main__":
    chatbot = ChatBot()
    chatbot.start()