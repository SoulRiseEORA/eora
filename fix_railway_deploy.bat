@echo off
chcp 65001 >nul
echo 🔧 Railway 배포 문제 해결 스크립트
echo ================================================

echo.
echo 📋 문제 해결 단계:
echo 1. Nixpacks 설정 파일 생성
echo 2. Procfile 수정
echo 3. Railway 설정 파일 생성
echo 4. GitHub에 푸시
echo 5. Railway 재배포
echo.

echo 🔍 현재 파일 상태 확인...
echo.
echo 📄 Procfile 내용:
type Procfile
echo.
echo 📄 .nixpacks/config.toml 내용:
type .nixpacks\config.toml
echo.
echo 📄 railway.json 내용:
type railway.json
echo.

echo 📤 GitHub에 푸시하시겠습니까? (y/n)
set /p choice=

if /i "%choice%"=="y" (
    echo.
    echo 📤 GitHub에 푸시 중...
    git add .
    git commit -m "🔧 Railway 배포 문제 해결 - Nixpacks 설정 개선"
    git push origin main
    
    echo.
    echo ✅ 푸시 완료!
    echo.
    echo 🔧 Railway에서 해야 할 일:
    echo 1. Railway 대시보드 접속
    echo 2. 프로젝트 선택
    echo 3. Deployments 탭에서 최신 배포 확인
    echo 4. 로그에서 빌드 성공 여부 확인
    echo 5. 환경변수 설정 확인 (OPENAI_API_KEY)
    echo.
    echo 📖 자세한 가이드: RAILWAY_SETUP_GUIDE.md
) else (
    echo ❌ 푸시가 취소되었습니다.
)

echo.
pause 