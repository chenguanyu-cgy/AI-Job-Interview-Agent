class JobAgent:
    def __init__(self, ai_client):
        self.ai_client = ai_client
        self.tool_map = {}

    def register_tool(self, tool_name, func):
        self.tool_map[tool_name] = func

    def think_intent(self, user_msg, resume_content, jd_content):
        # 优化点1：带思考链的意图判断（企业标准）
        prompt = f"""
你是求职AI助手，先思考再输出。
第一步：判断用户想做什么
第二步：检查有没有简历/JD
第三步：选择最合适的工具

可用工具：
简历解析：分析简历、总结简历
JD匹配：对比简历和岗位、算匹配度
生成面试题：根据简历+JD出面试题
直接回答：聊天、问候、无关问题

用户消息：{user_msg}
是否有简历：{"有" if resume_content.strip() else "无"}
是否有JD：{"有" if jd_content.strip() else "无"}

请只输出一个：简历解析 / JD匹配 / 生成面试题 / 直接回答
"""
        messages = [{"role": "user", "content": prompt}]
        try:
            return self.ai_client.get_response(messages).strip()
        except Exception as e:
            print("意图判断失败：", e)
            return "直接回答"

    # 优化点2：加参数检查，自动提示
    def check_params(self, intent, resume, jd):
        if intent == "简历解析" and not resume.strip():
            return False, "请先上传或填写简历～"
        if intent in ["JD匹配", "生成面试题"]:
            if not resume.strip():
                return False, "请先上传简历～"
            if not jd.strip():
                return False, "请先填写JD～"
        return True, ""