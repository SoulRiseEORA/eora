@echo off
echo 🚀 Railway 배포 준비 시작
echo ================================================

echo 📝 Git 상태 확인...
git status

echo.
echo 📤 변경사항 커밋...
git add .
git commit -m "🚀 Railway 배포 준비 - 환경변수 자동 수정 및 안정화"

echo.
echo 📤 GitHub에 푸시...
git push origin main

echo.
echo ✅ Railway 배포 준비 완료!
echo 📋 다음 단계:
echo 1. Railway 대시보드에서 자동 배포 확인
echo 2. 환경변수가 올바르게 설정되었는지 확인
echo 3. 서버 로그에서 MongoDB 연결 상태 확인

pause 