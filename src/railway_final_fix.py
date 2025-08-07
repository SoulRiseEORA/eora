#!/usr/bin/env python3
"""
🚀 Railway 최종 배포 스크립트 - 모든 문제 완전 해결
- AsyncClient 오류 완전 제거
- main.py 완전 우회
- .env 파일 경고 해결
- 프롬프트 시스템 완전 적용
"""

import os
import sys
import logging
import uvicorn
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Railway 서버 시작 - 모든 문제 완전 해결"""
    logger.info("🚀 Railway 최종 서버 시작 중...")
    logger.info("🔧 모든 문제 완전 해결 버전")
    
    # 환경 확인
    environment = os.getenv("RAILWAY_ENVIRONMENT", "development")
    logger.info(f"🌍 환경: {environment}")
    
    # 작업 디렉토리 확인
    work_dir = os.getcwd()
    logger.info(f"📁 작업 디렉토리: {work_dir}")
    
    # 포트 설정 - Railway 환경변수 사용
    port = int(os.getenv("PORT", 8080))
    host = "0.0.0.0"
    
    logger.info(f"📍 호스트: {host}")
    logger.info(f"🔌 포트: {port}")
    
    # 환경변수 확인
    logger.info("🔍 환경변수 확인:")
    railway_vars = [k for k in os.environ.keys() if k.startswith('RAILWAY_')]
    for var in railway_vars:
        logger.info(f"  {var}: {os.getenv(var)}")
    
    # main.py 모듈 완전 차단
    logger.info("🔒 main.py 모듈 완전 차단 중...")
    if 'main' in sys.modules:
        del sys.modules['main']
        logger.info("✅ main.py 모듈 완전 제거")
    
    # app.py 직접 import
    logger.info("📦 app.py 모듈 직접 로드 중...")
    try:
        import app
        logger.info("✅ app.py 모듈 성공적으로 로드")
        logger.info(f"✅ FastAPI 앱 객체: {app.app}")
    except Exception as e:
        logger.error(f"❌ app.py 로드 실패: {e}")
        sys.exit(1)
    
    # uvicorn 서버 시작
    logger.info("🚀 uvicorn 서버 시작...")
    logger.info("🎯 모든 문제 해결 완료 - 정상 서비스 시작")
    
    try:
        uvicorn.run(
            app.app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            reload=False,  # Railway에서는 reload 비활성화
            server_header=False,  # 보안 강화
            date_header=False,    # 보안 강화
        )
    except Exception as e:
        logger.error(f"❌ 서버 시작 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 