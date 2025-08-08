#!/usr/bin/env python3
"""
Railway 배포용 클라우드 스타일 스크립트
환경변수 처리를 완전히 안전하게 수행
"""

import os
import sys
import uvicorn

def main():
    """메인 함수"""
    print("🚀 EORA AI Railway 클라우드 스타일 서버 시작")
    
    # 포트 설정 - 클라우드 스타일
    port = int(os.environ.get('PORT', 8080))
    print(f"📍 포트: {port}")
    
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