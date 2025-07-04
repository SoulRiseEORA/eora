@echo off
echo 🚀 EORA AI 서버 시작 (Railway MongoDB 연결)
echo ================================================

echo 🔧 Railway 환경변수 설정...
set MONGO_INITDB_ROOT_PASSWORD=HYxotmUHxMxbYAejsOxEnHwrgKpAochC
set MONGO_INITDB_ROOT_USERNAME=mongo
set MONGO_PUBLIC_URL=mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594
set MONGO_URL=mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@mongodb.railway.internal:27017
set RAILWAY_TCP_PROXY_DOMAIN=trolley.proxy.rlwy.net
set RAILWAY_TCP_PROXY_PORT=26594
set RAILWAY_PRIVATE_DOMAIN=mongodb.railway.internal

echo 🔍 Railway 환경변수 확인 중...
echo MONGO_INITDB_ROOT_PASSWORD: %MONGO_INITDB_ROOT_PASSWORD%
echo MONGO_INITDB_ROOT_USERNAME: %MONGO_INITDB_ROOT_USERNAME%
echo RAILWAY_TCP_PROXY_DOMAIN: %RAILWAY_TCP_PROXY_DOMAIN%
echo RAILWAY_TCP_PROXY_PORT: %RAILWAY_TCP_PROXY_PORT%
echo RAILWAY_PRIVATE_DOMAIN: %RAILWAY_PRIVATE_DOMAIN%

echo.
echo ✅ Railway MongoDB 연결 정보가 설정되었습니다.

echo.
echo 🔗 서버 시작 (포트 8010)...
echo    만약 포트 충돌이 발생하면 다른 포트를 사용하세요.
python final_server.py

echo.
echo 📋 서버 종료
pause 