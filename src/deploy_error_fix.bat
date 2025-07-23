@echo off
echo 🚀 에러 수정 및 GitHub 배포
echo.

echo 📋 현재 상태 확인...
git status

echo.
echo 🔄 변경사항 커밋...
git add .
git commit -m "🔧 에러 수정: 토큰 계산 오류, huggingface-hub 호환성, langchain_community 추가"

echo.
echo 📤 GitHub에 배포...
git push origin main

echo.
echo ✅ 배포 완료!
echo 🌐 Railway 자동 배포 URL: https://web-production-40c0.up.railway.app
echo.

echo 📝 수정된 문제들:
echo   - ❌ 토큰 계산 오류: name 'user_message' is not defined 해결
echo   - huggingface-hub 버전 호환성 문제 해결 (0.19.4 → 0.16.4)
echo   - langchain_community 모듈 추가 (0.0.10)
echo   - 파일 끝 잘못된 코드 제거
echo.

echo 🔍 배포 후 확인:
echo   1. Railway 대시보드에서 배포 상태 확인
echo   2. 로그에서 에러 메시지 사라짐 확인
echo   3. 토큰 계산 정상 작동 확인
echo   4. EORA 고급 채팅 시스템 로드 확인
echo.

pause 