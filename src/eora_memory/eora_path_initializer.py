"""
EORA 경로 자동 초기화 모듈
- src 디렉토리를 PYTHONPATH에 자동 추가
- eora_memory 내부에서 최상위 import가 깨지지 않도록 유지
"""

import sys
import os

def ensure_src_path():
    current = os.path.abspath(__file__)
    eora_path = os.path.dirname(current)
    src_path = os.path.abspath(os.path.join(eora_path, ".."))

    if src_path not in sys.path:
        sys.path.insert(0, src_path)
        print(f"✅ PYTHONPATH에 src 경로 추가됨: {src_path}")
    else:
        print("ℹ️ src 경로 이미 포함됨")

# 자동 실행
ensure_src_path()
