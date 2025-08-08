@echo off
chcp 65001 >nul
echo 🤖 EORA AI - OpenAI API 키 설정 도우미
echo ================================================

echo.
echo 🔍 현재 OpenAI API 키 상태 확인 중...
python setup_openai_env.py

echo.
echo 💡 추가 도움말:
echo 1. Railway 배포 시: Railway 대시보드 > Service > Variables에서 설정
echo 2. 로컬 개발 시: 이 배치 파일을 실행하거나 환경변수를 직접 설정
echo 3. API 키는 https://platform.openai.com/api-keys 에서 발급 가능
echo.
pause 