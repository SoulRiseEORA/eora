@echo off
echo 🚀 EORA AI System 서버 시작 중...
echo.

REM 현재 디렉토리로 이동
cd /d "E:\AI_Dev_Tool\src"

REM 포트 사용 확인
netstat -an | findstr :8081
if %errorlevel% equ 0 (
    echo ⚠️ 포트 8081이 이미 사용 중입니다. 다른 포트를 사용합니다.
    set PORT=8082
) else (
    set PORT=8081
)

echo 📍 서버 포트: %PORT%
echo.

REM 서버 시작
python -m uvicorn main:app --host 127.0.0.1 --port %PORT% --reload

pause 