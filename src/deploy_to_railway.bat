@echo off
echo 🚀 Railway 배포 시작 - 중복 메시지 문제 해결 버전
echo.

echo 📋 현재 상태 확인...
git status

echo.
echo 🔄 변경사항 커밋...
git add .
git commit -m "🔧 중복 메시지 저장 문제 해결 - MongoDB/메모리 중복 방지 로직 추가"

echo.
echo 📤 Railway에 배포...
git push railway main

echo.
echo ✅ 배포 완료!
echo 🌐 배포된 URL: https://web-production-40c0.up.railway.app
echo.
echo 📝 해결된 문제:
echo   - AI 답변 새로고침 시 중복 저장 방지
echo   - MongoDB 중복 메시지 체크 (30초 내)
echo   - 메모리 기반 중복 메시지 체크
echo   - 프론트엔드 중복 메시지 로드 방지
echo.
echo 🔍 테스트 방법:
echo   1. https://web-production-40c0.up.railway.app/chat 접속
echo   2. 메시지 전송 후 새로고침
echo   3. AI 답변이 중복되지 않는지 확인
echo.
pause 