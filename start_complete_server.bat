@echo off
echo 🚀 EORA AI 완전 서버 시작...
echo.

REM Python 프로세스 종료
taskkill /f /im python.exe >nul 2>&1
echo ✅ 기존 Python 프로세스 종료 완료

REM 포트 8009 사용 중인 프로세스 종료
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8009') do (
    taskkill /f /pid %%a >nul 2>&1
)
echo ✅ 포트 8009 정리 완료

REM 서버 시작
echo 📍 서버 시작 중...
python complete_server.py

pause 