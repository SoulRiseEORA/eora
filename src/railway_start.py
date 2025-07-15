#!/usr/bin/env python3
"""
🚀 Railway 최종 시작 스크립트 - main.py 완전 무시
- main.py 파일을 완전히 무시하고 app.py만 실행
- AsyncClient 오류 완전 방지
- Railway 환경 최적화
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
    logger.info("🚀 Railway 최종 서버 시작...")
    logger.info("🔧 main.py 완전 무시 버전")
    
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
    
    # main.py 파일 완전 무시
    logger.info("🚫 main.py 파일 완전 무시 중...")
    
    # 1. main.py 파일을 임시로 숨김
    main_file = Path("main.py")
    if main_file.exists():
        hidden_name = ".main_hidden.py"
        try:
            main_file.rename(hidden_name)
            logger.info(f"✅ main.py를 {hidden_name}으로 숨김")
        except Exception as e:
            logger.warning(f"⚠️ main.py 숨김 실패: {e}")
    
    # 2. main 모듈 import 완전 차단
    class MainBlocker:
        def find_spec(self, name, path, target=None):
            if name == 'main' or name.startswith('main.'):
                logger.info(f"🚫 main 모듈 import 차단: {name}")
                return None
            return None
    
    sys.meta_path.insert(0, MainBlocker())
    logger.info("✅ main 모듈 import 완전 차단")
    
    # 3. sys.modules에서 main 제거
    if 'main' in sys.modules:
        del sys.modules['main']
        logger.info("✅ main 모듈 sys.modules에서 제거")
    
    # app.py 직접 실행
    logger.info("📦 app.py 직접 실행 중...")
    try:
        # app.py 파일이 존재하는지 확인
        app_file = Path("app.py")
        if not app_file.exists():
            logger.error("❌ app.py 파일을 찾을 수 없습니다")
            sys.exit(1)
        
        # app.py import
        import app
        logger.info("✅ app.py 모듈 성공적으로 로드")
        logger.info(f"✅ FastAPI 앱 객체: {app.app}")
        
    except Exception as e:
        logger.error(f"❌ app.py 로드 실패: {e}")
        # main.py 복원
        hidden_file = Path(".main_hidden.py")
        if hidden_file.exists():
            try:
                hidden_file.rename("main.py")
                logger.info("✅ main.py 복원 완료")
            except:
                pass
        sys.exit(1)
    
    # uvicorn 서버 시작
    logger.info("🚀 uvicorn 서버 시작...")
    logger.info("🎯 main.py 완전 무시 - app.py만 실행")
    
    try:
        uvicorn.run(
            app.app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            reload=False,
            server_header=False,
            date_header=False,
        )
    except Exception as e:
        logger.error(f"❌ 서버 시작 실패: {e}")
        # main.py 복원
        hidden_file = Path(".main_hidden.py")
        if hidden_file.exists():
            try:
                hidden_file.rename("main.py")
                logger.info("✅ main.py 복원 완료")
            except:
                pass
        sys.exit(1)

if __name__ == "__main__":
    main() 