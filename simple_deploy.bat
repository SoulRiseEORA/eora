@echo off
echo 🚀 EORA AI 간단 배포 시작
echo ========================

REM 기존 git 폴더 삭제
if exist ".git" rmdir /s /q .git

REM Git 초기화
git init
git branch -M main

REM 파일 추가 및 커밋
git add .
git commit -m "EORA AI 전체 프로젝트 배포"

echo ✅ Git 준비 완료!
echo.
echo 다음 명령어로 GitHub에 업로드하세요:
echo git remote add origin https://github.com/사용자명/eora-ai-complete.git
echo git push -u origin main
echo.
pause