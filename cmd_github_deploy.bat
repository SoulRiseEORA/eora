@echo off
chcp 65001 > nul
echo.
echo ========================================
echo 🚀 EORA AI GitHub CMD 배포 스크립트
echo ========================================
echo.

REM 현재 디렉토리 확인
echo 📂 현재 작업 디렉토리: %CD%
echo.

REM Git 설치 확인
echo 🔍 Git 설치 상태 확인 중...
git --version > nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Git이 설치되어 있습니다.
) else (
    echo ❌ Git이 설치되지 않았습니다. 
    echo    다운로드: https://git-scm.com/downloads
    echo    설치 후 이 스크립트를 다시 실행해주세요.
    pause
    exit /b 1
)
echo.

REM 기존 .git 폴더 삭제 (새로운 시작을 위해)
if exist ".git" (
    echo 🗑️ 기존 .git 폴더를 삭제합니다...
    rmdir /s /q ".git"
    echo ✅ .git 폴더 삭제 완료.
)
echo.

REM Git 저장소 초기화
echo 🔄 Git 저장소 초기화 중...
git init
if %errorlevel% neq 0 (
    echo ❌ Git 저장소 초기화 실패.
    pause
    exit /b 1
)
echo ✅ Git 저장소 초기화 완료.
echo.

REM Git 사용자 정보 설정 (필요한 경우)
echo 📋 Git 사용자 정보 확인 중...
for /f "tokens=*" %%i in ('git config --global user.name 2^>nul') do set git_name=%%i
for /f "tokens=*" %%i in ('git config --global user.email 2^>nul') do set git_email=%%i

if "%git_name%"=="" (
    echo ⚠️ Git 사용자 이름이 설정되지 않았습니다.
    set /p git_name="Git 사용자 이름을 입력하세요 (예: YourGitHubUsername): "
    git config --global user.name "%git_name%"
)

if "%git_email%"=="" (
    echo ⚠️ Git 이메일이 설정되지 않았습니다.
    set /p git_email="Git 이메일을 입력하세요 (예: your.email@example.com): "
    git config --global user.email "%git_email%"
)

echo ✅ Git 사용자: %git_name% (%git_email%)
echo.

REM .gitignore 파일 생성
echo 📝 .gitignore 파일 생성 중...
(
    echo .env
    echo __pycache__/
    echo *.pyc
    echo *.log
    echo data/
    echo venv/
    echo .vscode/
    echo *.db
    echo *.sqlite3
    echo *.json
    echo *.bak
    echo *.tmp
    echo *.swp
    echo *.swo
    echo *.DS_Store
    echo npm-debug.log*
    echo yarn-debug.log*
    echo yarn-error.log*
    echo .pytest_cache/
    echo .mypy_cache/
    echo .ruff_cache/
    echo .venv/
    echo build/
    echo dist/
    echo *.egg-info/
    echo *.so
    echo *.pyd
    echo *.dll
    echo *.exe
    echo *.out
    echo *.test
    echo *.prof
    echo *.ipynb_checkpoints
    echo .history/
    echo .git/
    echo *.bat
    echo *.ps1
) > .gitignore
echo ✅ .gitignore 파일 생성 완료.
echo.

REM README.md 파일 생성
echo 📝 README.md 파일 생성 중...
(
    echo # EORA AI - 완전한 학습 및 회상 시스템
    echo.
    echo EORA AI는 고급 학습 및 회상 기능을 갖춘 인공지능 시스템입니다.
    echo.
    echo ## 주요 기능
    echo - 8종 회상 시스템
    echo - 관리자 학습 기능  
    echo - 포인트 시스템
    echo - 실시간 채팅
    echo - 강력한 보안
    echo.
    echo ## 설치 및 실행
    echo ```bash
    echo pip install -r requirements.txt
    echo cd src
    echo python app.py
    echo ```
    echo.
    echo ## 접속 정보
    echo - 서버: http://127.0.0.1:8300
    echo - 관리자: admin@eora.ai / admin123
    echo.
    echo ---
    echo © 2024 EORA AI. All rights reserved.
) > README.md
echo ✅ README.md 파일 생성 완료.
echo.

REM 모든 파일 추가
echo ➕ 모든 파일을 Git에 추가 중...
git add .
if %errorlevel% neq 0 (
    echo ❌ 모든 파일 추가 실패.
    pause
    exit /b 1
)
echo ✅ 모든 파일 추가 완료.
echo.

REM 커밋 생성
echo 📝 커밋 생성 중...
git commit -m "🚀 EORA AI 완전한 시스템 배포"
if %errorlevel% neq 0 (
    echo ⚠️ 커밋 실패. 변경 사항이 없거나 Git 사용자 정보가 올바르지 않을 수 있습니다.
    pause
    exit /b 1
)
echo ✅ 커밋 생성 완료.
echo.

REM 메인 브랜치 설정
echo 🌿 메인 브랜치 설정 중...
git branch -M main
if %errorlevel% neq 0 (
    echo ❌ 메인 브랜치 설정 실패.
    pause
    exit /b 1
)
echo ✅ 메인 브랜치 설정 완료.
echo.

REM GitHub 저장소 URL 입력 요청
set /p github_repo_url="GitHub 저장소 URL을 입력하세요 (예: https://github.com/YOUR_USERNAME/your-repo-name.git): "
echo.

REM 원격 저장소 연결
echo 🔗 원격 저장소 연결 중...
git remote remove origin > nul 2>&1
git remote add origin %github_repo_url%
if %errorlevel% neq 0 (
    echo ❌ 원격 저장소 연결 실패. URL을 확인하세요.
    pause
    exit /b 1
)
echo ✅ 원격 저장소 연결 완료.
echo.

REM GitHub에 푸시
echo 📤 GitHub에 푸시 중...
echo    (GitHub 사용자 이름과 비밀번호/Personal Access Token을 입력하라는 메시지가 나타날 수 있습니다.)
git push -u origin main
if %errorlevel% neq 0 (
    echo ❌ GitHub 푸시 실패. 다음을 확인하세요:
    echo    1. GitHub 저장소 URL이 올바른지.
    echo    2. GitHub 사용자 이름과 비밀번호/Personal Access Token이 올바른지.
    echo    3. 저장소에 대한 쓰기 권한이 있는지.
    pause
    exit /b 1
)
echo.
echo ========================================
echo 🎉 GitHub 배포 완료!
echo    이제 GitHub 저장소에서 파일을 확인하실 수 있습니다.
echo    URL: %github_repo_url%
echo ========================================
echo.
pause
exit /b 0