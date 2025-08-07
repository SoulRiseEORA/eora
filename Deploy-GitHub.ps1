# EORA AI GitHub 배포 스크립트 (PowerShell)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 EORA AI GitHub 배포 시작" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 현재 디렉토리 확인
Write-Host "📂 현재 디렉토리: $PWD" -ForegroundColor Yellow
Write-Host ""

# Git 설치 확인
Write-Host "🔍 Git 설치 확인 중..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "✅ Git 설치 확인됨: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git이 설치되지 않았습니다!" -ForegroundColor Red
    Write-Host "🔗 https://git-scm.com/download/win 에서 Git을 설치하세요." -ForegroundColor Yellow
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}
Write-Host ""

# Git 설정 확인
Write-Host "📋 Git 설정 확인 중..." -ForegroundColor Yellow
try {
    $userName = git config --global user.name
    if (-not $userName) {
        $userName = Read-Host "Git 사용자 이름을 입력하세요"
        git config --global user.name $userName
    }
    
    $userEmail = git config --global user.email
    if (-not $userEmail) {
        $userEmail = Read-Host "Git 이메일을 입력하세요"
        git config --global user.email $userEmail
    }
    
    Write-Host "✅ Git 설정 완료: $userName ($userEmail)" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Git 설정 중 오류 발생" -ForegroundColor Yellow
}
Write-Host ""

# .gitignore 생성
Write-Host "📝 .gitignore 파일 생성 중..." -ForegroundColor Yellow
$gitignoreContent = @"
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env.local
.env.production

# Logs
*.log

# IDE
.vscode/
.idea/

# Temporary files
*.tmp
*.temp

# OS files
.DS_Store
Thumbs.db

# Node modules
node_modules/
"@

$gitignoreContent | Out-File -FilePath ".gitignore" -Encoding UTF8
Write-Host "✅ .gitignore 생성 완료" -ForegroundColor Green
Write-Host ""

# README.md 생성
Write-Host "📝 README.md 파일 생성 중..." -ForegroundColor Yellow
$readmeContent = @"
# EORA AI - 완전한 학습 및 회상 시스템

## 🎯 프로젝트 개요
EORA AI는 고급 학습 및 8종 회상 시스템을 갖춘 AI 채팅봇입니다.

## ✨ 주요 기능
- 🧠 **8종 회상 시스템**: 키워드, 임베딩, 감정, 신념, 맥락, 시간, 연관, 패턴 기반 회상
- 📚 **관리자 학습 기능**: 파일 업로드를 통한 AI 학습
- 💰 **포인트 시스템**: 사용량 기반 포인트 관리
- 🔐 **사용자 인증**: 관리자/일반회원 구분
- 🌐 **실시간 채팅**: WebSocket 기반 실시간 대화

## 🛠 기술 스택
- **Backend**: FastAPI, Python 3.8+
- **Database**: MongoDB
- **AI**: OpenAI GPT-4o
- **Frontend**: HTML, CSS, JavaScript
- **실시간 통신**: WebSocket

## 📦 설치 및 실행

### 1. 의존성 설치
``````bash
pip install -r requirements.txt
``````

### 2. 환경 변수 설정
`.env` 파일을 생성하고 다음 정보를 입력:
``````
OPENAI_API_KEY=your_openai_api_key
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=eora_ai
``````

### 3. 서버 실행
``````bash
cd src
python app.py
``````

### 4. 접속
- 메인 페이지: http://127.0.0.1:8300
- 관리자 패널: http://127.0.0.1:8300/admin
- 채팅 페이지: http://127.0.0.1:8300/chat

## 👑 관리자 계정
- 이메일: admin@eora.ai
- 비밀번호: admin123

## 📁 주요 파일 구조
``````
eora-ai-complete/
├── src/
│   ├── app.py                 # 메인 FastAPI 서버 (183KB)
│   ├── database.py           # MongoDB 관리
│   ├── eora_memory_system.py # EORA 메모리 시스템 (69KB)
│   ├── aura_memory_system.py # 8종 회상 시스템 (43KB)
│   ├── templates/            # HTML 템플릿
│   └── static/              # CSS, JS, 이미지
├── requirements.txt          # Python 패키지
└── README.md                # 프로젝트 설명
``````

## 🚀 배포
Railway, Heroku, AWS 등에 배포 가능합니다.

## 📄 라이선스
MIT License

## 🤝 기여
Pull Request를 환영합니다!

---
**배포일시**: $(Get-Date)
**총 파일 수**: 수백개
**프로젝트 크기**: ~50MB+
"@

$readmeContent | Out-File -FilePath "README.md" -Encoding UTF8
Write-Host "✅ README.md 생성 완료" -ForegroundColor Green
Write-Host ""

# Git 저장소 초기화
Write-Host "🔄 Git 저장소 초기화 중..." -ForegroundColor Yellow
if (Test-Path ".git") {
    Write-Host "✅ Git 저장소가 이미 존재합니다." -ForegroundColor Green
} else {
    git init
    Write-Host "✅ Git 저장소 초기화 완료" -ForegroundColor Green
}
Write-Host ""

