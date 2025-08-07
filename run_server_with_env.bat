@echo off
chcp 65001 > nul
echo 🚀 EORA AI 로컬 서버 시작 (환경 변수 포함)

REM .env 파일 확인
if not exist .env (
    echo ❌ .env 파일이 없습니다!
    echo.
    echo setup_local_env.bat를 먼저 실행하세요.
    pause
    exit /b 1
)

REM .env 파일에서 환경 변수 로드
echo 📋 .env 파일에서 환경 변수를 로드합니다...
for /f "tokens=1,2 delims==" %%a in (.env) do (
    REM 주석과 빈 줄 제외
    echo %%a | findstr /r "^#" >nul || (
        if not "%%a"=="" if not "%%b"=="" (
            set "%%a=%%b"
            echo   ✓ %%a 설정됨
        )
    )
)

REM src 폴더에도 .env 파일 복사
echo.
echo 📂 src 폴더에 .env 파일 복사...
copy .env src\.env >nul 2>&1

REM OpenAI API 키 확인
if "%OPENAI_API_KEY%"=="YOUR_API_KEY" (
    echo.
    echo ⚠️  경고: OpenAI API 키가 설정되지 않았습니다!
    echo    .env 파일을 열어서 OPENAI_API_KEY를 실제 키로 변경하세요.
    echo.
    notepad .env
    pause
    exit /b 1
)

echo.
echo ✅ 환경 변수 설정 완료
echo 🌐 서버 시작: http://127.0.0.1:8001
echo.

REM 서버 실행
python -m uvicorn src.app:app --host 127.0.0.1 --port 8001 --reload

pause 