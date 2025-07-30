@echo off
echo 🚀 EORA AI System - 모듈화된 서버 시작 중...

REM 환경 변수 설정
set OPENAI_API_KEY=your_openai_api_key_here
set DATABASE_NAME=eora_ai
set PORT=8010

REM 현재 디렉토리 저장
set CURRENT_DIR=%CD%

REM src 디렉토리로 이동
cd src
echo 📂 src 디렉토리로 이동했습니다.

REM 서버 실행
echo 🚀 서버를 시작합니다. (포트: %PORT%)
python run_railway_server.py --port %PORT%

REM 원래 디렉토리로 복귀
cd %CURRENT_DIR%

pause 