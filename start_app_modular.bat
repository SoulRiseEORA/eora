@echo off
echo ====================================
echo EORA AI System - 모듈화 버전 시작
echo 버전: 2.1.0 (모듈화)
echo ====================================

cd /d src

echo 현재 디렉토리: %CD%

echo Python 버전 확인...
python --version

echo 필요한 패키지 설치 확인...
pip install fastapi uvicorn python-dotenv pymongo openai pydantic

echo 서버 시작 중...
python app_modular.py

echo.
echo 만약 위 명령이 실패하면 아래 명령을 시도하세요:
echo python -m uvicorn app_modular:app --host 127.0.0.1 --port 8001 --reload

pause 