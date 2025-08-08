@echo off
echo 🚀 Railway 배포 시작 - JWT/numpy 의존성 문제 해결 버전
echo.

echo 📋 현재 상태 확인...
git status

echo.
echo 🔄 변경사항 커밋...
git add .
git commit -m "🔧 JWT/numpy 의존성 문제 해결 - requirements.txt 업데이트"

echo.
echo 📤 Railway에 배포...
git push railway main

echo.
echo ✅ 배포 완료!
echo 🌐 배포된 URL: https://web-production-40c0.up.railway.app
echo.
echo 📝 해결된 문제:
echo   - PyJWT==2.8.0 추가 (JWT 토큰 인증)
echo   - numpy==1.24.3 추가 (수치 계산)
echo   - sentence-transformers==2.2.2 추가 (텍스트 임베딩)
echo   - faiss-cpu==1.7.4 추가 (벡터 검색)
echo   - pymongo==4.6.0 추가 (MongoDB 연결)
echo   - redis==5.0.1 추가 (캐싱)
echo   - websockets==12.0 추가 (실시간 통신)
echo   - psutil==5.9.6 추가 (시스템 모니터링)
echo.
echo 🔍 테스트 방법:
echo   1. https://web-production-40c0.up.railway.app/ 접속
echo   2. 관리자 페이지 접속: /admin
echo   3. 프롬프트 관리 페이지 접속: /admin/prompt-management
echo   4. 채팅 기능 테스트: /chat
echo.
pause 