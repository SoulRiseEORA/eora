# EORA AI GitHub 배포 스크립트
Write-Host "========================================" -ForegroundColor Green
Write-Host "EORA AI GitHub 배포 스크립트" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host ""

# 1. Git 설치 확인
Write-Host "1. Git 설치 확인 중..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "Git이 설치되어 있습니다: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "Git이 설치되지 않았습니다." -ForegroundColor Red
    Write-Host "Git을 다운로드하고 설치합니다..." -ForegroundColor Yellow
    Write-Host "https://git-scm.com/download/win 에서 Git을 다운로드하여 설치해주세요." -ForegroundColor Cyan
    Write-Host "설치 후 이 스크립트를 다시 실행하세요." -ForegroundColor Yellow
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}

Write-Host ""

# 2. 현재 디렉토리 확인
Write-Host "2. 현재 디렉토리 확인..." -ForegroundColor Yellow
$currentDir = Get-Location
Write-Host "현재 디렉토리: $currentDir" -ForegroundColor Green

Write-Host ""

# 3. Git 저장소 초기화
Write-Host "3. Git 저장소 초기화..." -ForegroundColor Yellow
if (-not (Test-Path ".git")) {
    git init
    Write-Host "Git 저장소가 초기화되었습니다." -ForegroundColor Green
} else {
    Write-Host "Git 저장소가 이미 존재합니다." -ForegroundColor Green
}

Write-Host ""

# 4. .gitignore 파일 확인
Write-Host "4. .gitignore 파일 확인..." -ForegroundColor Yellow
if (-not (Test-Path ".gitignore")) {
    Write-Host ".gitignore 파일이 없습니다. 생성합니다..." -ForegroundColor Yellow
    @"
# 환경변수 파일
.env
.env.local
.env.production

# Python 캐시 파일
__pycache__/
*.py[cod]
*$py.class

# 로그 파일
*.log
chat_logs/

# 시스템 파일
.DS_Store
Thumbs.db
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8
    Write-Host ".gitignore 파일이 생성되었습니다." -ForegroundColor Green
} else {
    Write-Host ".gitignore 파일이 이미 존재합니다." -ForegroundColor Green
}

Write-Host ""

# 5. 파일들을 Git에 추가
Write-Host "5. 파일들을 Git에 추가..." -ForegroundColor Yellow
git add .
Write-Host "파일들이 Git에 추가되었습니다." -ForegroundColor Green

Write-Host ""

# 6. 첫 번째 커밋 생성
Write-Host "6. 첫 번째 커밋 생성..." -ForegroundColor Yellow
git commit -m "Initial commit: EORA AI 시스템 배포"
Write-Host "커밋이 생성되었습니다." -ForegroundColor Green

Write-Host ""

# 7. GitHub 원격 저장소 설정
Write-Host "7. GitHub 원격 저장소 설정..." -ForegroundColor Yellow
$githubUrl = Read-Host "GitHub 저장소 URL을 입력하세요 (예: https://github.com/username/eora-ai.git)"

if ([string]::IsNullOrEmpty($githubUrl)) {
    Write-Host "GitHub URL이 입력되지 않았습니다." -ForegroundColor Red
    Write-Host "나중에 다음 명령어로 원격 저장소를 추가할 수 있습니다:" -ForegroundColor Yellow
    Write-Host "git remote add origin YOUR_GITHUB_URL" -ForegroundColor Cyan
    Write-Host "git push -u origin main" -ForegroundColor Cyan
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}

git remote add origin $githubUrl
Write-Host "원격 저장소가 추가되었습니다." -ForegroundColor Green

Write-Host ""

# 8. GitHub에 푸시
Write-Host "8. GitHub에 푸시..." -ForegroundColor Yellow
git branch -M main
git push -u origin main
Write-Host "GitHub에 푸시되었습니다." -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "배포 완료!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "다음 단계:" -ForegroundColor Yellow
Write-Host "1. Railway 대시보드에서 새 프로젝트 생성" -ForegroundColor Cyan
Write-Host "2. GitHub 저장소 연결" -ForegroundColor Cyan
Write-Host "3. 환경변수 설정:" -ForegroundColor Cyan
Write-Host "   - OPENAI_API_KEY" -ForegroundColor White
Write-Host "   - MONGO_URL" -ForegroundColor White
Write-Host "   - MONGO_PUBLIC_URL" -ForegroundColor White
Write-Host "   - MONGO_INITDB_ROOT_USERNAME" -ForegroundColor White
Write-Host "   - MONGO_INITDB_ROOT_PASSWORD" -ForegroundColor White
Write-Host "4. 배포 시작" -ForegroundColor Cyan
Write-Host ""

Read-Host "계속하려면 Enter를 누르세요" 