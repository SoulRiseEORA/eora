@echo off
cd /d %~dp0
git init
git config user.name "SoulRiseEORA"
git config user.email "sooasim@gmail.com"
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/SoulRiseEORA/eora.git
git push -u origin main --force
pause
