@echo off
echo 🚀 Railway 서버 테스트 시작
echo ================================================

echo 🔧 환경변수 확인 중...
echo MONGO_PUBLIC_URL: %MONGO_PUBLIC_URL%
echo MONGO_URL: %MONGO_URL%
echo MONGO_INITDB_ROOT_PASSWORD: %MONGO_INITDB_ROOT_PASSWORD%
echo MONGO_INITDB_ROOT_USERNAME: %MONGO_INITDB_ROOT_USERNAME%

echo.
echo 🚀 final_server.py 실행 중...
python final_server.py

pause 