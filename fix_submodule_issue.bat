@echo off
chcp 65001 > nul
echo.
echo ========================================
echo 🔧 서브모듈 문제 해결 스크립트
echo ========================================
echo.

REM 현재 디렉토리 확인
echo 📂 현재 작업 디렉토리: %CD%
echo.

REM src 폴더의 .git 확인
if exist "src\.git" (
    echo 🔍 src 폴더에서 .git 발견!
    echo 🗑️ src\.git 폴더를 삭제합니다...
    rmdir /s /q "src\.git"
    echo ✅ src\.git 폴더 삭제 완료
) else (
    echo ✅ src 폴더에 .git 없음
)
echo.

REM 다른 하위 폴더의 .git도 확인
echo 🔍 모든 하위 폴더의 .git 검색 중...
for /r . %%i in (.git) do (
    if exist "%%i" (
        echo 🗑️ 발견된 .git 삭제: %%i
        rmdir /s /q "%%i" 2>nul
    )
)
echo ✅ 모든 하위 .git 폴더 정리 완료
echo.

REM 기존 루트 .git 폴더 삭제
if exist ".git" (
    echo 🗑️ 기존 루트 .git 폴더를 삭제합니다...
    rmdir /s /q ".git"
    echo ✅ 루트 .git 폴더 삭제 완료
)
echo.

REM Git 저장소 재초기화
echo 🔄 Git 저장소 재초기화 중...
git init
if %errorlevel% neq 0 (
    echo ❌ Git 초기화 실패
    pause
    exit /b 1
)
echo ✅ Git 저장소 재초기화 완료
echo.

REM .gitignore 생성
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
    echo .pytest_cache/
    echo .mypy_cache/
    echo .ruff_cache/
    echo .venv/
    echo build/
    echo dist/
    echo *.egg-info/
    echo .history/
    echo *.bat
    echo *.ps1
) > .gitignore
echo ✅ .gitignore 파일 생성 완료
echo.

REM 모든 파일 추가
echo ➕ 모든 파일을 Git에 추가 중...
git add .
if %errorlevel% neq 0 (
    echo ❌ 파일 추가 실패
    pause
    exit /b 1
)
echo ✅ 모든 파일 추가 완료
echo.

REM 상태 확인
echo 📊 Git 상태 확인:
git status --porcelain | findstr "^A" | wc -l
echo 개의 파일이 추가됨
echo.

REM 커밋
echo 📝 커밋 생성 중...
git commit -m "🚀 서브모듈 문제 해결 후 전체 프로젝트 배포"
if %errorlevel% neq 0 (
    echo ❌ 커밋 실패
    pause
    exit /b 1
)
echo ✅ 커밋 생성 완료
echo.

echo ========================================
echo 🎉 서브모듈 문제 해결 완료!
echo    이제 GitHub에 푸시할 수 있습니다.
echo ========================================
echo.
echo 다음 명령어로 GitHub에 푸시하세요:
echo git remote add origin YOUR_REPO_URL
echo git push -u origin main
echo.
pause