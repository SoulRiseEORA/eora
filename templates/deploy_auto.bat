@echo off
echo ========================================
echo EORA AI System 자동 배포 스크립트
echo ========================================

:: 환경변수 설정
set OPENAI_API_KEY=sk-your-openai-api-key-here
set MONGODB_URL=mongodb://your-mongodb-url
set REDIS_URL=redis://your-redis-url
set JWT_SECRET=your-jwt-secret-key

:: Git 상태 확인
echo [1/5] Git 상태 확인 중...
git status
if %errorlevel% neq 0 (
    echo Git이 설치되지 않았거나 초기화되지 않았습니다.
    pause
    exit /b 1
)

:: 변경사항 커밋
echo [2/5] 변경사항 커밋 중...
git add .
git commit -m "Auto deploy: %date% %time%"
if %errorlevel% neq 0 (
    echo 커밋 실패. 변경사항이 없을 수 있습니다.
)

:: GitHub에 푸시
echo [3/5] GitHub에 푸시 중...
git push origin main
if %errorlevel% neq 0 (
    echo 푸시 실패. GitHub 설정을 확인하세요.
    pause
    exit /b 1
)

:: 로컬 서버 시작 (선택사항)
echo [4/5] 로컬 서버 시작 중...
echo 로컬 서버를 시작하시겠습니까? (y/n)
set /p choice=
if /i "%choice%"=="y" (
    echo 서버 시작 중...
    python -m uvicorn main:app --host 0.0.0.0 --port 8016
)

echo [5/5] 배포 완료!
echo GitHub Actions를 통해 자동 배포가 진행됩니다.
echo https://github.com/yourusername/eora-ai-system/actions 에서 배포 상태를 확인하세요.
pause 