@echo off
echo ========================================
echo EORA AI System Git 배포 시작
echo ========================================

cd /d E:\AI_Dev_Tool\src

echo 현재 디렉토리: %CD%

echo.
echo 1. Git 상태 확인...
git status

echo.
echo 2. 변경사항 추가...
git add .

echo.
echo 3. 커밋 생성...
git commit -m "Stable: EORA AI system deployment fixes and improvements"

echo.
echo 4. 원격 저장소로 푸시...
git push

echo.
echo ========================================
echo Git 배포 완료
echo ========================================

pause 