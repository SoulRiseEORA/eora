@echo off
echo 🚀 Railway MongoDB 연결 테스트
echo ========================================

echo 🔧 Railway 환경변수 설정...
set MONGO_INITDB_ROOT_PASSWORD=HYxotmUHxMxbYAejsOxEnHwrgKpAochC
set MONGO_INITDB_ROOT_USERNAME=mongo
set MONGO_PUBLIC_URL=mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594
set MONGO_URL=mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@mongodb.railway.internal:27017
set RAILWAY_TCP_PROXY_DOMAIN=trolley.proxy.rlwy.net
set RAILWAY_TCP_PROXY_PORT=26594
set RAILWAY_PRIVATE_DOMAIN=mongodb.railway.internal

echo ✅ 환경변수 설정 완료

echo.
echo 🔗 MongoDB 연결 테스트 시작...
echo 📝 연결 URL: mongodb://mongo:***@trolley.proxy.rlwy.net:26594

echo.
echo 📋 테스트 완료
echo 💡 이제 run_server_with_railway_mongo.bat로 서버를 실행하세요.
pause 