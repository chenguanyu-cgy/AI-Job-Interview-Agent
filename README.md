# 📄 AI 求职智能助手（RAG + FunctionCall + Streamlit）

> 基于大模型的全流程求职辅助工具，支持简历解析、JD 岗位匹配、AI 面试模拟三大核心功能。
> 个人独立项目 | 已部署公网可在线体验

---

## ✨ 项目介绍
本项目是面向求职者的 AI 求职辅助系统，通过大模型 + RAG 技术实现：
• 简历智能解析（PDF 自动读取、结构化提取）
• JD 简历匹配度分析与优化建议
• 岗位针对性面试模拟与 AI 点评
• 多轮对话式求职助手

用户无需部署，打开公网链接即可直接使用。

---

## 🚀 公网在线演示
https://ai-job-interview-agent-tjpv53qjjfv7auuzadggsn.streamlit.app

---

## 🛠️ 技术栈
• 前端界面：Streamlit
• 大模型：DeepSeek API
• 文档解析：PyPDF2
• 向量检索：FAISS + RAG
• 工具封装：FunctionCall 智能调用
• 开发语言：Python 3.10+

---

## 📁 真实项目结构（与 GitHub 完全一致）
AI-Job-Interview-Agent/
├── core/                     # 核心业务模块
│   └── ai_client.py          # 大模型客户端封装
├── utils/                    # 工具函数模块
│   ├── logger.py             # 日志工具
│   ├── rag_utils.py          # RAG 知识库构建与检索
│   ├── agent_tools.py        # 求职工具（简历解析/JD匹配/面试）
│   └── agent_core.py         # 智能 Agent 核心逻辑
├── streamlit_app.py          # 项目主入口（Streamlit 应用）
├── config.py                 # 全局配置文件
├── requirements.txt          # 项目依赖包
├── .env.example              # 环境变量模板
└── README.md                 # 项目说明文档

---

## 🎯 核心功能
### 1. 简历智能解析
支持上传 PDF 简历，自动提取个人信息、技能、项目、工作经历。

### 2. JD 岗位匹配
输入 JD → 自动分析匹配度 → 生成简历优化建议。

### 3. AI 面试模拟
根据岗位自动生成面试题，支持多轮对话，AI 实时点评回答。

### 4. 求职智能助手
支持自由提问：简历优化、面试技巧、职业规划等。

---

## 🚀 本地运行方法
1. 克隆项目
git clone https://github.com/chenguanyu-cgy/AI-Job-Interview-Agent.git

2. 安装依赖
pip install -r requirements.txt

3. 配置 .env 文件（参考 .env.example）

4. 启动
streamlit run streamlit_app.py

---

## 📌 项目亮点
• 前后端一体，Streamlit 快速构建可视化界面
• RAG 检索增强，提高回答准确性
• FunctionCall 实现工具自动调用
• 公网部署，可直接展示给面试官
• 工程化结构清晰，日志、配置、模块化完整

---

## 📄 开源协议
MIT License

如果对你有帮助，欢迎 Star ⭐