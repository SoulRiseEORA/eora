#!/usr/bin/env python3
"""
🚀 Railway 안전 서버 - 루트 레벨
Railway가 찾는 정확한 경로에 배치
"""
import os
import sys
import uvicorn
from pathlib import Path

def main():
    print("🚀 Railway 안전 서버 시작 - 루트 레벨")
    
    # src 디렉토리를 Python 경로에 추가
    src_path = Path(__file__).parent / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
        print(f"✅ Python 경로에 src 추가: {src_path}")
    
    # 환경변수 확인
    port = int(os.environ.get("PORT", "8080"))
    host = "0.0.0.0"
    
    print(f"📍 호스트: {host}")
    print(f"🔌 포트: {port}")
    print(f"📁 현재 디렉토리: {Path.cwd()}")
    
    # app.py 파일 찾기
    possible_paths = [
        Path("src/app.py"),
        Path("app.py"),
        Path(__file__).parent / "src" / "app.py"
    ]
    
    app_file = None
    for path in possible_paths:
        if path.exists():
            app_file = path
            print(f"✅ app.py 파일 발견: {app_file}")
            break
    
    if not app_file:
        print("❌ app.py 파일을 찾을 수 없습니다!")
        print(f"❌ 확인한 경로들: {[str(p) for p in possible_paths]}")
        sys.exit(1)
    
    try:
        # FastAPI 앱 import - src에서
        print("🔄 FastAPI 앱 로드 시도...")
        
        # src 디렉토리 작업
        os.chdir(src_path)
        print(f"📁 작업 디렉토리 변경: {os.getcwd()}")
        
        from app import app
        print("✅ FastAPI 앱 로드 성공")
        
        # uvicorn 서버 시작
        print("🌐 uvicorn 서버 시작 중...")
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            use_colors=False,
            server_header=False,
            date_header=False
        )
        
    except ImportError as e:
        print(f"❌ FastAPI 앱 import 실패: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()