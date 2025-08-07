@echo off
echo EORA AI 서버를 시작합니다...

REM 기존 Python 프로세스 종료 시도
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak > nul

REM 서버 실행
cd src
set OPENAI_API_KEY=sk-test-api-key-for-testing-only
python -m uvicorn app_modular:app --host 0.0.0.0 --port 8011
pause 