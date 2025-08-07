@echo off
chcp 65001
echo 📦 필요한 패키지 설치 중...
echo.

echo 1. uvicorn 설치:
pip install uvicorn
echo.

echo 2. fastapi 설치:
pip install fastapi
echo.

echo 3. python-multipart 설치:
pip install python-multipart
echo.

echo 4. jinja2 설치:
pip install jinja2
echo.

echo 5. python-jose[cryptography] 설치:
pip install python-jose[cryptography]
echo.

echo 6. PyJWT 설치:
pip install PyJWT
echo.

echo ✅ 설치 완료
echo.
echo 이제 서버를 시작할 수 있습니다:
echo start_server_simple.bat
pause 