@echo off
echo 🚀 Railway 간단 배포 - 최소 의존성으로 안정 배포
echo.

echo 📋 현재 상태 확인...
git status

echo.
echo 🔄 변경사항 커밋...
git add .
git commit -m "🔧 Railway 간단 배포 - 최소 의존성으로 안정화"

echo.
echo 📤 Railway에 배포...
git push origin main

echo.
echo ✅ 배포 완료!
echo 🌐 배포된 URL: https://web-production-40c0.up.railway.app
echo.
echo 📝 변경 사항:
echo   - nixpacks.toml 제거 (Railway 기본 설정 사용)
echo   - Procfile 직접 uvicorn 명령어 사용
echo   - requirements.txt 최소 의존성으로 단순화
echo   - PyJWT==2.8.0 포함
echo.
echo 🔍 배포 후 확인:
echo   1. Railway 대시보드에서 배포 상태 확인
echo   2. 로그에서 "✅ EORA AI System 시작 완료" 메시지 확인
echo   3. https://web-production-40c0.up.railway.app 접속 테스트
echo.
pause 