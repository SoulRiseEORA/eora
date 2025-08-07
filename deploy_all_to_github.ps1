# EORA AI 전체 파일 GitHub 배포 스크립트 (PowerShell)
param(
    [string]$CommitMessage = "회원가입 시스템 수정 완료 - Railway 환경 최적화",
    [string]$GitHubUrl = "",
    [switch]$Force = $false
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "🚀 EORA AI 전체 파일 GitHub 배포" -ForegroundColor Green  
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 현재 시간 표시
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "📅 배포 시작: $timestamp" -ForegroundColor Yellow
Write-Host ""

# Git 설치 확인
Write-Host "🔍 Git 설치 확인 중..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "✅ Git이 설치되어 있습니다: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git이 설치되지 않았습니다." -ForegroundColor Red
    Write-Host "💡 Git 설치 방법:" -ForegroundColor Cyan
    Write-Host "   1. https://git-scm.com/download/win 방문" -ForegroundColor White
    Write-Host "   2. Git for Windows 다운로드 및 설치" -ForegroundColor White
    Write-Host "   3. 설치 후 이 스크립트 다시 실행" -ForegroundColor White
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}
Write-Host ""

# Git 사용자 설정 확인
Write-Host "🔧 Git 사용자 설정 확인..." -ForegroundColor Yellow
try {
    $userName = git config user.name
    $userEmail = git config user.email
    
    if ([string]::IsNullOrEmpty($userName) -or [string]::IsNullOrEmpty($userEmail)) {
        Write-Host "⚠️ Git 사용자 설정이 필요합니다." -ForegroundColor Yellow
        
        $username = Read-Host "GitHub 사용자명을 입력하세요"
        $email = Read-Host "GitHub 이메일을 입력하세요"
        
        git config --global user.name $username
        git config --global user.email $email
        Write-Host "✅ Git 사용자 설정 완료" -ForegroundColor Green
    } else {
        Write-Host "✅ Git 사용자 설정이 이미 완료되어 있습니다." -ForegroundColor Green
        Write-Host "   사용자명: $userName" -ForegroundColor Gray
        Write-Host "   이메일: $userEmail" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️ Git 사용자 설정 확인 중 오류 발생" -ForegroundColor Yellow
}
Write-Host ""

# 현재 디렉토리 확인
Write-Host "📁 현재 디렉토리: $(Get-Location)" -ForegroundColor Yellow
Write-Host ""

# Git 저장소 초기화
Write-Host "🔧 Git 저장소 초기화..." -ForegroundColor Yellow
if (-not (Test-Path ".git")) {
    git init
    Write-Host "✅ Git 저장소가 초기화되었습니다." -ForegroundColor Green
} else {
    Write-Host "✅ Git 저장소가 이미 존재합니다." -ForegroundColor Green
}
Write-Host ""

# .gitignore 파일 생성/업데이트
Write-Host "📝 .gitignore 파일 생성/업데이트..." -ForegroundColor Yellow
$gitignoreContent = @"
# 환경변수 파일
.env
.env.local
.env.production
.env.development

# Python 관련
__pycache__/
*.py[cod]
*`$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg

# 로그 파일
*.log
logs/
chat_logs/

# 데이터베이스 파일
*.db
*.sqlite
*.sqlite3

# 시스템 파일
.DS_Store
Thumbs.db
desktop.ini

# IDE 파일
.vscode/
.idea/
*.swp
*.swo
*~

# 임시 파일
tmp/
temp/
*.tmp
*.bak
*.backup

# Node.js 관련 (혹시 있을 경우)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Railway 관련
.railway/

# 테스트 파일
test_*.html
debug_*.py
quick_test_*.py

# 압축 파일
*.zip
*.rar
*.7z
*.tar.gz
"@

$gitignoreContent | Out-File -FilePath ".gitignore" -Encoding UTF8
Write-Host "✅ .gitignore 파일이 생성/업데이트되었습니다." -ForegroundColor Green
Write-Host ""

# 현재 상태 확인
Write-Host "📊 현재 Git 상태 확인..." -ForegroundColor Yellow
git status
Write-Host ""

# 원격 저장소 확인
Write-Host "🔗 원격 저장소 확인..." -ForegroundColor Yellow
try {
    $remotes = git remote -v
    if ($remotes) {
        Write-Host "✅ 원격 저장소가 이미 설정되어 있습니다:" -ForegroundColor Green
        $remotes | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
        Write-Host ""
        
        if ([string]::IsNullOrEmpty($GitHubUrl)) {
            $changeRemote = Read-Host "새로운 원격 저장소를 설정하시겠습니까? (y/n)"
            if ($changeRemote -eq "y" -or $changeRemote -eq "Y") {
                git remote remove origin
                $GitHubUrl = Read-Host "GitHub 저장소 URL을 입력하세요 (예: https://github.com/username/repository-name.git)"
                git remote add origin $GitHubUrl
                Write-Host "✅ 원격 저장소가 변경되었습니다." -ForegroundColor Green
            }
        }
    }
} catch {
    if ([string]::IsNullOrEmpty($GitHubUrl)) {
        Write-Host "⚠️ 원격 저장소가 설정되지 않았습니다." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "GitHub 저장소 URL을 입력하세요." -ForegroundColor Cyan
        Write-Host "예시: https://github.com/username/repository-name.git" -ForegroundColor Gray
        $GitHubUrl = Read-Host "GitHub URL"
    }
    
    if ([string]::IsNullOrEmpty($GitHubUrl)) {
        Write-Host "❌ GitHub URL이 입력되지 않았습니다." -ForegroundColor Red
        Write-Host "💡 나중에 다음 명령어로 설정할 수 있습니다:" -ForegroundColor Cyan
        Write-Host "   git remote add origin YOUR_GITHUB_URL" -ForegroundColor White
        Write-Host "   git push -u origin main" -ForegroundColor White
        Read-Host "계속하려면 Enter를 누르세요"
        exit 1
    }
    
    git remote add origin $GitHubUrl
    Write-Host "✅ 원격 저장소가 설정되었습니다." -ForegroundColor Green
}
Write-Host ""

# 모든 파일 추가
Write-Host "📂 모든 파일을 Git에 추가 중..." -ForegroundColor Yellow
git add .
Write-Host "✅ 모든 파일이 Git에 추가되었습니다." -ForegroundColor Green
Write-Host ""

# 추가된 파일 목록 표시
Write-Host "📋 추가된 파일 목록:" -ForegroundColor Yellow
try {
    $addedFiles = git diff --name-only --cached
    if ($addedFiles) {
        $addedFiles | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
    } else {
        Write-Host "   (변경사항 없음)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   (파일 목록을 가져올 수 없음)" -ForegroundColor Gray
}
Write-Host ""

# 커밋 메시지 확인
if ([string]::IsNullOrEmpty($CommitMessage)) {
    $userCommitMsg = Read-Host "커밋 메시지를 입력하세요 (Enter만 누르면 기본 메시지 사용)"
    if (-not [string]::IsNullOrEmpty($userCommitMsg)) {
        $CommitMessage = $userCommitMsg
    } else {
        $CommitMessage = "회원가입 시스템 수정 완료 - Railway 환경 최적화"
    }
}

# 커밋 생성
Write-Host "📝 커밋 생성 중..." -ForegroundColor Yellow
Write-Host "   메시지: $CommitMessage" -ForegroundColor Gray
try {
    git commit -m $CommitMessage
    Write-Host "✅ 커밋이 생성되었습니다." -ForegroundColor Green
} catch {
    Write-Host "⚠️ 커밋할 변경사항이 없거나 오류가 발생했습니다." -ForegroundColor Yellow
    git status
    Write-Host ""
    
    if (-not $Force) {
        $continueChoice = Read-Host "계속 진행하시겠습니까? (y/n)"
        if ($continueChoice -ne "y" -and $continueChoice -ne "Y") {
            Write-Host "배포를 중단합니다." -ForegroundColor Yellow
            Read-Host "계속하려면 Enter를 누르세요"
            exit 1
        }
    }
}
Write-Host ""

# 브랜치 확인 및 설정
Write-Host "🌿 브랜치 설정..." -ForegroundColor Yellow
git branch
git branch -M main
Write-Host "✅ main 브랜치로 설정되었습니다." -ForegroundColor Green
Write-Host ""

# GitHub에 푸시
Write-Host "🚀 GitHub에 푸시 중..." -ForegroundColor Yellow
if (-not $Force) {
    Write-Host "⚠️ 기존 코드를 덮어쓸 수 있습니다. 계속하시겠습니까? (y/n)" -ForegroundColor Yellow
    $confirmPush = Read-Host "선택"
    if ($confirmPush -ne "y" -and $confirmPush -ne "Y") {
        Write-Host "푸시를 중단합니다." -ForegroundColor Yellow
        Read-Host "계속하려면 Enter를 누르세요"
        exit 1
    }
}

try {
    git push -u origin main --force
    Write-Host "✅ GitHub에 성공적으로 푸시되었습니다!" -ForegroundColor Green
} catch {
    Write-Host "❌ 푸시 중 오류가 발생했습니다." -ForegroundColor Red
    Write-Host "💡 가능한 해결방법:" -ForegroundColor Cyan
    Write-Host "   1. GitHub 저장소 URL이 올바른지 확인" -ForegroundColor White
    Write-Host "   2. GitHub 로그인 상태 확인" -ForegroundColor White
    Write-Host "   3. 인터넷 연결 상태 확인" -ForegroundColor White
    Write-Host "   4. Personal Access Token 설정 (필요시)" -ForegroundColor White
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "🎉 배포 완료!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "📋 배포된 내용:" -ForegroundColor Yellow
Write-Host "   • 모든 Python 파일" -ForegroundColor White
Write-Host "   • 설정 파일들" -ForegroundColor White
Write-Host "   • 템플릿 및 정적 파일들" -ForegroundColor White
Write-Host "   • 수정된 회원가입 시스템" -ForegroundColor White
Write-Host ""

Write-Host "🔗 다음 단계:" -ForegroundColor Yellow
Write-Host "   1. GitHub 저장소에서 파일 업로드 확인" -ForegroundColor White
Write-Host "   2. Railway 대시보드에서 자동 배포 확인" -ForegroundColor White
Write-Host "   3. Railway 환경변수 설정 점검" -ForegroundColor White
Write-Host "   4. 배포된 서비스 테스트" -ForegroundColor White
Write-Host ""

Write-Host "💡 Railway 자동 배포:" -ForegroundColor Cyan
Write-Host "   GitHub에 푸시하면 Railway가 자동으로 감지하여" -ForegroundColor White
Write-Host "   새 버전을 배포합니다. 배포 로그를 확인하세요." -ForegroundColor White
Write-Host ""

Read-Host "완료하려면 Enter를 누르세요"