#!/usr/bin/env python3
"""
Railway 배포용 가장 간단한 시작 스크립트
환경변수 처리를 완전히 안전하게 수행
"""

import os
import sys
import uvicorn

def main():
    """메인 함수"""
    print("🚀 EORA AI Railway 간단 시작 서버")
    
    # 포트 설정 - 가장 간단한 방법
    port = 8080  # 기본값
    
    # 환경변수에서 포트 가져오기
    port_env = os.environ.get('PORT')
    if port_env:
        try:
            port = int(port_env)
            print(f"✅ 환경변수 PORT 사용: {port}")
        except (ValueError, TypeError):
            print(f"❌ 환경변수 PORT가 유효하지 않음: {port_env}, 기본값 사용: {port}")
    else:
        print(f"📍 기본 포트 사용: {port}")
    
    print(f"🌐 서버 시작 - 포트: {port}")
    
    # main 모듈 import
    try:
        from main import app
        print("✅ 앱 로드 성공")
        
        # 서버 시작
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 