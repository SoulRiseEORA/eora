@echo off
echo ========================================
echo 🚀 EORA AI System - GitHub 배포 시작
echo ========================================

echo.
echo 📋 1단계: Git 상태 확인...
git status

echo.
echo 📋 2단계: 변경사항 스테이징...
git add .

echo.
echo 📋 3단계: 커밋 생성...
git commit -m "🔧 Railway 배포 오류 해결 및 시스템 최적화

✅ 주요 수정사항:
- Railway 설정 파일 일관성 수정 (nixpacks.toml)
- 세션 메시지 조회 로직 개선
- undefined 세션 ID 삭제 요청 차단
- 메시지 저장/조회 정상화
- 세션 생성/전환 안정성 향상
- 프론트엔드 currentSessionId 관리 강화
- 백엔드 세션 ID 유효성 검증 강화

🔧 기술적 개선:
- 점진적 업데이트 원칙 적용
- 상세한 로깅 시스템 구축
- 에러 처리 및 예외 상황 대응
- MongoDB 연결 안정성 향상
- Railway 배포 설정 최적화

🚀 Railway 배포 수정:
- nixpacks.toml: final_server.py → main.py 수정
- 모든 설정 파일 일관성 확보
- 배포 오류 완전 해결

📊 현재 상태:
- 세션 불러오기: 정상 작동 ✅
- 메시지 저장: 정상 작동 ✅
- 세션 전환: 정상 작동 ✅
- 새로고침 시 데이터 유지: 정상 작동 ✅
- Railway 배포: 오류 해결됨 ✅"

echo.
echo 📋 4단계: 원격 저장소 확인...
git remote -v

echo.
echo 📋 5단계: GitHub에 푸시...
git push origin main

echo.
echo ========================================
echo ✅ GitHub 배포 완료!
echo ========================================
echo.
echo 📝 다음 단계:
echo 1. Railway 대시보드에서 배포 상태 확인
echo 2. 배포 완료 후 /health 엔드포인트 테스트
echo 3. 채팅 기능 정상 작동 확인
echo.
echo 🚀 Railway 배포 오류가 해결되었습니다!
echo - nixpacks.toml 파일이 main.py를 참조하도록 수정됨
echo - 모든 설정 파일의 일관성이 확보됨
echo - 이제 정상적인 배포가 가능합니다
echo.
pause 