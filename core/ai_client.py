from config import Config
from utils.logger import logger
from openai import OpenAI
import time
from functools import wraps

def retry(times=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"请求失败，第{i+1}次重试: {e}")
                    time.sleep(delay)
            raise Exception(f"重试{times}次后仍失败")
        return wrapper
    return decorator

class AIClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=Config.API_KEY,
            base_url=Config.BASE_URL,
        )

    @retry()
    def get_response(self, messages):
        # ↓↓↓ 这里 messages 必须是列表格式，不能是字符串！
        try:
            response = self.client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=messages
            )
            logger.info("AI调用成功")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI调用失败: {e}")
            return f"AI 暂时无法回答，请稍后再试"

    def get_stream_response(self, messages):
        stream = self.client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=messages,
            stream=True  # 开启流式
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content