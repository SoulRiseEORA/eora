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

REM 서버 실행
cd src
python app_modular.py

pause 