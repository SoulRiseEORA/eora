@echo off
echo 🚀 EORA AI System 간단 배포 스크립트
echo ======================================

echo 📂 현재 디렉토리: %CD%
echo.

echo 🔍 Git 상태 확인...
git status
echo.

echo 📦 변경사항 추가...
git add .
echo.

echo 💾 커밋 생성...
git commit -m "배포 업데이트: 최종 수정사항 적용"
echo.

echo 🚀 GitHub에 푸시...
git push origin main
echo.

echo ✅ 배포 완료!
echo 🌐 Railway에서 자동 배포가 진행됩니다.
echo ⏰ 배포 완료까지 2-3분 정도 소요됩니다.
echo.

echo 📋 배포 후 확인사항:
echo 1. Railway 대시보드에서 배포 상태 확인
echo 2. /health 엔드포인트로 헬스체크 확인
echo 3. 환경변수 설정 확인
echo.

pause 