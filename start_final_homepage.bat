@echo off
chcp 65001
echo 🚀 EORA AI 최종 홈페이지 서버 시작...
echo.

REM Python 프로세스 종료
echo 🔄 기존 Python 프로세스 종료 중...
taskkill /f /im python.exe >nul 2>&1

REM 포트 8005 사용 중인 프로세스 확인 및 종료
echo 🔍 포트 8005 사용 중인 프로세스 확인...
netstat -ano | findstr :8005 >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️ 포트 8005가 사용 중입니다. 프로세스를 종료합니다...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8005') do (
        taskkill /f /pid %%a >nul 2>&1
    )
)

REM 잠시 대기
timeout /t 2 /nobreak >nul

echo ✅ 서버 시작 준비 완료
echo 📍 접속 주소: http://127.0.0.1:8005
echo.

REM 서버 시작
cd /d "%~dp0"
python final_homepage_server.py

pause 