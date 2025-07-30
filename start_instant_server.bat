@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    🚀 EORA AI 즉시 실행 서버
echo ========================================
echo.

REM 기존 Python 프로세스 종료
echo 🔄 기존 서버 종료 중...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im py.exe >nul 2>&1
timeout /t 2 >nul

REM 포트 8013 정리
echo 🧹 포트 8013 정리 중...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8013') do (
    taskkill /f /pid %%a >nul 2>&1
)
timeout /t 1 >nul

REM Python 경로 확인
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python 발견: python
    echo.
    echo 🚀 서버 시작 중...
    python instant_server.py
) else (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Python 발견: py
        echo.
        echo 🚀 서버 시작 중...
        py instant_server.py
    ) else (
        echo ❌ Python을 찾을 수 없습니다.
        echo Python이 설치되어 있는지 확인하세요.
    )
)

pause 