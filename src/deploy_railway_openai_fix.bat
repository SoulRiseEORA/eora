@echo off
echo 🚀 Railway OpenAI 모듈 문제 해결 배포
echo.

echo 📋 현재 상태 확인...
git status

echo.
echo 🔄 변경사항 커밋...
git add .
git commit -m "🔧 OpenAI 모듈 문제 해결 - requirements.txt 업데이트 및 ImportError 처리 개선"

echo.
echo 📤 Railway에 배포...
git push origin main

echo.
echo ✅ 배포 완료!
echo 🌐 배포된 URL: https://web-production-40c0.up.railway.app
echo.
echo 📝 해결된 문제:
echo   - openai==1.3.7 버전 명시적 설치
echo   - huggingface-hub==0.19.4 버전 고정
echo   - transformers==4.35.2 버전 고정
echo   - ImportError 예외 처리 개선
echo   - OpenAI 모듈 없을 때 안전한 처리
echo.
echo 🔍 배포 후 확인:
echo   1. Railway 대시보드에서 배포 상태 확인
echo   2. 로그에서 "✅ OpenAI API 키 설정 성공" 메시지 확인
echo   3. https://web-production-40c0.up.railway.app 접속 테스트
echo   4. 채팅 기능 정상 작동 확인
echo.
pause 