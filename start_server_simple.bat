@echo off
chcp 65001
echo 🚀 EORA AI 서버 시작 중...
echo.

REM 기존 Python 프로세스 종료
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 >nul

REM Python 경로 확인
echo Python 경로 확인 중...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python을 찾을 수 없습니다.
    echo Python이 설치되어 있는지 확인하세요.
    pause
    exit /b 1
)

echo ✅ Python 발견됨

REM 디렉토리 이동
cd /d "%~dp0"

REM 간단한 서버 시작
echo 🚀 디버그 서버 시작...
python debug_server.py

pause 