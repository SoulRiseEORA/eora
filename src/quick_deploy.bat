@echo off
echo ========================================
echo EORA AI 빠른 배포 스크립트
echo ========================================

echo.
echo 1. Git 설치 확인...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git이 설치되지 않았습니다.
    echo 📥 https://git-scm.com/download/win 에서 Git을 다운로드하여 설치해주세요.
    echo.
    echo 설치 후 이 스크립트를 다시 실행하세요.
    pause
    exit /b 1
) else (
    echo ✅ Git이 설치되어 있습니다.
)

echo.
echo 2. Git 저장소 초기화...
if not exist ".git" (
    git init
    echo ✅ Git 저장소가 초기화되었습니다.
) else (
    echo ✅ Git 저장소가 이미 존재합니다.
)

echo.
echo 3. 파일들을 Git에 추가...
git add .
echo ✅ 파일들이 Git에 추가되었습니다.

echo.
echo 4. 커밋 생성...
git commit -m "EORA AI 시스템 배포" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ 커밋 실패. Git 사용자 정보를 설정해야 합니다.
    echo.
    echo 다음 명령어로 사용자 정보를 설정하세요:
    echo git config --global user.name "Your Name"
    echo git config --global user.email "your.email@example.com"
    echo.
    echo 설정 후 이 스크립트를 다시 실행하세요.
    pause
    exit /b 1
) else (
    echo ✅ 커밋이 생성되었습니다.
)

echo.
echo 5. GitHub 저장소 URL 입력...
set /p github_url="GitHub 저장소 URL을 입력하세요: "

if "%github_url%"=="" (
    echo ❌ GitHub URL이 입력되지 않았습니다.
    echo.
    echo GitHub에서 새 저장소를 만들고 URL을 복사해주세요.
    echo 예: https://github.com/username/eora-ai.git
    pause
    exit /b 1
)

echo.
echo 6. 원격 저장소 연결...
git remote add origin %github_url% 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ 원격 저장소가 이미 존재합니다.
    git remote set-url origin %github_url%
    echo ✅ 원격 저장소 URL이 업데이트되었습니다.
) else (
    echo ✅ 원격 저장소가 연결되었습니다.
)

echo.
echo 7. GitHub에 푸시...
git branch -M main
git push -u origin main
if %errorlevel% neq 0 (
    echo ❌ 푸시 실패. GitHub 인증이 필요합니다.
    echo.
    echo GitHub에서 Personal Access Token을 생성하고 사용하세요.
    echo 또는 GitHub Desktop을 사용하여 푸시하세요.
    pause
    exit /b 1
) else (
    echo ✅ GitHub에 푸시되었습니다.
)

echo.
echo ========================================
echo 🎉 배포 완료!
echo ========================================
echo.
echo 다음 단계:
echo 1. Railway.app에서 새 프로젝트 생성
echo 2. GitHub 저장소 연결
echo 3. 환경변수 설정 (OPENAI_API_KEY, MongoDB 등)
echo 4. 배포 시작
echo.
echo 자세한 가이드는 GITHUB_DEPLOY_STEPS.md 파일을 참조하세요.
echo.
pause 