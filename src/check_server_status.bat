@echo off
echo 🔍 EORA AI System 서버 상태 확인 중...
echo.

REM 포트 8081 확인
netstat -an | findstr :8081 > nul
if %errorlevel% equ 0 (
    echo ✅ 포트 8081: 사용 중
) else (
    echo ❌ 포트 8081: 사용 안함
)

REM 포트 8082 확인
netstat -an | findstr :8082 > nul
if %errorlevel% equ 0 (
    echo ✅ 포트 8082: 사용 중
) else (
    echo ❌ 포트 8082: 사용 안함
)

echo.
echo 📋 현재 실행 중인 Python 프로세스:
tasklist | findstr python

echo.
echo 🌐 웹 브라우저에서 다음 URL을 확인하세요:
echo http://127.0.0.1:8081
echo http://127.0.0.1:8082

pause 