@echo off
echo 🚀 EORA AI 서버 시작 (환경변수 설정)
echo ==================================================
echo 🔧 Railway 환경변수 설정 중...

REM Railway 환경변수 설정 (실제 값으로 변경하세요)
set OPENAI_API_KEY=sk-your-openai-api-key-here

REM MongoDB 환경변수 (Railway에서 제공하는 값)
set MONGO_INITDB_ROOT_PASSWORD=your-mongo-password
set MONGO_INITDB_ROOT_USERNAME=mongo
set MONGO_PUBLIC_URL=mongodb://mongo:password@trolley.proxy.rlwy.net:26594
set MONGO_URL=mongodb://mongo:password@mongodb.railway.internal:27017
set RAILWAY_TCP_PROXY_DOMAIN=trolley.proxy.rlwy.net
set RAILWAY_TCP_PROXY_PORT=26594
set RAILWAY_PRIVATE_DOMAIN=mongodb.railway.internal

echo 📍 서버 주소: http://localhost:8011
echo 🔐 관리자 계정: admin@eora.ai / admin1234
echo ==================================================

REM 서버 실행
python final_server.py

pause 