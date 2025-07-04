@echo off
echo 🚀 Railway 환경변수 설정
echo ================================

echo.
echo 🔧 Railway 대시보드에서 다음 정보들을 확인하세요:
echo.
echo 1. MONGO_INITDB_ROOT_PASSWORD
echo 2. MONGO_INITDB_ROOT_USERNAME  
echo 3. RAILWAY_TCP_PROXY_DOMAIN
echo 4. RAILWAY_TCP_PROXY_PORT
echo 5. RAILWAY_PRIVATE_DOMAIN
echo.

echo 📝 아래에 실제 값들을 입력하세요:
echo.

set /p MONGO_INITDB_ROOT_PASSWORD="MONGO_INITDB_ROOT_PASSWORD: "
set /p MONGO_INITDB_ROOT_USERNAME="MONGO_INITDB_ROOT_USERNAME: "
set /p RAILWAY_TCP_PROXY_DOMAIN="RAILWAY_TCP_PROXY_DOMAIN: "
set /p RAILWAY_TCP_PROXY_PORT="RAILWAY_TCP_PROXY_PORT: "
set /p RAILWAY_PRIVATE_DOMAIN="RAILWAY_PRIVATE_DOMAIN: "

echo.
echo ✅ 환경변수 설정 완료
echo.

echo 🔍 설정된 환경변수 확인:
echo MONGO_INITDB_ROOT_PASSWORD: %MONGO_INITDB_ROOT_PASSWORD%
echo MONGO_INITDB_ROOT_USERNAME: %MONGO_INITDB_ROOT_USERNAME%
echo RAILWAY_TCP_PROXY_DOMAIN: %RAILWAY_TCP_PROXY_DOMAIN%
echo RAILWAY_TCP_PROXY_PORT: %RAILWAY_TCP_PROXY_PORT%
echo RAILWAY_PRIVATE_DOMAIN: %RAILWAY_PRIVATE_DOMAIN%

echo.
echo 🔗 MongoDB 연결 테스트 시작...
python setup_railway_mongo.py

echo.
echo 📋 설정 완료
pause 