@echo off
echo 🚀 회상 시스템 오류 수정 및 테스트 개선 배포
echo.

echo 📋 현재 상태 확인...
git status

echo.
echo 🔄 변경사항 커밋...
git add .
git commit -m "🔧 회상 시스템 오류 수정 및 테스트 개선 - API 오류 처리 강화, 기본 회상 시뮬레이션 추가"

echo.
echo 📤 GitHub에 배포...
git push origin main

echo.
echo ✅ 배포 완료!
echo 🌐 Railway 자동 배포 URL: https://web-production-40c0.up.railway.app
echo.

echo 📝 해결된 문제들:
echo   - 회상 API 500 오류 수정
echo   - 메모리 통계 API 오류 처리 개선
echo   - 기본 회상 시뮬레이션 추가
echo   - 키워드 기반 회상 기능 구현
echo   - 오류 로깅 및 디버깅 정보 추가
echo.

echo 🔍 배포 후 확인:
echo   1. Railway 대시보드에서 배포 상태 확인
echo   2. 회상 API 정상 작동 확인
echo   3. 메모리 통계 API 정상 작동 확인
echo   4. 고급 회상 시스템 테스트 재실행
echo   5. 채팅에서 EORA 프롬프트 정상 적용 확인
echo.

echo 🧪 테스트 실행 방법:
echo   cd src
echo   python test_recall_system.py
echo.

echo 🎯 예상 개선 결과:
echo   - 회상 API 500 오류 해결
echo   - 메모리 통계 정상 조회
echo   - 키워드 기반 회상 작동
echo   - EORA 프롬프트 정상 적용
echo   - 고급 회상 시스템 테스트 통과
echo.

pause 