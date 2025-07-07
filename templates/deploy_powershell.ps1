# PowerShell 배포 스크립트
# Railway 배포 전용

Write-Host "🚀 Railway 배포를 시작합니다..." -ForegroundColor Green

# 1. 현재 상태 확인
Write-Host "📋 현재 상태 확인 중..." -ForegroundColor Yellow
git status

# 2. 변경사항 커밋
Write-Host "💾 변경사항 커밋 중..." -ForegroundColor Yellow
git add .
git commit -m "Railway 배포 최적화 - PowerShell 호환성 개선"

# 3. Railway 배포
Write-Host "🚀 Railway에 배포 중..." -ForegroundColor Yellow
railway up

Write-Host "✅ 배포 완료!" -ForegroundColor Green
Write-Host "🌐 배포 URL: https://your-app-name.railway.app" -ForegroundColor Cyan 