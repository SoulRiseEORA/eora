@echo off
REM EORA AI System - Windows 배치 파일
REM Railway 최종 배포 버전 v2.0.0

echo 🚀 EORA AI System 시작 중...

REM 현재 디렉토리 확인
echo 📁 현재 디렉토리: %CD%

REM src 디렉토리 확인
if exist "src" (
    echo ✅ src 디렉토리 발견
) else (
    echo ❌ src 디렉토리를 찾을 수 없습니다
    pause
    exit /b 1
)

REM 환경변수 확인
if defined OPENAI_API_KEY (
    echo ✅ OpenAI API 키 설정됨
) else (
    echo ⚠️ OpenAI API 키가 설정되지 않았습니다
)

REM 포트 확인
if defined PORT (
    set PORT_NUM=%PORT%
) else (
    set PORT_NUM=8001
)
echo 🔧 서버 포트: %PORT_NUM%

REM 서버 시작
echo 🚀 FastAPI 서버 시작 중...
echo 📡 서버 주소: http://127.0.0.1:%PORT_NUM%

REM uvicorn으로 서버 시작 (src.app 모듈 경로 사용)
python -m uvicorn src.app:app --host 127.0.0.1 --port %PORT_NUM% --reload

REM 오류 발생 시 대체 포트 시도
if errorlevel 1 (
    echo ❌ 포트 %PORT_NUM% 실패, 대체 포트 시도 중...
    
    for %%p in (8002 8003 8004 8005) do (
        echo 🔄 포트 %%p 시도 중...
        python -m uvicorn src.app:app --host 127.0.0.1 --port %%p --reload
        if not errorlevel 1 goto :success
    )
    
    echo ❌ 모든 포트 시도 실패
    pause
    exit /b 1
)

:success
echo ✅ 서버 시작 완료
pause 