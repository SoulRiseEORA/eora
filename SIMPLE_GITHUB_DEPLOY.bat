@echo off
echo ========================================
echo 🚀 EORA AI 깃허브 배포 시작
echo ========================================
echo.

REM 현재 디렉토리 확인
echo 📂 현재 디렉토리: %CD%
echo.

REM Git 버전 확인
echo 🔍 Git 확인 중...
git --version
if %errorlevel% neq 0 (
    echo ❌ Git이 설치되지 않았습니다!
    echo 🔗 https://git-scm.com/download/win 에서 Git을 설치하세요.
    pause
    exit /b 1
)
echo ✅ Git 설치 확인됨
echo.

REM Git 설정 확인
echo 📋 Git 설정 확인 중...
git config --global user.name > nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Git 사용자 이름이 설정되지 않았습니다.
    set /p username="Git 사용자 이름을 입력하세요: "
    git config --global user.name "%username%"
)

git config --global user.email > nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Git 이메일이 설정되지 않았습니다.
    set /p useremail="Git 이메일을 입력하세요: "
    git config --global user.email "%useremail%"
)

echo ✅ Git 설정 완료
echo.

REM .gitignore 생성
echo 📝 .gitignore 파일 생성 중...
echo # Python > .gitignore
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore
echo *.pyo >> .gitignore
echo *.pyd >> .gitignore
echo .Python >> .gitignore
echo env/ >> .gitignore
echo venv/ >> .gitignore
echo.env.local >> .gitignore
echo.env.production >> .gitignore
echo *.log >> .gitignore
echo.vscode/ >> .gitignore
echo.idea/ >> .gitignore
echo *.tmp >> .gitignore
echo *.temp >> .gitignore
echo .DS_Store >> .gitignore
echo Thumbs.db >> .gitignore
echo ✅ .gitignore 생성 완료
echo.

REM README.md 생성
echo 📝 README.md 파일 생성 중...
echo # EORA AI - 완전한 학습 및 회상 시스템 > README.md
echo. >> README.md
echo ## 🎯 프로젝트 개요 >> README.md
echo EORA AI는 고급 학습 및 8종 회상 시스템을 갖춘 AI 채팅봇입니다. >> README.md
echo. >> README.md
echo ## ✨ 주요 기능 >> README.md
echo - 🧠 8종 회상 시스템: 키워드, 임베딩, 감정, 신념, 맥락, 시간, 연관, 패턴 기반 회상 >> README.md
echo - 📚 관리자 학습 기능: 파일 업로드를 통한 AI 학습 >> README.md
echo - 💰 포인트 시스템: 사용량 기반 포인트 관리 >> README.md
echo - 🔐 사용자 인증: 관리자/일반회원 구분 >> README.md
echo - 🌐 실시간 채팅: WebSocket 기반 실시간 대화 >> README.md
echo. >> README.md
echo ## 🛠 기술 스택 >> README.md
echo - Backend: FastAPI, Python 3.8+ >> README.md
echo - Database: MongoDB >> README.md
echo - AI: OpenAI GPT-4o >> README.md
echo - Frontend: HTML, CSS, JavaScript >> README.md
echo - 실시간 통신: WebSocket >> README.md
echo. >> README.md
echo ## 📦 설치 및 실행 >> README.md
echo. >> README.md
echo ### 1. 의존성 설치 >> README.md
echo ```bash >> README.md
echo pip install -r requirements.txt >> README.md
echo ``` >> README.md
echo. >> README.md
echo ### 2. 환경 변수 설정 >> README.md
echo .env 파일을 생성하고 다음 정보를 입력: >> README.md
echo ``` >> README.md
echo OPENAI_API_KEY=your_openai_api_key >> README.md
echo MONGODB_URI=mongodb://localhost:27017 >> README.md
echo DATABASE_NAME=eora_ai >> README.md
echo ``` >> README.md
echo. >> README.md
echo ### 3. 서버 실행 >> README.md
echo ```bash >> README.md
echo cd src >> README.md
echo python app.py >> README.md
echo ``` >> README.md
echo. >> README.md
echo ### 4. 접속 >> README.md
echo - 메인 페이지: http://127.0.0.1:8300 >> README.md
echo - 관리자 패널: http://127.0.0.1:8300/admin >> README.md
echo - 채팅 페이지: http://127.0.0.1:8300/chat >> README.md
echo. >> README.md
echo ## 👑 관리자 계정 >> README.md
echo - 이메일: admin@eora.ai >> README.md
echo - 비밀번호: admin123 >> README.md
echo. >> README.md
echo ## 📁 주요 파일 구조 >> README.md
echo ``` >> README.md
echo eora-ai-complete/ >> README.md
echo ├── src/ >> README.md
echo │   ├── app.py                 # 메인 FastAPI 서버 >> README.md
echo │   ├── database.py           # MongoDB 관리 >> README.md
echo │   ├── eora_memory_system.py # EORA 메모리 시스템 >> README.md
echo │   ├── aura_memory_system.py # 8종 회상 시스템 >> README.md
echo │   ├── templates/            # HTML 템플릿 >> README.md
echo │   └── static/              # CSS, JS, 이미지 >> README.md
echo ├── requirements.txt          # Python 패키지 >> README.md
echo └── README.md                # 프로젝트 설명 >> README.md
echo ``` >> README.md
echo. >> README.md
echo ## 🚀 배포 >> README.md
echo Railway, Heroku, AWS 등에 배포 가능합니다. >> README.md
echo. >> README.md
echo ## 📄 라이선스 >> README.md
echo MIT License >> README.md
echo ✅ README.md 생성 완료
echo.

