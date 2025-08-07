@echo off
setlocal

:: 사용자 설정 - 아래 두 줄을 꼭 수정하세요
set "REPO_URL=https://github.com/SoulRiseEORA/eora.git"
set "COMMIT_MSG=최초 커밋"

:: 1. 기존 .git 폴더 삭제
echo 삭제 중: .git 폴더...
rmdir /s /q .git

:: 2. 새 Git 저장소 초기화
echo Git 저장소 초기화 중...
git init

:: 3. 원격 저장소(origin) 등록
echo 원격 저장소 등록 중...
git remote add origin %REPO_URL%

:: 4. 브랜치명 main으로 변경
git branch -M main

:: 5. 전체 파일 추가
git add .

:: 6. 커밋
git commit -m "%COMMIT_MSG%"

:: 7. 강제 푸시
echo GitHub로 푸시 중...
git push -u origin main --force

echo 완료되었습니다!
pause
