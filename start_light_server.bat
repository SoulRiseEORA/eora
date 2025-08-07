@echo off
setlocal enabledelayedexpansion
echo 🚀 EORA AI - 메모리 최적화 서버 시작
echo ========================================
echo.

REM 메모리 정리
echo 💾 시스템 메모리 정리 중...
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM OpenAI API 키 입력
if "%OPENAI_API_KEY%"=="" (
    echo 🔑 OpenAI API 키를 설정해주세요
    echo 📍 API 키는 https://platform.openai.com/account/api-keys 에서 생성
    echo.
    set /p API_KEY="OpenAI API 키를 입력하세요: "
    
    if "!API_KEY!"=="" (
        echo ❌ API 키가 입력되지 않았습니다.
        pause
        exit /b 1
    )
    
    set OPENAI_API_KEY=!API_KEY!
)

REM 환경변수 설정
echo ✅ 환경변수 설정 중...
set MONGODB_URI=mongodb://localhost:27017
set PYTHONUNBUFFERED=1
set PYTHONHASHSEED=random

REM 메모리 제한 설정 (Python)
set PYTHON_GC_THRESHOLD=100,10,10

echo.
echo 🔧 설정 완료:
echo   📍 서버 주소: http://127.0.0.1:8002
echo   🔐 관리자: admin@eora.ai / admin1234
echo   💾 메모리 최적화: 활성화
echo.

REM 서버 시작 (메모리 최적화)
cd src
echo 🚀 서버 시작 중...
python -X dev -m uvicorn app:app --host 0.0.0.0 --port 8002 --workers 1 --limit-max-requests 100

pause 