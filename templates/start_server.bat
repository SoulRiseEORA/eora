@echo off
echo 🚀 EORA AI System 서버 시작 중...
echo.

REM 기존 Python 프로세스 종료
taskkill /f /im python.exe >nul 2>&1
echo ✅ 기존 프로세스 정리 완료

REM 잠시 대기
timeout /t 2 /nobreak >nul

REM 서버 시작
echo 🚀 서버 시작 중...
python final_server.py

pause 