@echo off
echo 🚀 EORA AI 배포 스크립트 시작
echo.

echo 📂 현재 디렉토리 확인...
cd /d "%~dp0"
echo 현재 위치: %CD%
echo.

echo 🔄 Git 상태 확인...
git status
echo.

echo 📦 변경사항 추가...
git add .
echo.

echo 💾 커밋 생성...
git commit -m "Remove Redis dependency and optimize deployment configuration"
echo.

echo 🚀 GitHub에 푸시...
git push origin main
echo.

echo ✅ 배포 준비 완료!
echo.

echo 📋 다음 단계:
echo 1. Railway.com에서 프로젝트 확인
echo 2. 환경 변수 설정 확인
echo 3. 배포 상태 모니터링
echo.

echo 🔧 주요 수정사항:
echo - Redis 의존성 제거로 배포 안정성 향상
echo - 포트 환경 변수 지원 추가
echo - 서버 타임아웃 설정 최적화
echo.

echo 🌐 접속 주소: https://your-app-name.railway.app
echo.

pause 