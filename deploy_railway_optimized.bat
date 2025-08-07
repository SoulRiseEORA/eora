@echo off
echo ======================================
echo Railway 성능 최적화 배포 스크립트
echo ======================================

echo 🚀 Git 상태 확인...
git status

echo 📦 변경사항 스테이징...
git add .

echo 💾 커밋 생성...
git commit -m "🚀 Railway 성능 최적화 적용 - MongoDB 연결 최적화, 캐싱 시스템 개선, 비동기 처리 최적화"

echo 🚂 Railway 배포...
git push railway main

echo ✅ 배포 완료!
echo 📊 성능 모니터링: https://web-production-40c0.up.railway.app/api/status
echo 🔧 관리자 페이지: https://web-production-40c0.up.railway.app/admin

pause 