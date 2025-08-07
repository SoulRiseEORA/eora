@echo off
chcp 65001 > nul
echo EORA AI 서버를 시작합니다...

REM 기존 Python 프로세스 종료 시도
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak > nul

REM 환경 변수 설정
set OPENAI_API_KEY=sk-test-api-key-for-testing-only

REM 디렉토리 생성 확인
mkdir src\backups 2>nul

REM 새 명령 프롬프트 창에서 서버 실행
start cmd /c "cd src && python -m uvicorn app_modular:app --host 0.0.0.0 --port 8011 --reload"

echo 서버가 시작되었습니다. 브라우저에서 http://localhost:8011 으로 접속하세요. 