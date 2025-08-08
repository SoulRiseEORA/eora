
# ai_memory_writer.py

import os
from datetime import datetime

def write_ai_memory(role_name: str, result: str, base_path="ai_brain"):
    """
    AI의 작업 결과를 역할별 지침 파일에 자동 누적 저장합니다.
    """
    role_file = os.path.join(base_path, f"{role_name}.txt")
    os.makedirs(base_path, exist_ok=True)
    with open(role_file, 'a', encoding='utf-8') as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"\n\n[기록 시각: {now}]\n{result.strip()}\n")
