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
    
    # main 모듈 import 및 실행
    try:
        import main
        print("✅ main 모듈 로드 성공")
        
        # FastAPI 앱 실행
        import uvicorn
        
        # 포트 설정 (여러 방법 시도)
        port = 8080  # 기본값
        
        # 환경변수에서 포트 가져오기
        port_env = os.getenv("PORT")
        if port_env:
            try:
                port = int(port_env)
                print(f"✅ 환경변수 PORT 사용: {port}")
            except (ValueError, TypeError):
                print(f"❌ 환경변수 PORT가 유효하지 않음: {port_env}, 기본값 사용: {port}")
        else:
            print(f"📍 기본 포트 사용: {port}")
        
        print(f"🚀 서버 시작 - 포트: {port}")
        print(f"🌐 접속 URL: http://0.0.0.0:{port}")
        
        uvicorn.run(
            main.app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ main 모듈 로드 실패: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 서버 실행 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 