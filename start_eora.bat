@echo off
chcp 65001 > nul
echo 🚀 EORA AI 시스템 시작 중...
echo.

:: 기존 Python 프로세스 정리
echo 🔄 기존 프로세스 정리 중...
taskkill /F /IM python.exe > nul 2>&1

:: 3초 대기
timeout /t 3 /nobreak > nul

:: src 디렉토리로 이동
cd /d "%~dp0src"
echo 📁 작업 디렉토리: %CD%

:: 환경변수 확인
echo 🔍 환경변수 확인 중...
python -c "import os; from dotenv import load_dotenv; load_dotenv('../.env'); key=os.getenv('OPENAI_API_KEY',''); print(f'✅ API 키: {key[:10]}...{key[-4:]}' if key else '❌ API 키 설정 안됨')"

echo.
echo 🚀 EORA AI 서버 시작...
echo 📍 접속 주소: http://127.0.0.1:8001
echo 🔧 관리자 페이지: http://127.0.0.1:8001/admin
echo.
echo 💡 서버를 종료하려면 Ctrl+C를 누르세요
echo =====================================

:: FastAPI 서버 시작
python -m uvicorn app:app --host 127.0.0.1 --port 8001 --reload

pause 