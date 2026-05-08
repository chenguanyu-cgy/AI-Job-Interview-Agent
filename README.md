# AI-求职-面试-代理
AI求职智能助手 | 简历解析 | JD匹配 | 面试题生成 | RAG知识库 | FunctionCall工具调用

## 项目介绍
基于大模型开发的AI求职助手，通过RAG增强问答+FunctionCall实现求职全流程辅助，支持多轮对话、会话管理、容器化部署。

## 核心功能
1. 简历智能解析：分析优势、亮点、优化建议
2. JD简历匹配：计算匹配度、分析优劣势、面试重点
3. 专属面试题生成：技术题+项目题+行为面
4. RAG知识库：支持PDF/TXT/DOCX上传检索
5. 多轮会话管理：上下文记忆、会话持久化
6. 流式输出：大模型回复实时展示

## 技术栈
- 前端：Streamlit
- 大模型：DeepSeek API
- 向量Embedding：阿里云百炼
- 向量库：FAISS
- 框架：LangChain
- 核心能力：API接口、RAG、FunctionCall、MCP上下文管理
- 部署：Docker容器化
- 环境：Python 3.10+

## 项目结构
├── agent_core.py        # Agent 智能体核心逻辑
├── agent_tools.py       # 自定义工具函数（简历解析、JD匹配）
├── ai_client.py         # 大模型 API 调用客户端
├── app.py               # 后端服务入口
├── config.py            # 项目配置文件
├── logger.py            # 日志工具
├── rag_utils.py         # RAG 知识库核心工具（切片、向量化、检索）
├── session_manager.py   # MCP 上下文会话管理
├── streamlit_app.py     # 前端可视化界面（Streamlit）
├── requirements.txt     # 项目依赖包
├── .env.example         # 环境变量配置模板
└── .gitignore           # Git 忽略文件

## 快速启动
1. 安装依赖
```bash
pip install -r requirements.txt
