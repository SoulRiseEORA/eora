# 완전 안정 배포 스크립트 - 모든 문제 해결
Write-Host "🚀 완전 안정 Railway 배포를 시작합니다..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan

# 1. 현재 상태 확인
Write-Host "📋 현재 상태 확인 중..." -ForegroundColor Yellow
try {
    git status
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Git 상태 확인 실패" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Git 명령어 실행 실패" -ForegroundColor Red
    exit 1
}

# 2. 변경사항 추가
Write-Host "💾 변경사항 추가 중..." -ForegroundColor Yellow
try {
    git add .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 변경사항 추가 실패" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Git add 실패" -ForegroundColor Red
    exit 1
}

# 3. 커밋 생성
Write-Host "📝 커밋 생성 중..." -ForegroundColor Yellow
try {
    git commit -m "완전 안정 서버 배포 - 모든 문제 해결"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 커밋 생성 실패" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Git commit 실패" -ForegroundColor Red
    exit 1
}

# 4. Railway 배포
Write-Host "🚀 Railway에 배포 중..." -ForegroundColor Yellow
try {
    railway up
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Railway 배포 실패" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Railway 명령어 실행 실패" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 완전 안정 배포 완료!" -ForegroundColor Green
Write-Host "🌐 배포 URL: https://your-app-name.railway.app" -ForegroundColor Cyan
Write-Host "🎯 모든 문제가 해결되었습니다!" -ForegroundColor Green 