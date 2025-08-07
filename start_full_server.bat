@echo off
echo 🚀 EORA AI 완전 복구 서버 시작...
echo.

REM Python 프로세스 종료
taskkill /f /im python.exe >nul 2>&1
echo ✅ 기존 Python 프로세스 종료 완료

REM 포트 8011 사용 중인 프로세스 종료
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8011') do (
    taskkill /f /pid %%a >nul 2>&1
)
echo ✅ 포트 8011 정리 완료

REM Python 경로 확인
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python 발견: python
    python full_server.py
) else (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Python 발견: py
        py full_server.py
    ) else (
        echo ❌ Python을 찾을 수 없습니다.
        echo Python이 설치되어 있는지 확인하세요.
    )
)

pause 