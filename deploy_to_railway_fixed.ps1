Write-Host "🚀 Railway 배포 시작 - JWT/numpy 의존성 문제 해결 버전" -ForegroundColor Green
Write-Host ""

Write-Host "📋 현재 상태 확인..." -ForegroundColor Yellow
git status

Write-Host ""
Write-Host "🔄 변경사항 커밋..." -ForegroundColor Yellow
git add .
git commit -m "🔧 JWT/numpy 의존성 문제 해결 - requirements.txt 업데이트"

Write-Host ""
Write-Host "📤 Railway에 배포..." -ForegroundColor Yellow
git push railway main

Write-Host ""
Write-Host "✅ 배포 완료!" -ForegroundColor Green
Write-Host "🌐 배포된 URL: https://web-production-40c0.up.railway.app" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 해결된 문제:" -ForegroundColor Yellow
Write-Host "  - PyJWT==2.8.0 추가 (JWT 토큰 인증)" -ForegroundColor White
Write-Host "  - numpy==1.24.3 추가 (수치 계산)" -ForegroundColor White
Write-Host "  - sentence-transformers==2.2.2 추가 (텍스트 임베딩)" -ForegroundColor White
Write-Host "  - faiss-cpu==1.7.4 추가 (벡터 검색)" -ForegroundColor White
Write-Host "  - pymongo==4.6.0 추가 (MongoDB 연결)" -ForegroundColor White
Write-Host "  - redis==5.0.1 추가 (캐싱)" -ForegroundColor White
Write-Host "  - websockets==12.0 추가 (실시간 통신)" -ForegroundColor White
Write-Host "  - psutil==5.9.6 추가 (시스템 모니터링)" -ForegroundColor White
Write-Host ""
Write-Host "🔍 테스트 방법:" -ForegroundColor Yellow
Write-Host "  1. https://web-production-40c0.up.railway.app/ 접속" -ForegroundColor White
Write-Host "  2. 관리자 페이지 접속: /admin" -ForegroundColor White
Write-Host "  3. 프롬프트 관리 페이지 접속: /admin/prompt-management" -ForegroundColor White
Write-Host "  4. 채팅 기능 테스트: /chat" -ForegroundColor White
Write-Host ""

Read-Host "엔터를 눌러 종료" 