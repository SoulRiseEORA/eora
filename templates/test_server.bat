@echo off
echo 🧪 EORA AI System 서버 테스트 시작
echo.

REM 서버가 실행 중인지 확인
echo 🔍 서버 상태 확인 중...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 서버가 실행 중입니다.
    echo.
    echo 🧪 테스트 실행 중...
    python test_server_simple.py
) else (
    echo ❌ 서버가 실행되지 않았습니다.
    echo 🚀 서버를 먼저 시작해주세요.
    echo.
    echo start_server.bat을 실행하세요.
)

echo.
pause 