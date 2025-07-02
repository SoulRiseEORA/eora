@echo off
cd /d %~dp0\backend

REM Git 초기화 및 설정
git init
git config user.name "SoulRiseEORA"
git config user.email "sooasim@gmail.com"

REM GitHub 원격 저장소 설정
git remote remove origin 2>nul
git remote add origin https://github.com/SoulRiseEORA/eora.git

REM 변경사항 추가 및 커밋
git add .
git commit -m "fix: update FastAPI with correct template structure"
git branch -M main
git push -u origin main --force

pause
