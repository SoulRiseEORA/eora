@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    🚀 EORA AI 안정 서버 실행 (GPT 연동)
echo ========================================
echo.

REM OpenAI API 키 설정 (여기에 실제 API 키를 입력하세요)
set OPENAI_API_KEY=sk-your-api-key-here

REM API 키가 설정되지 않았으면 경고
if "%OPENAI_API_KEY%"=="sk-your-api-key-here" (
    echo ⚠️  경고: OpenAI API 키가 설정되지 않았습니다!
    echo.
    echo 이 파일을 편집하여 실제 API 키를 입력하세요:
    echo set OPENAI_API_KEY=sk-실제API키
    echo.
    echo API 키가 없으면 기본 응답만 제공됩니다.
    echo.
    pause
)

REM 모든 Python 프로세스 종료
echo 🔄 기존 서버 종료 중...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im py.exe >nul 2>&1
timeout /t 2 >nul

REM 포트 8100 정리
echo 🧹 포트 8100 정리 중...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8100') do (
    taskkill /f /pid %%a >nul 2>&1
)
timeout /t 1 >nul

REM Python 경로 확인
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python 발견: python
    echo ✅ OpenAI API 키: %OPENAI_API_KEY:~0,7%...
    echo.
    echo 🚀 안정 서버 시작 중...
    echo.
    python stable_server.py
) else (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Python 발견: py
        echo ✅ OpenAI API 키: %OPENAI_API_KEY:~0,7%...
        echo.
        echo 🚀 안정 서버 시작 중...
        echo.
        py stable_server.py
    ) else (
        echo ❌ Python을 찾을 수 없습니다.
        echo Python이 설치되어 있는지 확인하세요.
    )
)

pause 