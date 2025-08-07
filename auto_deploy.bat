@echo off
echo ================================
echo EORA 시스템 자동 배포 시작
echo ================================

REM Git 설정: pager 비활성화
git config --global core.pager ""
git config --global --unset core.pager

echo 1. Git 상태 확인...
git status --porcelain

echo 2. 모든 파일 추가...
git add .

echo 3. 커밋 실행...
git commit -m "Deploy EORA complete system with all features"

echo 4. GitHub에 푸시...
git push origin main

echo ================================
echo 배포 완료!
echo ================================
pause