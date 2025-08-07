@echo off
chcp 65001
echo 🔧 Python PATH 문제 해결 중...
echo.

echo 1. 일반적인 Python 설치 경로 확인:
echo.

echo C:\Python39\python.exe 확인:
if exist "C:\Python39\python.exe" (
    echo ✅ C:\Python39\python.exe 발견
    set PYTHON_PATH=C:\Python39\python.exe
    goto :found_python
)

echo C:\Python310\python.exe 확인:
if exist "C:\Python310\python.exe" (
    echo ✅ C:\Python310\python.exe 발견
    set PYTHON_PATH=C:\Python310\python.exe
    goto :found_python
)

echo C:\Python311\python.exe 확인:
if exist "C:\Python311\python.exe" (
    echo ✅ C:\Python311\python.exe 발견
    set PYTHON_PATH=C:\Python311\python.exe
    goto :found_python
)

echo C:\Python312\python.exe 확인:
if exist "C:\Python312\python.exe" (
    echo ✅ C:\Python312\python.exe 발견
    set PYTHON_PATH=C:\Python312\python.exe
    goto :found_python
)

echo C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\python.exe 확인:
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\python.exe" (
    echo ✅ AppData Python39 발견
    set PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\python.exe
    goto :found_python
)

echo C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe 확인:
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe" (
    echo ✅ AppData Python310 발견
    set PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe
    goto :found_python
)

echo C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe 확인:
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe" (
    echo ✅ AppData Python311 발견
    set PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe
    goto :found_python
)

echo C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe 확인:
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" (
    echo ✅ AppData Python312 발견
    set PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe
    goto :found_python
)

echo.
echo ❌ Python을 찾을 수 없습니다.
echo.
echo 해결 방법:
echo 1. https://python.org 에서 Python 다운로드
echo 2. 설치 시 "Add Python to PATH" 체크
echo 3. 컴퓨터 재시작
echo.
pause
exit /b 1

:found_python
echo.
echo ✅ Python 발견: %PYTHON_PATH%
echo.

echo 2. Python 버전 확인:
"%PYTHON_PATH%" --version
if %errorlevel% neq 0 (
    echo ❌ Python 실행 실패
    pause
    exit /b 1
)

echo.
echo 3. pip 확인:
"%PYTHON_PATH%" -m pip --version
if %errorlevel% neq 0 (
    echo ❌ pip 실패
    pause
    exit /b 1
)

echo.
echo 4. 필요한 패키지 설치:
echo fastapi 설치 중...
"%PYTHON_PATH%" -m pip install fastapi
echo uvicorn 설치 중...
"%PYTHON_PATH%" -m pip install uvicorn
echo jinja2 설치 중...
"%PYTHON_PATH%" -m pip install jinja2
echo python-multipart 설치 중...
"%PYTHON_PATH%" -m pip install python-multipart
echo PyJWT 설치 중...
"%PYTHON_PATH%" -m pip install PyJWT

echo.
echo 5. 서버 테스트:
echo 간단한 서버를 시작합니다...
"%PYTHON_PATH%" simple_server.py

pause 