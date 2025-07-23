@echo off
echo 🚀 Railway 세션 생성 및 관리자 페이지 접근 문제 해결 배포
echo.

echo 📋 현재 상태 확인...
git status

echo.
echo 🔄 변경사항 커밋...
git add .
git commit -m "🔧 Railway 세션 생성 및 관리자 페이지 접근 문제 해결 - 임시 사용자 인증 추가"

echo.
echo 📤 Railway에 배포...
git push origin main

echo.
echo ✅ 배포 완료!
echo 🌐 배포된 URL: https://web-production-40c0.up.railway.app
echo.
echo 📝 해결된 문제:
echo   - 세션 생성 시 사용자 인증 문제 해결
echo   - 관리자 페이지 접근 문제 해결
echo   - 레일웨이 환경에서 임시 사용자/관리자 계정 생성
echo   - MongoDB 연결 실패 시 메모리 fallback 개선
echo.
echo 🔍 배포 후 확인:
echo   1. Railway 대시보드에서 배포 상태 확인
echo   2. 로그에서 "✅ 관리자 계정 자동 생성 성공" 메시지 확인
echo   3. https://web-production-40c0.up.railway.app 접속 테스트
echo   4. 새 세션 생성 테스트
echo   5. 관리자 페이지: /admin 접속 테스트
echo.
pause 