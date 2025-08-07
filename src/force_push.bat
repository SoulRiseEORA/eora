@echo off
cd /d %~dp0
git rm -r --cached .
git add .
git commit -m "♻️ 전체 파일 재추적 및 강제 푸시"
git push -u origin main --force
pause