#!/usr/bin/env python3
"""
EORA Railway 메인 실행 파일
Railway가 자동으로 감지하여 실행
"""
import os
import sys
import uvicorn
from pathlib import Path

def main():
    print("🚀 EORA Railway 메인 서버 시작")
    
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
    
    try:
        # FastAPI 앱 import
        from src.app import app
        print("✅ FastAPI 앱 로드 성공")
        
        # uvicorn 서버 시작
        print("🌐 uvicorn 서버 시작 중...")
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            use_colors=False
        )
        
    except ImportError as e:
        print(f"❌ FastAPI 앱 import 실패: {e}")
        print("🔄 대안 방법 시도...")
        
        # 대안: 직접 모듈 import
        try:
            import app as app_module
            app = app_module.app
            print("✅ 대안 방법으로 앱 로드 성공")
            
            uvicorn.run(
                app,
                host=host,
                port=port,
                log_level="info",
                access_log=True,
                use_colors=False
            )
        except Exception as e2:
            print(f"❌ 대안 방법도 실패: {e2}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()