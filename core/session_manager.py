import os
from config import Config
from utils.logger import logger
from pathlib import Path
import json
from datetime import datetime

class SessionManager:
    def __init__(self):
        self.cache_path = Path("config_cache.json")
        self.config=self.load_config_path()
        if not os.path.exists(Config.SESSION_FOLDER):
            os.mkdir(Config.SESSION_FOLDER)
    #加载配置文件路径
    def load_config_path(self):
        #文件配置
        default_config = {
            # 核心对话配置
            "system_prompt": "你是我的专属AI伴侣，说话温柔简洁，像朋友一样聊天。",
            "max_history": 15,  # 最大上下文轮数，15比较稳，兼顾记忆和token
            "temperature": 0.7,  # 温度，0.7适合日常聊天，不会太死板也不会太放飞
            "top_p": 0.9,  # 核采样，配合温度用，让回复更自然

            # 会话管理配置
            "default_session_name": "default_session",

            # 高级/调试配置（隐藏给用户，自己后台用）
            "debug_mode": False,
            "log_level": "INFO",
            "response_timeout": 30  # 请求超时时间，单位秒
        }
        if self.cache_path.exists():
            with open(self.cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return default_config
    #获取会话文件路径
    def get_session_path(self, session_id):
        return os.path.join(Config.SESSION_FOLDER, f"{session_id}.json")
    #加载会话
    def load_session(self, session_id):
        try:
            # 拼接路径
            session_path=self.get_session_path(session_id)
            if not os.path.exists(session_path):
                return []
            with open(session_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载会话失败: {e}")
            return []
    #保存会话
    def save_session(self, session_id, session):
        try:
            session_path=self.get_session_path(session_id)
            with open(session_path, "w", encoding="utf-8") as f:
                json.dump(session, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存会话失败: {e}")
    #追加新消息
    def append_message(self, session_id: str, role: str, content: str)-> list:
        #加载当前会话的历史记录
        history=self.load_session(session_id)
        #在历史消息里面追加新消息
        history.append({"role": role, "content": content})
        #将更新后的历史保存到文件，实现持久化
        self.save_session(session_id, history)
        #定义最大对话轮数，一轮对话是一次提问+一次回答
        max_history=15
        #如果超过最大对话轮数，则只保留最新的对话轮数
        if len(history) > max_history*2:
            history = history[-max_history*2:]
        return  history
    #列出所有会话
    def list_all_sessions(self):
        sessions=[]
        #遍历Session文件夹下的所有文件
        for filename in os.listdir(Config.SESSION_FOLDER):
            #判断是否是JSON文件
            if filename.endswith(".json"):
                #获取会话ID
                session_id=filename[:-5]
                file_path=os.path.join(Config.SESSION_FOLDER, filename)
                #获取修改时间
                mtime=os.path.getmtime(file_path)
                sessions.append({
                    "session_id": session_id,
                    "mtime": datetime.fromtimestamp(mtime)
                })
                sessions.sort(key=lambda x: x["mtime"], reverse=True)
        return  sessions
    #创建新会话
    def create_new_session(self, custom_id: str = None):
        if custom_id:
            session_path=self.get_session_path(custom_id)
            if os.path.exists(session_path):
                logger.info(f"会话已存在: {custom_id}")
                return custom_id
            new_session_id=custom_id
            empty_session = []
            self.save_session(new_session_id, empty_session)
            logger.info(f"创建新会话: {new_session_id}")
            return new_session_id
        else:
            new_session_id=f"session_{datetime.now().strftime("%Y%m%d%H%M%S")}"
            empty_session=[]
            self.save_session(new_session_id, empty_session)
            logger.info(f"创建新会话: {new_session_id}")
            return new_session_id

    def delete_session(self, session_id):
        session_path=self.get_session_path(session_id)
        if os.path.exists(session_path):
            os.remove(session_path)
            logger.info(f"删除会话: {session_id}")
            return True
        else:
            return False

    def switch_session(self, session_id):
        session_path=self.get_session_path(session_id)
        if not os.path.exists(session_path):
            raise Exception("会话不存在")
        session_data=self.load_session(session_id)
        logger.info(f"切换会话: {session_id}")
        return session_data




