@echo off
chcp 65001
echo 🚨 EORA AI 긴급 서버 시작 중...
echo.

REM 기존 Python 프로세스 종료
taskkill /f /im python.exe >nul 2>&1
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
echo 🚀 긴급 서버 시작...
echo 📍 접속 주소: http://127.0.0.1:8011
echo.
echo ⚠️ 이 서버는 긴급 상황을 위한 최소 기능 버전입니다.
echo 완전한 기능을 사용하려면 FastAPI 서버를 실행하세요.
echo.

REM 디렉토리 이동
cd /d "%~dp0"

REM 긴급 서버 시작
%PYTHON_CMD% emergency_server.py

pause 