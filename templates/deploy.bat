@echo off
setlocal enabledelayedexpansion

echo 🚀 EORA AI System 배포를 시작합니다...
echo ======================================

echo 📂 현재 디렉토리: %CD%
echo.

echo 🔍 Git 상태 확인...
git status
if !errorlevel! neq 0 (
    echo ❌ Git 상태 확인 실패
    echo 🔧 Git이 설치되어 있고 현재 디렉토리가 Git 저장소인지 확인하세요.
    pause
    exit /b 1
)
echo.

echo 📦 변경사항 추가...
git add .
if !errorlevel! neq 0 (
    echo ❌ 변경사항 추가 실패
    pause
    exit /b 1
)
echo.

echo 💾 커밋 생성...
git commit -m "배포 업데이트: 서버 안정성 개선 및 재시작 문제 해결"
if !errorlevel! neq 0 (
    echo ❌ 커밋 생성 실패
    echo 🔧 변경사항이 있는지 확인하세요.
    pause
    exit /b 1
)
echo.

echo 🚀 GitHub에 푸시...
git push origin main
if !errorlevel! neq 0 (
    echo ❌ GitHub 푸시 실패
    echo 🔧 GitHub 인증과 원격 저장소 설정을 확인하세요.
    pause
    exit /b 1
)
echo.

echo ✅ 배포 완료!
echo 🌐 Railway에서 자동 배포가 진행됩니다.
echo ⏰ 배포 완료까지 2-3분 정도 소요됩니다.
echo.

echo 📋 배포 후 확인사항:
echo 1. Railway 대시보드에서 배포 상태 확인
echo 2. /health 엔드포인트로 헬스체크 확인
echo 3. 환경변수 설정 확인
echo 4. 로그에서 오류 메시지 확인
echo.

echo 🎉 모든 작업이 완료되었습니다!
echo.
echo 💡 문제가 발생하면 Railway 로그를 확인하세요.
pause 