@echo off
chcp 65001
echo 🔍 Python 설치 상태 확인 중...
echo.

echo 1. Python 버전 확인:
python --version
if %errorlevel% neq 0 (
    echo ❌ python 명령어 실패
    echo.
    echo 2. py 명령어 확인:
    py --version
    if %errorlevel% neq 0 (
        echo ❌ py 명령어도 실패
        echo.
        echo 3. Python 경로 확인:
        where python
        if %errorlevel% neq 0 (
            echo ❌ Python이 PATH에 없습니다
            echo.
            echo 4. py 경로 확인:
            where py
            if %errorlevel% neq 0 (
                echo ❌ py도 PATH에 없습니다
                echo.
                echo ========================================
                echo ❌ Python이 설치되어 있지 않거나 PATH에 없습니다
                echo.
                echo 해결 방법:
                echo 1. https://python.org 에서 Python 다운로드
                echo 2. 설치 시 "Add Python to PATH" 체크
                echo 3. 컴퓨터 재시작
                echo 4. 이 배치 파일 다시 실행
                echo ========================================
            ) else (
                echo ✅ py 명령어 발견
                echo Python 경로: 
                where py
            )
        ) else (
            echo ✅ python 명령어 발견
            echo Python 경로:
            where python
        )
    ) else (
        echo ✅ py 명령어 사용 가능
    )
) else (
    echo ✅ python 명령어 사용 가능
)

echo.
echo 5. pip 확인:
pip --version
if %errorlevel% neq 0 (
    echo ❌ pip 명령어 실패
) else (
    echo ✅ pip 사용 가능
)

echo.
echo 6. 현재 디렉토리:
cd
echo.

echo 7. 파일 목록:
dir *.py
echo.

pause 