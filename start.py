#!/usr/bin/env python3
"""
Railway 시작 스크립트 - 확실한 서버 실행
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 EORA Railway 시작 스크립트")
    
    # 현재 디렉토리 확인
    current_dir = Path.cwd()
    print(f"📁 현재 디렉토리: {current_dir}")
    
    # app.py 파일 찾기
    possible_paths = [
        "app.py",
        "src/app.py",
        current_dir / "app.py",
        current_dir / "src" / "app.py"
    ]
    
    app_file = None
    for path in possible_paths:
        if Path(path).exists():
            app_file = Path(path)
            print(f"✅ app.py 파일 발견: {app_file}")
            break
    
    if not app_file:
        print("❌ app.py 파일을 찾을 수 없습니다!")
        sys.exit(1)
    
    # 환경변수 확인
    port = os.environ.get("PORT", "8080")
    print(f"🔌 포트: {port}")
    
    # uvicorn 실행
    if "src" in str(app_file):
        cmd = ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", port]
    else:
        cmd = ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", port]
    
    print(f"🌐 실행 명령어: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"❌ 서버 실행 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()