
# aura_system/logger.py

import logging

logger = logging.getLogger("AURA")
logger.setLevel(logging.INFO)

# 콘솔 출력 핸들러 설정
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
console_handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(console_handler)
