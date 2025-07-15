"""
EORA 런처 스크립트 (경로 문제 완전 해결 + 문법 오류 수정됨)
- PYTHONPATH를 자동 설정하고
- eora_live_chat_refined.py를 안정적으로 실행
"""

import os
import subprocess
import sys

# 기준 경로 설정
base_dir = os.path.abspath(os.path.dirname(__file__))
src_dir = base_dir
eora_script = os.path.join(src_dir, "eora_memory", "eora_live_chat_refined.py")

# PYTHONPATH 설정
env = os.environ.copy()
env["PYTHONPATH"] = src_dir

# 실행 명령
print("🚀 EORA 실행 중...")
print(f"📂 PYTHONPATH: {src_dir}")
print(f"▶️ 실행 파일: {eora_script}\n")

subprocess.run([sys.executable, eora_script], env=env)
