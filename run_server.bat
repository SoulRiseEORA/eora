@echo off
echo 🚀 EORA AI System 서버 시작 중...
echo 📁 작업 디렉토리: %CD%
echo.

REM 포트 확인 및 설정
set PORT=8081
echo 🔌 포트: %PORT%

REM Python 환경 확인
python --version
echo.

REM 서버 시작
echo 🚀 uvicorn 서버 시작...
python -m uvicorn main:app --host 127.0.0.1 --port %PORT% --reload

pause 