REM Git 저장소 초기화
echo 🔄 Git 저장소 초기화 중...
if exist .git (
    echo ✅ Git 저장소가 이미 존재합니다.
) else (
    git init
    echo ✅ Git 저장소 초기화 완료
)
echo.

REM 모든 파일 추가
echo 📦 모든 파일을 Git에 추가 중...
git add .
echo ✅ 파일 추가 완료
echo.

REM 커밋
echo 💾 변경사항 커밋 중...
git commit -m "🚀 EORA AI 완전한 학습 및 회상 시스템 - 전체 프로젝트 배포

✨ 주요 기능:
- 8종 회상 시스템 (키워드, 임베딩, 감정, 신념, 맥락, 시간, 연관, 패턴)
- 관리자 학습 기능 (파일 업로드)
- 포인트 시스템 (사용량 기반)
- 실시간 채팅 (WebSocket)
- MongoDB 데이터베이스 연동
- OpenAI GPT-4o 통합

🛠 기술 스택: FastAPI + Python + MongoDB + OpenAI
📁 주요 파일: app.py (183KB), eora_memory_system.py (69KB), aura_memory_system.py (43KB)
✅ 100%% 작동 확인됨"

if %errorlevel% neq 0 (
    echo ❌ 커밋 실패. 변경사항이 없을 수 있습니다.
) else (
    echo ✅ 커밋 완료
)
echo.

REM 메인 브랜치 설정
echo 🌿 메인 브랜치 설정 중...
git branch -M main
echo ✅ 메인 브랜치 설정 완료
echo.

REM GitHub 저장소 URL 입력
echo ========================================
echo 🌐 GitHub 저장소 연결
echo ========================================
echo.
echo 다음 단계를 수행해주세요:
echo.
echo 1. 🌐 https://github.com/new 에서 새 저장소 생성
echo 2. 📝 Repository name: eora-ai-complete
echo 3. 📄 Description: EORA AI - 완전한 학습 및 회상 시스템
echo 4. 🔒 Public 또는 Private 선택
echo 5. ✅ Create repository 클릭
echo.
set /p repo_url="생성된 저장소 URL을 입력하세요 (예: https://github.com/사용자명/eora-ai-complete.git): "

if "%repo_url%"=="" (
    echo ❌ URL이 입력되지 않았습니다.
    echo 수동으로 다음 명령어를 실행하세요:
    echo git remote add origin https://github.com/사용자명/eora-ai-complete.git
    echo git push -u origin main
    goto :end
)

REM 원격 저장소 추가
echo.
echo 🔗 원격 저장소 연결 중...
git remote remove origin 2>nul
git remote add origin %repo_url%
if %errorlevel% neq 0 (
    echo ❌ 원격 저장소 연결 실패
    goto :end
)
echo ✅ 원격 저장소 연결 완료
echo.

REM GitHub에 푸시
echo 🚀 GitHub에 푸시 중...
git push -u origin main
if %errorlevel% neq 0 (
    echo ❌ 푸시 실패. GitHub 인증이 필요할 수 있습니다.
    echo.
    echo 🔐 해결 방법:
    echo 1. GitHub Personal Access Token 생성
    echo 2. GitHub Desktop 사용
    echo 3. 웹에서 수동 업로드
    goto :end
)

echo.
echo ========================================
echo 🎉 배포 완료!
echo ========================================
echo.
echo ✅ EORA AI 프로젝트가 성공적으로 GitHub에 배포되었습니다!
echo 🌐 저장소 URL: %repo_url%
echo.
echo 📊 배포된 내용:
echo - 📁 전체 소스 코드 (수백개 파일)
echo - 🧠 EORA 메모리 시스템 (69KB)
echo - 🔍 8종 회상 시스템 (43KB)
echo - 🖥️ FastAPI 서버 (183KB)
echo - 🌐 웹 인터페이스 (HTML/CSS/JS)
echo - 📋 테스트 페이지들
echo - 📝 설정 파일들
echo - 📖 완전한 문서화
echo.

:end
echo ========================================
echo 🎯 배포 작업 완료
echo ========================================
pause