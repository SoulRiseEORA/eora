@echo off
echo 🚀 Railway 최종 배포 - JWT/numpy 의존성 완전 해결
echo.

echo 📋 현재 상태 확인...
git status

echo.
echo 🔄 변경사항 커밋...
git add .
git commit -m "🔧 Railway 배포 최종 수정 - nixpacks.toml 업데이트 및 의존성 완전 해결"

echo.
echo 📤 Railway에 배포...
git push origin main

echo.
echo ✅ 배포 완료!
echo 🌐 배포된 URL: https://web-production-40c0.up.railway.app
echo.
echo 📝 해결된 문제:
echo   - nixpacks.toml 업데이트 (Python 3.12, gcc 추가)
echo   - railway_requirements_fixed.txt 생성
echo   - PyJWT==2.8.0 명시적 설치
echo   - numpy==1.24.3 명시적 설치
echo   - 모든 의존성 버전 고정
echo.
echo 🔍 배포 후 확인:
echo   1. Railway 대시보드에서 배포 상태 확인
echo   2. 로그에서 "✅ EORA AI System 시작 완료" 메시지 확인
echo   3. https://web-production-40c0.up.railway.app 접속 테스트
echo   4. 관리자 페이지: /admin 접속 테스트
echo.
pause 