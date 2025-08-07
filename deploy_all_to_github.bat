@echo off
chcp 65001 >nul 2>&1
echo.
echo ========================================
echo 🚀 EORA AI 전체 파일 GitHub 배포
echo ========================================
echo.

REM 현재 시간 저장
set TIMESTAMP=%date:~0,4%-%date:~5,2%-%date:~8,2% %time:~0,2%:%time:~3,2%
echo 📅 배포 시작: %TIMESTAMP%
echo.

REM Git 설치 확인
echo 🔍 Git 설치 확인 중...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git이 설치되지 않았습니다.
    echo 💡 Git 설치 방법:
    echo    1. https://git-scm.com/download/win 방문
    echo    2. Git for Windows 다운로드 및 설치
    echo    3. 설치 후 이 스크립트 다시 실행
    pause
    exit /b 1
) else (
    echo ✅ Git이 설치되어 있습니다.
)
echo.

REM Git 사용자 설정 확인
echo 🔧 Git 사용자 설정 확인...
git config user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Git 사용자 설정이 필요합니다.
    set /p username="GitHub 사용자명을 입력하세요: "
    set /p email="GitHub 이메일을 입력하세요: "
    git config --global user.name "%username%"
    git config --global user.email "%email%"
    echo ✅ Git 사용자 설정 완료
) else (
    echo ✅ Git 사용자 설정이 이미 완료되어 있습니다.
)
echo.

REM 현재 디렉토리 확인
echo 📁 현재 디렉토리: %~dp0
cd /d "%~dp0"
echo.

REM Git 저장소 초기화
echo 🔧 Git 저장소 초기화...
if not exist ".git" (
    git init
    echo ✅ Git 저장소가 초기화되었습니다.
) else (
    echo ✅ Git 저장소가 이미 존재합니다.
)
echo.

REM .gitignore 파일 생성/업데이트
echo 📝 .gitignore 파일 생성/업데이트...
(
echo # 환경변수 파일
echo .env
echo .env.local
echo .env.production
echo .env.development
echo
echo # Python 관련
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo *.so
echo .Python
echo build/
echo develop-eggs/
echo dist/
echo downloads/
echo eggs/
echo .eggs/
echo lib/
echo lib64/
echo parts/
echo sdist/
echo var/
echo wheels/
echo share/python-wheels/
echo *.egg-info/
echo .installed.cfg
echo *.egg
echo
echo # 로그 파일
echo *.log
echo logs/
echo chat_logs/
echo
echo # 데이터베이스 파일
echo *.db
echo *.sqlite
echo *.sqlite3
echo
echo # 시스템 파일
echo .DS_Store
echo Thumbs.db
echo desktop.ini
echo
echo # IDE 파일
echo .vscode/
echo .idea/
echo *.swp
echo *.swo
echo *~
echo
echo # 임시 파일
echo tmp/
echo temp/
echo *.tmp
echo *.bak
echo *.backup
echo
echo # Node.js 관련 (혹시 있을 경우^)
echo node_modules/
echo npm-debug.log*
echo yarn-debug.log*
echo yarn-error.log*
echo
echo # Railway 관련
echo .railway/
echo
echo # 테스트 파일
echo test_*.html
echo debug_*.py
echo quick_test_*.py
echo
echo # 압축 파일
echo *.zip
echo *.rar
echo *.7z
echo *.tar.gz
) > .gitignore
echo ✅ .gitignore 파일이 생성/업데이트되었습니다.
echo.

REM 현재 상태 확인
echo 📊 현재 Git 상태 확인...
git status
echo.

REM 원격 저장소 확인
echo 🔗 원격 저장소 확인...
git remote -v >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 원격 저장소가 이미 설정되어 있습니다:
    git remote -v
    echo.
    echo 새로운 원격 저장소를 설정하시겠습니까? (y/n^)
    set /p change_remote="선택: "
    if /i "%change_remote%"=="y" (
        git remote remove origin
        goto :SET_REMOTE
    )
) else (
    :SET_REMOTE
    echo ⚠️ 원격 저장소가 설정되지 않았습니다.
    echo.
    echo GitHub 저장소 URL을 입력하세요.
    echo 예시: https://github.com/username/repository-name.git
    set /p github_url="GitHub URL: "
    
    if "%github_url%"=="" (
        echo ❌ GitHub URL이 입력되지 않았습니다.
        echo 💡 나중에 다음 명령어로 설정할 수 있습니다:
        echo    git remote add origin YOUR_GITHUB_URL
        echo    git push -u origin main
        pause
        exit /b 1
    )
    
    git remote add origin %github_url%
    echo ✅ 원격 저장소가 설정되었습니다.
)
echo.

REM 모든 파일 추가
echo 📂 모든 파일을 Git에 추가 중...
git add .
echo ✅ 모든 파일이 Git에 추가되었습니다.
echo.

REM 추가된 파일 목록 표시
echo 📋 추가된 파일 목록:
git diff --name-only --cached
echo.

REM 커밋 메시지 입력
echo 💬 커밋 메시지를 입력하세요 (Enter만 누르면 기본 메시지 사용^):
set /p commit_msg="커밋 메시지: "
if "%commit_msg%"=="" (
    set commit_msg=회원가입 시스템 수정 완료 - Railway 환경 최적화
)

REM 커밋 생성
echo 📝 커밋 생성 중...
git commit -m "%commit_msg%"
if %errorlevel% neq 0 (
    echo ⚠️ 커밋할 변경사항이 없거나 오류가 발생했습니다.
    git status
    echo.
    echo 계속 진행하시겠습니까? (y/n^)
    set /p continue_push="선택: "
    if /i not "%continue_push%"=="y" (
        echo 배포를 중단합니다.
        pause
        exit /b 1
    )
) else (
    echo ✅ 커밋이 생성되었습니다.
)
echo.

REM 브랜치 확인 및 설정
echo 🌿 브랜치 확인...
git branch
git branch -M main
echo ✅ main 브랜치로 설정되었습니다.
echo.

REM GitHub에 푸시
echo 🚀 GitHub에 푸시 중...
echo ⚠️ 기존 코드를 덮어쓸 수 있습니다. 계속하시겠습니까? (y/n^)
set /p confirm_push="선택: "
if /i not "%confirm_push%"=="y" (
    echo 푸시를 중단합니다.
    pause
    exit /b 1
)

git push -u origin main --force
if %errorlevel% neq 0 (
    echo ❌ 푸시 중 오류가 발생했습니다.
    echo 💡 가능한 해결방법:
    echo    1. GitHub 저장소 URL이 올바른지 확인
    echo    2. GitHub 로그인 상태 확인
    echo    3. 인터넷 연결 상태 확인
    echo    4. Personal Access Token 설정 (필요시^)
    pause
    exit /b 1
) else (
    echo ✅ GitHub에 성공적으로 푸시되었습니다!
)
echo.

echo ========================================
echo 🎉 배포 완료!
echo ========================================
echo.
echo 📋 배포된 내용:
echo    • 모든 Python 파일
echo    • 설정 파일들
echo    • 템플릿 및 정적 파일들
echo    • 수정된 회원가입 시스템
echo.
echo 🔗 다음 단계:
echo    1. GitHub 저장소에서 파일 업로드 확인
echo    2. Railway 대시보드에서 자동 배포 확인
echo    3. Railway 환경변수 설정 점검
echo    4. 배포된 서비스 테스트
echo.
echo 💡 Railway 자동 배포:
echo    GitHub에 푸시하면 Railway가 자동으로 감지하여
echo    새 버전을 배포합니다. 배포 로그를 확인하세요.
echo.

pause