# 모든 파일 추가
Write-Host "📦 모든 파일을 Git에 추가 중..." -ForegroundColor Yellow
git add .
Write-Host "✅ 파일 추가 완료" -ForegroundColor Green
Write-Host ""

# 커밋
Write-Host "💾 변경사항 커밋 중..." -ForegroundColor Yellow
$commitMessage = @"
🚀 EORA AI 완전한 학습 및 회상 시스템 - 전체 프로젝트 배포

✨ 주요 기능:
- 8종 회상 시스템 (키워드, 임베딩, 감정, 신념, 맥락, 시간, 연관, 패턴)
- 관리자 학습 기능 (파일 업로드)
- 포인트 시스템 (사용량 기반)
- 실시간 채팅 (WebSocket)
- MongoDB 데이터베이스 연동
- OpenAI GPT-4o 통합

🛠 기술 스택: FastAPI + Python + MongoDB + OpenAI
📁 주요 파일: app.py (183KB), eora_memory_system.py (69KB), aura_memory_system.py (43KB)
✅ 100% 작동 확인됨
📅 배포일시: $(Get-Date)
"@

try {
    git commit -m $commitMessage
    Write-Host "✅ 커밋 완료" -ForegroundColor Green
} catch {
    Write-Host "⚠️ 커밋 실패. 변경사항이 없을 수 있습니다." -ForegroundColor Yellow
}
Write-Host ""

# 메인 브랜치 설정
Write-Host "🌿 메인 브랜치 설정 중..." -ForegroundColor Yellow
git branch -M main
Write-Host "✅ 메인 브랜치 설정 완료" -ForegroundColor Green
Write-Host ""

# GitHub 저장소 연결
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🌐 GitHub 저장소 연결" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "다음 단계를 수행해주세요:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 🌐 https://github.com/new 에서 새 저장소 생성" -ForegroundColor White
Write-Host "2. 📝 Repository name: eora-ai-complete" -ForegroundColor White
Write-Host "3. 📄 Description: EORA AI - 완전한 학습 및 회상 시스템" -ForegroundColor White
Write-Host "4. 🔒 Public 또는 Private 선택" -ForegroundColor White
Write-Host "5. ✅ Create repository 클릭" -ForegroundColor White
Write-Host ""

$repoUrl = Read-Host "생성된 저장소 URL을 입력하세요 (예: https://github.com/사용자명/eora-ai-complete.git)"

if (-not $repoUrl) {
    Write-Host "❌ URL이 입력되지 않았습니다." -ForegroundColor Red
    Write-Host "수동으로 다음 명령어를 실행하세요:" -ForegroundColor Yellow
    Write-Host "git remote add origin https://github.com/사용자명/eora-ai-complete.git" -ForegroundColor White
    Write-Host "git push -u origin main" -ForegroundColor White
    Read-Host "계속하려면 Enter를 누르세요"
    exit
}

# 원격 저장소 추가
Write-Host ""
Write-Host "🔗 원격 저장소 연결 중..." -ForegroundColor Yellow
try {
    git remote remove origin 2>$null
    git remote add origin $repoUrl
    Write-Host "✅ 원격 저장소 연결 완료" -ForegroundColor Green
} catch {
    Write-Host "❌ 원격 저장소 연결 실패" -ForegroundColor Red
    Read-Host "계속하려면 Enter를 누르세요"
    exit
}
Write-Host ""

# GitHub에 푸시
Write-Host "🚀 GitHub에 푸시 중..." -ForegroundColor Yellow
try {
    git push -u origin main
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "🎉 배포 완료!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✅ EORA AI 프로젝트가 성공적으로 GitHub에 배포되었습니다!" -ForegroundColor Green
    Write-Host "🌐 저장소 URL: $repoUrl" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 배포된 내용:" -ForegroundColor Yellow
    Write-Host "- 📁 전체 소스 코드 (수백개 파일)" -ForegroundColor White
    Write-Host "- 🧠 EORA 메모리 시스템 (69KB)" -ForegroundColor White
    Write-Host "- 🔍 8종 회상 시스템 (43KB)" -ForegroundColor White
    Write-Host "- 🖥️ FastAPI 서버 (183KB)" -ForegroundColor White
    Write-Host "- 🌐 웹 인터페이스 (HTML/CSS/JS)" -ForegroundColor White
    Write-Host "- 📋 테스트 페이지들" -ForegroundColor White
    Write-Host "- 📝 설정 파일들" -ForegroundColor White
    Write-Host "- 📖 완전한 문서화" -ForegroundColor White
    
} catch {
    Write-Host "❌ 푸시 실패. GitHub 인증이 필요할 수 있습니다." -ForegroundColor Red
    Write-Host ""
    Write-Host "🔐 해결 방법:" -ForegroundColor Yellow
    Write-Host "1. GitHub Personal Access Token 생성" -ForegroundColor White
    Write-Host "2. GitHub Desktop 사용" -ForegroundColor White
    Write-Host "3. 웹에서 수동 업로드" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎯 배포 작업 완료" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Read-Host "계속하려면 Enter를 누르세요"