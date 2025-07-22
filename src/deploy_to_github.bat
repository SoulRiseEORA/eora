@echo off
echo 🚀 GitHub 배포 시작
echo ================================

echo 📁 현재 디렉토리: %~dp0

REM Git 초기화 및 설정
echo 🔧 Git 초기화...
git init
git config user.name "SoulRiseEORA"
git config user.email "sooasim@gmail.com"

REM GitHub 원격 저장소 설정
echo 🔗 GitHub 원격 저장소 설정...
git remote remove origin 2>nul
git remote add origin https://github.com/SoulRiseEORA/eora.git

REM 변경사항 추가 및 커밋
echo 📝 변경사항 추가 및 커밋...
git add .
git commit -m "feat: Railway MongoDB 연결 및 서버 업데이트"

REM 메인 브랜치로 푸시
echo 🚀 GitHub에 푸시...
git branch -M main
git push -u origin main --force

echo.
echo ✅ GitHub 배포 완료!
echo.
echo 📋 다음 단계:
echo 1. Railway 대시보드에서 GitHub 저장소 연결 확인
echo 2. Railway에서 자동 배포가 시작되었는지 확인
echo 3. Railway MongoDB 서비스 상태 확인
echo 4. Railway 환경변수 설정 확인

pause
