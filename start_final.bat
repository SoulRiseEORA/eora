@echo off
chcp 65001 > nul
cls
echo.
echo ========================================
echo 🚀 EORA AI 시스템 최종 시작
echo ========================================
echo.

:: 기존 프로세스 정리
echo 🔄 기존 Python 프로세스 정리 중...
taskkill /F /IM python.exe > nul 2>&1
timeout /t 2 /nobreak > nul

:: 환경변수 확인
echo 🔍 환경변수 확인 중...
if exist .env (
    echo ✅ .env 파일 발견
) else (
    echo ❌ .env 파일이 없습니다
)

:: src 디렉토리로 이동
cd /d "%~dp0src"
echo 📁 작업 디렉토리: %CD%

echo.
echo 🎯 접속 주소 목록:
echo 📍 메인 서버: http://127.0.0.1:8001
echo 🔧 관리자 페이지: http://127.0.0.1:8001/admin
echo 📊 상태 확인: http://127.0.0.1:8001/health
echo.
echo 💡 서버를 종료하려면 이 창을 닫으세요
echo ========================================
echo.

:: 메인 서버 시작
echo 🚀 EORA AI 서버 시작 중...
python -m uvicorn app:app --host 127.0.0.1 --port 8001 --reload

pause 