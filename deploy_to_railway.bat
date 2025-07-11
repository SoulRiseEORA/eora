@echo off
echo 🚀 Railway 배포 시작...

echo 📦 Git 상태 확인...
git status

echo 🔄 변경사항 커밋...
git add .
git commit -m "Railway 배포 업데이트 - home.html 및 환경변수 설정"

echo 🚀 Railway에 푸시...
git push railway main

echo ✅ Railway 배포 완료!
echo 🌐 배포 URL: https://web-production-40c0.up.railway.app/
echo 📝 환경변수 설정 필요: OPENAI_API_KEY
pause 