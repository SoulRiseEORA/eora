@echo off
echo =============================
echo 🔧 Git 시크릿 제거 자동화 시작
echo =============================

REM 1. OpenAI 키 제거 (src/app.py가 존재할 경우)
IF EXIST src\app.py (
    echo 👉 src\app.py에서 OpenAI API 키 제거 중...
    powershell -Command "(Get-Content src/app.py) -replace 'sk-[a-zA-Z0-9]{20,}', 'os.getenv(\"OPENAI_API_KEY\")' | Set-Content src/app.py"
)

REM 2. git-filter-repo 설치 여부 확인
echo 👉 git-filter-repo 설치 확인 중...
where git-filter-repo >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ git-filter-repo가 설치되지 않았습니다.
    echo ▶ Python 설치 후, 아래 명령으로 설치하세요:
    echo     pip install git-filter-repo
    pause
    exit /b
)

REM 3. 교체할 문자열 등록
echo 👉 민감 문자열 대체 파일 작성...
echo sk-==REMOVED_KEY>replacements.txt

REM 4. 과거 커밋 기록에서 제거
echo 👉 커밋 기록에서 시크릿 제거 중...
git filter-repo --replace-text replacements.txt

REM 5. GitHub로 푸시
echo 👉 GitHub로 푸시 중...
git push origin main --force

echo =============================
echo ✅ 완료: 시크릿 제거 및 푸시 성공
echo =============================
pause
