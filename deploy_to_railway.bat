@echo off
chcp 65001 >nul
echo 🚀 EORA AI Railway 배포 스크립트
echo ================================================

echo.
echo 📋 배포 전 체크리스트:
echo 1. Railway 환경변수 설정 확인
echo 2. GitHub에 코드 푸시
echo 3. Railway 자동 배포 확인
echo.

echo 🔍 현재 상태 확인...
git status

echo.
echo 📤 GitHub에 푸시하시겠습니까? (y/n)
set /p choice=

if /i "%choice%"=="y" (
    echo.
    echo 📤 GitHub에 푸시 중...
    git add .
    git commit -m "🚀 Railway 배포 준비 - OpenAI API 키 설정 개선"
    git push origin main
    
    echo.
    echo ✅ 푸시 완료!
    echo.
    echo 🔧 Railway 환경변수 설정 확인:
    echo 1. Railway 대시보드 접속
    echo 2. 프로젝트 선택
    echo 3. Service > Variables 탭
    echo 4. OPENAI_API_KEY 설정 확인
    echo.
    echo 📖 자세한 가이드: RAILWAY_SETUP_GUIDE.md
) else (
    echo ❌ 푸시가 취소되었습니다.
)

echo.
pause 