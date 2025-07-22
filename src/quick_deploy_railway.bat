@echo off
echo 🚀 Railway 빠른 배포
git add .
git commit -m "🔧 의존성 업데이트"
git push railway main
echo ✅ 배포 완료!
pause 