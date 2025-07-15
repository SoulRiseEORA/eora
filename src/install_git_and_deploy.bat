@echo off
echo ========================================
echo EORA AI GitHub 배포 스크립트
echo ========================================

echo.
echo 1. Git 설치 확인 중...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git이 설치되지 않았습니다.
    echo Git을 다운로드하고 설치합니다...
    echo https://git-scm.com/download/win 에서 Git을 다운로드하여 설치해주세요.
    echo 설치 후 이 스크립트를 다시 실행하세요.
    pause
    exit /b 1
) else (
    echo Git이 이미 설치되어 있습니다.
)

echo.
echo 2. 현재 디렉토리 확인...
cd /d "%~dp0"
echo 현재 디렉토리: %CD%

echo.
echo 3. Git 저장소 초기화...
if not exist ".git" (
    git init
    echo Git 저장소가 초기화되었습니다.
) else (
    echo Git 저장소가 이미 존재합니다.
)

echo.
echo 4. .gitignore 파일 생성...
if not exist ".gitignore" (
    echo .env > .gitignore
    echo __pycache__/ >> .gitignore
    echo *.pyc >> .gitignore
    echo .DS_Store >> .gitignore
    echo .vscode/ >> .gitignore
    echo node_modules/ >> .gitignore
    echo chat_logs/ >> .gitignore
    echo *.log >> .gitignore
    echo .gitignore 파일이 생성되었습니다.
) else (
    echo .gitignore 파일이 이미 존재합니다.
)

echo.
echo 5. 파일들을 Git에 추가...
git add .

echo.
echo 6. 첫 번째 커밋 생성...
git commit -m "Initial commit: EORA AI 시스템 배포"

echo.
echo 7. GitHub 원격 저장소 설정...
echo GitHub 저장소 URL을 입력하세요 (예: https://github.com/username/eora-ai.git):
set /p github_url="GitHub URL: "

if "%github_url%"=="" (
    echo GitHub URL이 입력되지 않았습니다.
    echo 나중에 다음 명령어로 원격 저장소를 추가할 수 있습니다:
    echo git remote add origin YOUR_GITHUB_URL
    echo git push -u origin main
    pause
    exit /b 1
)

git remote add origin %github_url%

echo.
echo 8. GitHub에 푸시...
git branch -M main
git push -u origin main

echo.
echo ========================================
echo 배포 완료!
echo ========================================
echo.
echo 다음 단계:
echo 1. Railway 대시보드에서 새 프로젝트 생성
echo 2. GitHub 저장소 연결
echo 3. 환경변수 설정:
echo    - OPENAI_API_KEY
echo    - MONGO_URL
echo    - MONGO_PUBLIC_URL
echo    - MONGO_INITDB_ROOT_USERNAME
echo    - MONGO_INITDB_ROOT_PASSWORD
echo 4. 배포 시작
echo.
pause 