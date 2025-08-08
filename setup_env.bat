@echo off
echo OpenAI API 키 설정 스크립트
echo ================================

set /p OPENAI_API_KEY="OpenAI API 키를 입력하세요: "

if "%OPENAI_API_KEY%"=="" (
    echo API 키가 입력되지 않았습니다.
    pause
    exit /b 1
)

echo.
echo API 키가 설정되었습니다: %OPENAI_API_KEY%
echo.
echo 이제 서버를 시작하세요:
echo python -m uvicorn app:app --host 127.0.0.1 --port 8081 --reload
echo.
pause 