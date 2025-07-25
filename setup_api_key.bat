@echo off
echo 🔧 EORA AI - OpenAI API 키 설정
echo ===============================
echo.
echo 중요: 실제 OpenAI API 키를 입력해주세요!
echo API 키는 https://platform.openai.com/account/api-keys 에서 생성할 수 있습니다.
echo.

set /p API_KEY="OpenAI API 키를 입력하세요 (sk-proj-로 시작): "

if "%API_KEY%"=="" (
    echo.
    echo ❌ API 키가 입력되지 않았습니다.
    echo.
    pause
    exit /b 1
)

if not "%API_KEY:~0,7%"=="sk-proj" (
    echo.
    echo ⚠️ 경고: API 키가 'sk-proj'로 시작하지 않습니다.
    echo 올바른 OpenAI API 키인지 확인해주세요.
    echo.
)

echo.
echo ✅ 환경변수 설정 중...
set OPENAI_API_KEY=%API_KEY%
set MONGODB_URI=mongodb://localhost:27017

echo.
echo 🚀 서버 시작 중...
echo 📍 접속 주소: http://127.0.0.1:8002
echo 🔐 관리자: admin@eora.ai / admin1234
echo.

cd src
python -m uvicorn app:app --host 0.0.0.0 --port 8002 --reload

pause 