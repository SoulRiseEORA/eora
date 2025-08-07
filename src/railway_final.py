#!/usr/bin/env python3
"""
Railway 최종 배포 스크립트
app.py를 직접 실행하여 main.py 의존성 제거
"""

import os
import sys
import subprocess
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """메인 실행 함수"""
    try:
        logger.info("🚀 Railway 서버 시작 중...")
        logger.info("🌍 환경: production")
        logger.info("📁 작업 디렉토리: %s", os.getcwd())
        
        # app.py 파일 존재 확인
        if not os.path.exists("app.py"):
            logger.error("❌ app.py 파일이 존재하지 않습니다!")
            return 1
        
        logger.info("✅ app.py 파일 확인 완료")
        
        # Railway 환경변수에서 포트 가져오기 (기본값 8080)
        port = os.environ.get("PORT", "8080")
        host = "0.0.0.0"
        
        logger.info("📍 호스트: %s", host)
        logger.info("🔌 포트: %s", port)
        
        # 환경변수 확인
        logger.info("🔍 환경변수 확인:")
        for key in ["PORT", "OPENAI_API_KEY", "MONGODB_URI"]:
            value = os.environ.get(key, "설정되지 않음")
            if key == "OPENAI_API_KEY" and value != "설정되지 않음":
                value = value[:10] + "..."  # API 키 일부만 표시
            logger.info("  %s: %s", key, value)
        
        logger.info("🚀 uvicorn 서버 시작...")
        
        # uvicorn 명령어 실행
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "app:app", 
            "--host", host,
            "--port", port,
            "--workers", "1"
        ]
        
        logger.info("📋 실행 명령어: %s", " ".join(cmd))
        
        # 서버 실행
        result = subprocess.run(cmd, check=True)
        return result.returncode
        
    except subprocess.CalledProcessError as e:
        logger.error("❌ 서버 실행 실패: %s", e)
        return e.returncode
    except KeyboardInterrupt:
        logger.info("🛑 사용자에 의해 중단됨")
        return 0
    except Exception as e:
        logger.error("❌ 예상치 못한 오류: %s", e)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 