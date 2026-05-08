import os
from config import Config
from loguru import logger

if not os.path.exists(Config.LOGS_FOLDER):
    os.makedirs(Config.LOGS_FOLDER)
    logger.add(
        os.path.join(Config.LOGS_FOLDER, "logs.log"),
        rotation="10 MB",
        encoding="utf-8",)