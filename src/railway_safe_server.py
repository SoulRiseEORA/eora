#!/usr/bin/env python3
"""
🚀 Railway 안전 서버 - 502 오류 완전 방지
모든 환경변수와 의존성을 안전하게 처리하여 Railway에서 안정적으로 실행
"""

import os
import sys
import logging
import uvicorn
from pathlib import Path

# 로깅 설정 - Railway 호환
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def safe_get_env(key: str, default: str = "") -> str:
    """환경변수를 안전하게 가져오기"""
    try:
        value = os.environ.get(key, default)
        if value:
            # 따옴표와 공백 제거
            value = value.strip().replace('"', '').replace("'", "")
        return value
    except Exception as e:
        logger.warning(f"환경변수 {key} 읽기 실패: {e}")
        return default

def setup_railway_environment():
    """Railway 환경 안전 설정"""
    logger.info("🚂 Railway 환경 안전 설정 시작")
    
    # 필수 환경변수 안전 설정
    required_vars = {
        "OPENAI_API_KEY": "",
        "MONGODB_URI": "mongodb://localhost:27017",
        "DATABASE_NAME": "eora_ai",
        "ENABLE_POINTS_SYSTEM": "true",
        "DEFAULT_POINTS": "100000",
        "SESSION_SECRET": "eora_railway_session_secret_2024",
        "MAX_SESSIONS_PER_USER": "50",
        "SESSION_TIMEOUT": "3600"
    }
    
    # 환경변수 안전 확인 및 설정
    for key, default_value in required_vars.items():
        current_value = safe_get_env(key, default_value)
        if not current_value and default_value:
            os.environ[key] = default_value
            logger.info(f"✅ {key}: 기본값 설정")
        else:
            logger.info(f"✅ {key}: 설정됨")
    
    # OpenAI API 키 특별 확인
    openai_key = safe_get_env("OPENAI_API_KEY")
    if openai_key and openai_key.startswith("sk-"):
        logger.info("✅ OpenAI API 키 유효")
    else:
        logger.warning("⚠️ OpenAI API 키 미설정 - 환경변수에서 설정 필요")
    
    return True

def main():
    """안전한 서버 시작"""
    try:
        logger.info("🚀 Railway 안전 서버 시작")
        
        # 환경 설정
        setup_railway_environment()
        
        # 포트 설정 - Railway 호환
        port = int(safe_get_env("PORT", "8080"))
        host = "0.0.0.0"
        
        logger.info(f"📍 호스트: {host}")
        logger.info(f"🔌 포트: {port}")
        
        # 작업 디렉토리 확인
        work_dir = os.getcwd()
        logger.info(f"📁 작업 디렉토리: {work_dir}")
        
        # app.py 파일 존재 확인
        app_file = Path("app.py")
        if not app_file.exists():
            logger.error("❌ app.py 파일이 존재하지 않습니다!")
            return False
        
        logger.info("✅ app.py 파일 확인 완료")
        
        # FastAPI 앱 import - 안전하게
        try:
            from app import app
            logger.info("✅ FastAPI 앱 로드 성공")
        except Exception as e:
            logger.error(f"❌ FastAPI 앱 로드 실패: {e}")
            # 대체 방법으로 앱 로드 시도
            sys.path.insert(0, os.getcwd())
            try:
                import app as app_module
                app = app_module.app
                logger.info("✅ 대체 방법으로 FastAPI 앱 로드 성공")
            except Exception as e2:
                logger.error(f"❌ 대체 방법 실패: {e2}")
                return False
        
        # 서버 시작 - Railway 호환 설정
        logger.info("🌐 uvicorn 서버 시작 중...")
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            use_colors=False,  # Railway 로그 호환
            server_header=False,
            date_header=False
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 서버 중단됨 (Ctrl+C)")
        return True
    except Exception as e:
        logger.error(f"❌ 서버 시작 실패: {e}")
        logger.error(f"❌ 오류 상세: {type(e).__name__}: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        logger.error("❌ 서버 실행 실패")
        sys.exit(1)
    else:
        logger.info("✅ 서버 정상 종료")
        sys.exit(0) 