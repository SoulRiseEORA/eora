#!/usr/bin/env python3
"""
로컬 개발 서버 실행 스크립트
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
        logger.info("🚀 로컬 개발 서버 시작 중...")
        logger.info("📁 작업 디렉토리: %s", os.getcwd())
        
        # app.py 파일 존재 확인
        if not os.path.exists("app.py"):
            logger.error("❌ app.py 파일이 존재하지 않습니다!")
            return 1
        
        logger.info("✅ app.py 파일 확인 완료")
        
        # 환경변수 설정
        os.environ["ENVIRONMENT"] = "development"
        
        # uvicorn 명령어 실행
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "app:app", 
            "--host", "127.0.0.1", 
            "--port", "8001", 
            "--reload"
        ]
        
        logger.info("🚀 uvicorn 서버 시작...")
        logger.info("📍 호스트: 127.0.0.1")
        logger.info("🔌 포트: 8001")
        logger.info("🔄 자동 리로드: 활성화")
        
        # 서버 실행
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        logger.info("🛑 서버가 중단되었습니다.")
        return 0
    except subprocess.CalledProcessError as e:
        logger.error("❌ 서버 실행 중 오류 발생: %s", e)
        return 1
    except Exception as e:
        logger.error("❌ 예상치 못한 오류 발생: %s", e)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 