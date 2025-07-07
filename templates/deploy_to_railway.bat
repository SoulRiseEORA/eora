@echo off
echo 🚀 Railway 배포 준비 중...
echo.

REM Git 상태 확인
echo 📊 Git 상태 확인...
git status

echo.
echo 📝 변경사항 추가 중...
git add .

echo.
echo 💬 커밋 메시지 입력 중...
git commit -m "🔧 Railway 최적화 완료 - 모든 오류 해결"

echo.
echo 🚀 GitHub에 푸시 중...
git push origin main

echo.
echo ✅ 배포 완료!
echo 🌐 Railway에서 자동 배포가 시작됩니다.
echo 📋 Railway 대시보드에서 배포 상태를 확인하세요.
echo.
pause 