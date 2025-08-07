@echo off
echo 🔄 서버 재시작 중...

REM 기존 Python 프로세스 종료
echo 🛑 기존 서버 종료 중...
taskkill /F /IM python.exe 2>nul

REM 잠시 대기
timeout /t 2 >nul

REM 새 서버 시작
echo 🚀 새 서버 시작 중...
cd /d %~dp0
python -m uvicorn src.app:app --host 127.0.0.1 --port 8001 --reload

pause 