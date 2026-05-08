from langchain_community.document_loaders import (
    TextLoader, PyPDFLoader, Docx2txtLoader, CSVLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
import requests
import os
from pathlib import Path
from typing import List
from utils.logger import logger
from config import Config

# ====================== 阿里云百炼 Embedding ======================
class AliEmbeddings(Embeddings):
    """阿里云百炼 Embedding（原生接口，稳定可用）"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "text-embedding-v3",
            "input": {
                "texts": texts
            },
            "parameters": {
                "text_type": "document"
            }
        }
        resp = requests.post(self.api_url, json=data, headers=headers, timeout=30)
        resp.raise_for_status()
        return [item["embedding"] for item in resp.json()["output"]["embeddings"]]

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

# ====================== 文档加载逻辑 ======================
def load_all_docs() -> List[Document]:
    docs = []
    path = Path(Config.KNOWLEDGE_DIR)
    path.mkdir(exist_ok=True, parents=True)
    loader_map = {
        ".txt": TextLoader,
        ".md": TextLoader,
        ".pdf": PyPDFLoader,
        ".docx": Docx2txtLoader,
        ".csv": CSVLoader
    }
    for file in os.listdir(path):
        file_path = path / file
        suffix = file_path.suffix.lower()
        if suffix not in loader_map:
            logger.warning(f"不支持的文件格式: {file}，跳过")
            continue
        try:
            loader = loader_map[suffix](str(file_path), encoding="utf-8")
            loaded_docs = loader.load()
            for doc in loaded_docs:
                doc.metadata["source_file"] = file
                doc.metadata["file_type"] = suffix
            docs.extend(loaded_docs)
            logger.info(f"成功解析文件: {file}，共{len(loaded_docs)}个片段")
        except Exception as e:
            logger.error(f"解析文件失败: {file}，错误: {str(e)}")
    return docs

# ====================== 文本分片 ======================
def split_docs(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.RAG_CONFIG["chunk_size"],
        chunk_overlap=Config.RAG_CONFIG["chunk_overlap"],
        separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""],
        length_function=len,
        add_start_index=True
    )
    splits = splitter.split_documents(docs)
    logger.info(f"文本分片完成，共生成{len(splits)}个片段")
    return splits

# ====================== 构建知识库 ======================
def build_knowledge_base() -> None:
    logger.info("=== 开始构建知识库 ===")
    docs = load_all_docs()
    if not docs:
        logger.warning("knowledge目录无文件，跳过构建")
        return
    splits = split_docs(docs)
    emb = AliEmbeddings(api_key=Config.ALY_API_KEY)
    db = FAISS.from_documents(splits, emb)
    db.save_local(str(Config.FAISS_DB_PATH))
    logger.info(f"知识库构建完成，向量库已持久化到: {Config.FAISS_DB_PATH}")

# ====================== 检索 ======================
def search_knowledge(query: str) -> List[Document]:
    index_path = Path(Config.FAISS_DB_PATH) / "index.faiss"
    if not index_path.exists():
        logger.warning("向量库不存在，请先运行build_knowledge_base()")
        return []
    emb = AliEmbeddings(api_key=Config.ALY_API_KEY)
    db = FAISS.load_local(
        str(Config.FAISS_DB_PATH),
        emb,
        allow_dangerous_deserialization=True
    )
    retriever = db.as_retriever(search_kwargs={"k": Config.RAG_CONFIG["top_k"]})
    return retriever.invoke(query)