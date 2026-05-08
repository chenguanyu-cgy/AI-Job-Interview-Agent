def tool_resume_analyze(resume_text, ai_client):
    prompt = f"""你是专业求职顾问，请详细分析这份简历：
1. 个人核心优势
2. 技术与项目亮点
3. 适合岗位
4. 优化建议

简历：
{resume_text}
"""
    messages = [{"role": "user", "content": prompt}]
    return ai_client.get_response(messages)

def tool_jd_match(resume_text, jd_text, ai_client):
    prompt = f"""你是简历JD匹配专家，请输出：
1. 匹配度（0-100）
2. 优势
3. 差距短板
4. 优化建议
5. 面试重点

简历：
{resume_text}

JD：
{jd_text}
"""
    messages = [{"role": "user", "content": prompt}]
    return ai_client.get_response(messages)

def tool_interview_generate(resume_text, jd_text, ai_client):
    prompt = f"""根据简历与JD生成面试题，包含答案与思路：
1. 3道技术题（带答案）
2. 2道项目深挖题
3. 2道行为面试题
4. 1道反问面试官建议

简历：
{resume_text}

JD：
{jd_text}
"""
    messages = [{"role": "user", "content": prompt}]
    return ai_client.get_response(messages)