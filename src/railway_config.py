#!/usr/bin/env python3
"""
🚀 Railway 설정 파일 - main.py 완전 무시
- Railway에서 main.py를 실행하지 않도록 설정
- app.py만 직접 실행
- 모든 오류 완전 방지
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
    """Railway 서버 시작 - main.py 완전 무시"""
    logger.info("🚀 Railway 설정 서버 시작...")
    logger.info("🔧 main.py 완전 무시 설정")
    
    # 환경 확인
    environment = os.getenv("RAILWAY_ENVIRONMENT", "development")
    logger.info(f"🌍 환경: {environment}")
    
    # 작업 디렉토리 확인
    work_dir = os.getcwd()
    logger.info(f"📁 작업 디렉토리: {work_dir}")
    
    # 포트 설정
    port = int(os.getenv("PORT", 8080))
    host = "0.0.0.0"
    
    logger.info(f"📍 호스트: {host}")
    logger.info(f"🔌 포트: {port}")
    
    # main.py 파일을 임시로 숨김
    main_file = Path("main.py")
    backup_file = Path("main_backup.py")
    
    if main_file.exists():
        try:
            # main.py를 백업 파일로 이동
            main_file.rename(backup_file)
            logger.info("✅ main.py를 main_backup.py로 이동")
        except Exception as e:
            logger.warning(f"⚠️ main.py 이동 실패: {e}")
    
    # app.py만 import하여 실행
    try:
        import app
        logger.info("✅ app.py 로드 성공")
        
        uvicorn.run(
            app.app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            reload=False  # Railway에서는 reload 비활성화
        )
    except Exception as e:
        logger.error(f"❌ app.py 실행 실패: {e}")
        
        # 오류 발생 시 main.py 복원
        if backup_file.exists():
            try:
                backup_file.rename(main_file)
                logger.info("✅ main.py 복원 완료")
            except:
                pass
        
        sys.exit(1)

if __name__ == "__main__":
    main() 