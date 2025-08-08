@echo off
echo 🚂 Railway 빠른 상태 확인
echo ================================

REM 실제 Railway URL로 변경하세요
set RAILWAY_URL=https://www.eora.life

echo 📍 메인 페이지 확인 중...
curl -s -o nul -w "메인 페이지: %%{http_code} (%%{time_total}ms)\n" %RAILWAY_URL%/

echo 📍 헬스 체크 확인 중...
curl -s -o nul -w "헬스 체크: %%{http_code} (%%{time_total}ms)\n" %RAILWAY_URL%/health

echo 📍 API 문서 확인 중...
curl -s -o nul -w "API 문서: %%{http_code} (%%{time_total}ms)\n" %RAILWAY_URL%/docs

echo ================================
echo 💡 실제 Railway URL로 RAILWAY_URL을 변경하세요!
pause 