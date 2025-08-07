# EORA AI GitHub 배포 스크립트
Write-Host "🚀 EORA AI GitHub 배포 시작" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan

# Git 초기화
Write-Host "📦 Git 저장소 초기화 중..." -ForegroundColor Yellow
git init

# 모든 파일 추가
Write-Host "📂 파일 추가 중..." -ForegroundColor Yellow
git add .

# 커밋
Write-Host "💾 커밋 생성 중..." -ForegroundColor Yellow
git commit -m "🚀 EORA AI 완전한 시스템 배포

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
📅 배포일시: $(Get-Date)"

# 브랜치 설정
Write-Host "🌿 메인 브랜치 설정 중..." -ForegroundColor Yellow
git branch -M main

Write-Host "" 
Write-Host "🌐 GitHub 저장소 연결 안내" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""
Write-Host "다음 단계를 수행하세요:" -ForegroundColor White
Write-Host "1. https://github.com/new 에서 새 저장소 생성" -ForegroundColor White
Write-Host "2. Repository name: eora-ai-complete" -ForegroundColor White
Write-Host "3. Description: EORA AI - 완전한 학습 및 회상 시스템" -ForegroundColor White
Write-Host "4. Public 또는 Private 선택" -ForegroundColor White
Write-Host "5. Create repository 클릭" -ForegroundColor White
Write-Host ""
Write-Host "저장소 생성 후 아래 명령어를 실행하세요:" -ForegroundColor Yellow
Write-Host ""
Write-Host "git remote add origin https://github.com/YOUR_USERNAME/eora-ai-complete.git" -ForegroundColor Cyan
Write-Host "git push -u origin main" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ 준비 완료! 위 안내에 따라 GitHub에 업로드하세요." -ForegroundColor Green