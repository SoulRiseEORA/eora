@echo off
chcp 65001
echo 🔍 Python 설치 상태 확인 중...
echo.

echo 1. Python 버전 확인:
python --version
echo.

echo 2. Python 경로 확인:
where python
echo.

echo 3. pip 버전 확인:
pip --version
echo.

echo 4. uvicorn 설치 확인:
pip show uvicorn
echo.

echo 5. fastapi 설치 확인:
pip show fastapi
echo.

echo ✅ 확인 완료
pause 