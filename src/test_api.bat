@echo off
echo 🧪 EORA AI System API 테스트 중...
echo.

REM 서버가 실행 중인지 확인
netstat -an | findstr :8081 > nul
if %errorlevel% equ 0 (
    set TEST_PORT=8081
) else (
    netstat -an | findstr :8082 > nul
    if %errorlevel% equ 0 (
        set TEST_PORT=8082
    ) else (
        echo ❌ 서버가 실행 중이지 않습니다.
        echo 💡 start_server.bat를 먼저 실행하세요.
        pause
        exit /b 1
    )
)

echo 📍 테스트 포트: %TEST_PORT%
echo.

REM 메인 페이지 테스트
echo 🔍 메인 페이지 테스트...
curl -s http://127.0.0.1:%TEST_PORT%/ > nul
if %errorlevel% equ 0 (
    echo ✅ 메인 페이지: 정상
) else (
    echo ❌ 메인 페이지: 오류
)

REM 프롬프트 API 테스트
echo 🔍 프롬프트 API 테스트...
curl -s http://127.0.0.1:%TEST_PORT%/api/prompts > nul
if %errorlevel% equ 0 (
    echo ✅ 프롬프트 API: 정상
) else (
    echo ❌ 프롬프트 API: 오류
)

REM 관리자 페이지 테스트
echo 🔍 관리자 페이지 테스트...
curl -s http://127.0.0.1:%TEST_PORT%/admin > nul
if %errorlevel% equ 0 (
    echo ✅ 관리자 페이지: 정상
) else (
    echo ❌ 관리자 페이지: 오류
)

echo.
echo 🌐 웹 브라우저에서 확인:
echo http://127.0.0.1:%TEST_PORT%/
echo http://127.0.0.1:%TEST_PORT%/admin

pause 