@echo off
echo 🚀 세션 자동 생성 방지 및 관리자 페이지 연결 문제 해결 배포
echo.

echo 📋 현재 상태 확인...
git status

echo.
echo 🔄 변경사항 커밋...
git add .
git commit -m "🔧 세션 자동 생성 방지 및 관리자 페이지 연결 수정 - 사용자 수동 세션 생성으로 변경"

echo.
echo 📤 Railway에 배포...
git push origin main

echo.
echo ✅ 배포 완료!
echo 🌐 배포된 URL: https://web-production-40c0.up.railway.app
echo.
echo 📝 해결된 문제:
echo   - 채팅 시작 시 자동 세션 생성 방지
echo   - 홈페이지에서 자동 세션 생성 방지
echo   - 관리자 페이지 프롬프트 관리 링크 수정
echo   - 사용자 수동 세션 생성으로 변경
echo.
echo 🔍 배포 후 확인:
echo   1. Railway 대시보드에서 배포 상태 확인
echo   2. 홈페이지에서 채팅 시작 시 자동 세션 생성 안됨 확인
echo   3. 채팅 페이지에서 "새 세션" 버튼으로 수동 생성 확인
echo   4. 관리자 페이지: /admin 접속 후 프롬프트 관리 링크 확인
echo.
pause 