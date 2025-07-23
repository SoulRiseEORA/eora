@echo off
echo 🚀 프롬프트 전달 문제 해결 및 고급 회상 시스템 테스트 배포
echo.

echo 📋 현재 상태 확인...
git status

echo.
echo 🔄 변경사항 커밋...
git add .
git commit -m "🔧 프롬프트 전달 문제 해결 및 고급 회상 시스템 테스트 추가 - ai_prompts.json 구조에 맞게 수정"

echo.
echo 📤 GitHub에 배포...
git push origin main

echo.
echo ✅ 배포 완료!
echo 🌐 Railway 자동 배포 URL: https://web-production-40c0.up.railway.app
echo.

echo 📝 해결된 문제들:
echo   - ai_prompts.json 구조에 맞게 프롬프트 로딩 수정
echo   - system + role + guide + format 조합으로 프롬프트 구성
echo   - 고급 회상 시스템 테스트 스크립트 추가
echo   - 프롬프트 통합 테스트 기능 추가
echo   - 메모리 회상 기능 종합 테스트
echo.

echo 🔍 배포 후 확인:
echo   1. Railway 대시보드에서 배포 상태 확인
echo   2. 로그에서 "✅ ai_prompts.json의 ai1 프롬프트 적용" 메시지 확인
echo   3. 채팅에서 EORA 관련 키워드 확인
echo   4. 고급 회상 시스템 테스트 실행: python test_recall_system.py
echo   5. 메모리 회상 기능 정상 작동 확인
echo.

echo 🧪 테스트 실행 방법:
echo   cd src
echo   python test_recall_system.py
echo.

pause 