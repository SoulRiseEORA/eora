#!/usr/bin/env python3
"""
Railway 배포용 간단한 서버
Nixpacks 문제를 피하기 위한 최소한의 설정
"""

import os
import sys
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """메인 함수"""
    print("🚀 EORA AI Railway 배포 서버 시작")
    print("=" * 50)
    
    # 환경변수 확인
    print("🔍 환경변수 확인:")
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("✅ OPENAI_API_KEY: 설정됨")
    else:
        print("❌ OPENAI_API_KEY: 설정되지 않음")
    
    mongo_url = os.getenv("MONGO_PUBLIC_URL")
    if mongo_url:
        print("✅ MONGO_PUBLIC_URL: 설정됨")
    else:
        print("❌ MONGO_PUBLIC_URL: 설정되지 않음")
    
    # final_server 모듈 import 및 실행
    try:
        import final_server
        print("✅ final_server 모듈 로드 성공")
        
        # FastAPI 앱 실행
        import uvicorn
        port = int(os.getenv("PORT", "8080"))
        print(f"📍 서버 포트: {port}")
        
        uvicorn.run(
            final_server.app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ final_server 모듈 로드 실패: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 서버 실행 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 