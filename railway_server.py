#!/usr/bin/env python3
"""
Railway 배포 전용 EORA AI 서버
"""

import os
import sys
import logging
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

def setup_railway_environment():
    """Railway 환경 설정"""
    logger.info("🚂 Railway 환경 설정 시작")
    
    # Railway 환경변수 확인
    required_vars = [
        'OPENAI_API_KEY',
        'MONGO_URL', 
        'MONGO_PUBLIC_URL',
        'PORT'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"⚠️ 누락된 환경변수: {missing_vars}")
        logger.info("🔧 Railway 대시보드에서 환경변수를 설정해주세요.")
    else:
        logger.info("✅ 모든 필수 환경변수가 설정되었습니다.")
    
    # 포트 설정
    port = int(os.getenv('PORT', 8080))
    logger.info(f"📍 서버 포트: {port}")
    
    # OpenAI API 키 확인
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and openai_key.startswith('sk-'):
        logger.info("✅ OpenAI API 키가 설정되었습니다.")
    else:
        logger.warning("⚠️ OpenAI API 키가 올바르게 설정되지 않았습니다.")
    
    # MongoDB 연결 확인
    mongo_url = os.getenv('MONGO_URL') or os.getenv('MONGO_PUBLIC_URL')
    if mongo_url:
        logger.info("✅ MongoDB 연결 URL이 설정되었습니다.")
    else:
        logger.warning("⚠️ MongoDB 연결 URL이 설정되지 않았습니다.")
    
    return port

def main():
    """메인 실행 함수"""
    try:
        # Railway 환경 설정
        port = setup_railway_environment()
        
        # final_server 모듈 임포트
        logger.info("📦 final_server 모듈 로드 중...")
        from final_server import app
        
        # 서버 시작
        import uvicorn
        logger.info(f"🚀 Railway EORA AI 서버 시작 (포트: {port})")
        logger.info("📍 서버 주소: http://0.0.0.0:" + str(port))
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        
    except ImportError as e:
        logger.error(f"❌ 모듈 임포트 오류: {e}")
        logger.error("final_server.py 파일이 존재하는지 확인해주세요.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 서버 시작 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 