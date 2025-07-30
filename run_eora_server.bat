@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    🚀 EORA AI 서버 실행기
echo ========================================
echo.

REM 기존 Python 프로세스 모두 종료
echo 🔄 기존 서버 종료 중...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im py.exe >nul 2>&1
ping 127.0.0.1 -n 3 >nul

REM 포트 확인 및 정리
echo 🧹 포트 정리 중...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8007') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8011') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8012') do taskkill /f /pid %%a >nul 2>&1
ping 127.0.0.1 -n 2 >nul

REM Python 실행 확인
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
    ) else (
        echo ❌ Python이 설치되어 있지 않습니다!
        echo Python을 먼저 설치해주세요.
        pause
        exit /b 1
    )
)

echo.
echo 🚀 서버를 시작합니다...
echo.

REM final_homepage_server.py 실행 (포트 8007)
if exist "final_homepage_server.py" (
    echo ✅ EORA AI 서버 시작 (포트 8007)
    echo.
    echo ========================================
    echo 📌 서버 정보
    echo ========================================
    echo 🌐 홈페이지: http://127.0.0.1:8007
    echo 🔐 로그인: http://127.0.0.1:8007/login
    echo ⚙️ 관리자: http://127.0.0.1:8007/admin
    echo 💬 채팅: http://127.0.0.1:8007/chat
    echo ========================================
    echo 📧 관리자 계정: admin@eora.ai
    echo 🔑 비밀번호: admin123
    echo ========================================
    echo.
    echo 💡 브라우저가 자동으로 열립니다...
    ping 127.0.0.1 -n 3 >nul
    start http://127.0.0.1:8007
    echo.
    %PYTHON_CMD% final_homepage_server.py
) else (
    echo ❌ final_homepage_server.py 파일을 찾을 수 없습니다!
    pause
    exit /b 1
)

pause 