import os
from dotenv import load_dotenv
#大模型基础配置
load_dotenv()
class Config:
    API_KEY = os.getenv("DEEPSEEK_API_KEY")
    BASE_URL = os.getenv("DEEPSEEK_BASE_URL")
    MODEL_NAME = os.getenv("DEEPSEEK_MODEL_NAME")
    SESSION_FOLDER = os.getenv("SESSION_FOLDER","sessions")
    LOGS_FOLDER = os.getenv("LOGS_FOLDER","logs")
    MAX_HISTORY = os.getenv("MAX_HISTORY","15")
    ALY_API_KEY = os.getenv("ALY_API_KEY")
    # ========== 新增：RAG 相关配置（完全不影响原有代码） ==========
    KNOWLEDGE_DIR = "knowledge"  # 知识库文档目录
    FAISS_DB_PATH = "faiss_db"  # 向量库存储目录
    RAG_CONFIG = {
        "chunk_size": 1000,  # 文本切块大小
        "chunk_overlap": 200,  # 切块重叠长度
        "top_k": 3,  # 检索返回的文档数量
    }
