@echo off
chcp 65001
echo 🚀 EORA AI 포트 8002 서버 시작 중...
echo.

REM 기존 Python 프로세스 종료
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 >nul

REM 포트 8002 사용 중인 프로세스 종료
echo 포트 8002 확인 중...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do (
    echo 프로세스 %%a 종료 중...
    taskkill /f /pid %%a >nul 2>&1
)
timeout /t 2 >nul

REM Python 경로 확인
echo Python 경로 확인 중...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ python 명령어 실패
    echo.
    echo py 명령어 확인 중...
    where py >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ py 명령어도 실패
        echo.
        echo ========================================
        echo ❌ Python이 설치되어 있지 않거나 PATH에 없습니다
        echo.
        echo 해결 방법:
        echo 1. https://python.org 에서 Python 다운로드
        echo 2. 설치 시 "Add Python to PATH" 체크
        echo 3. 컴퓨터 재시작
        echo 4. 이 배치 파일 다시 실행
        echo ========================================
        pause
        exit /b 1
    ) else (
        echo ✅ py 명령어 발견
        set PYTHON_CMD=py
    )
) else (
    echo ✅ python 명령어 발견
    set PYTHON_CMD=python
)

echo.
echo 🚀 포트 8002 서버 시작...
echo 📍 접속 주소: http://127.0.0.1:8002
echo 📊 API 상태: http://127.0.0.1:8002/api/status
echo 🧪 테스트: http://127.0.0.1:8002/test
echo ❤️ 헬스 체크: http://127.0.0.1:8002/health
echo.

REM 디렉토리 이동
cd /d "%~dp0"

REM 포트 8002 서버 시작
%PYTHON_CMD% port_8002_server.py

pause 