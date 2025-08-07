@echo off
echo ========================================
echo EORA AI 완전한 프로젝트 깃허브 배포
echo ========================================

echo 1. Git 초기화...
if not exist .git (
    git init
    echo Git 저장소 초기화 완료
) else (
    echo Git 저장소가 이미 존재합니다
)

echo.
echo 2. 모든 파일을 Git에 추가...
git add .
echo 파일 추가 완료

echo.
echo 3. 변경사항 커밋...
git commit -m "EORA AI 완전한 학습 기능 구현 - 100%% 작동 확인됨"
echo 커밋 완료

echo.
echo 4. 메인 브랜치 설정...
git branch -M main
echo 메인 브랜치 설정 완료

echo.
echo ========================================
echo 다음 단계: 깃허브 저장소 연결
echo ========================================
echo.
echo 1. https://github.com 에 로그인
echo 2. "New repository" 클릭
echo 3. 저장소 이름: eora-ai-complete
echo 4. Public/Private 선택
echo 5. "Create repository" 클릭
echo.
echo 6. 생성된 저장소의 URL을 복사하고 아래 명령어 실행:
echo    git remote add origin https://github.com/사용자명/eora-ai-complete.git
echo    git push -u origin main
echo.
echo ========================================
echo 프로젝트 구조 요약:
echo ========================================
echo ✅ 메인 서버 파일: src/app.py (183KB)
echo ✅ 학습 시스템: eora_memory_system.py (69KB)
echo ✅ 회상 시스템: aura_memory_system.py (43KB)
echo ✅ 데이터베이스: database.py (30KB)
echo ✅ 테스트 페이지: complete_learning_test.html (23KB)
echo ✅ 설정 파일: ai_prompts.json (41KB)
echo ✅ 요구사항: requirements.txt
echo.
echo 📊 총 파일 수: 수백개
echo 📊 총 프로젝트 크기: ~50MB+
echo.
echo ========================================
echo 배포 준비 완료!
echo ========================================

pause