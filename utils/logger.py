import os
import logging
from config import Config

# 确保日志文件夹存在
if not os.path.exists(Config.LOGS_FOLDER):
    os.makedirs(Config.LOGS_FOLDER)

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(Config.LOGS_FOLDER, "logs.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# 定义logger对象
logger = logging.getLogger(__name__)