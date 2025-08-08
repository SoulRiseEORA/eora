"""
EORA 실행 환경 자동 설정기 (run_env_initializer.py)
- src 하위 모든 패키지를 sys.path에 추가
- __init__.py 누락된 폴더 감지
- 모듈 import 오류 방지
"""

import sys
import os

def add_all_subfolders_to_sys_path(base_path):
    print(f"📁 기준 루트 경로: {base_path}")
    missing_init = []

    for root, dirs, files in os.walk(base_path):
        if "__init__.py" not in files:
            rel = os.path.relpath(root, base_path)
            if rel != ".":
                missing_init.append(rel)
        if root not in sys.path:
            sys.path.insert(0, root)

    print("✅ 모든 하위 폴더 sys.path 등록 완료")

    if missing_init:
        print("⚠️ __init__.py 누락 폴더:")
        for p in missing_init:
            print(f"  - {p}")
    else:
        print("✅ 모든 폴더에 __init__.py가 있습니다.")

if __name__ == "__main__":
    current_file_path = os.path.abspath(__file__)
    src_root = os.path.abspath(os.path.join(current_file_path, ".."))
    add_all_subfolders_to_sys_path(src_root)
