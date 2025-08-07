@echo off
echo ====================================
echo EORA AI 크롬 브라우저 연결 도우미
echo ====================================
echo.
echo 🔧 크롬 캐시 정리 중...
taskkill /F /IM chrome.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo 🌐 EORA AI 사이트 열기...
echo.
echo 📍 접속 중인 주소:
echo    http://127.0.0.1:8001
echo    http://127.0.0.1:8001/admin
echo.

REM 크롬으로 사이트 열기 (시크릿 모드)
start chrome --new-window --incognito "http://127.0.0.1:8001"
timeout /t 2 /nobreak >nul
start chrome --new-window --incognito "http://127.0.0.1:8001/admin"

echo ✅ 크롬 브라우저에서 사이트를 열었습니다!
echo.
echo 💡 만약 연결이 안 되면:
echo    1. 주소창에 직접 입력: http://127.0.0.1:8001
echo    2. Ctrl+F5로 강제 새로고침
echo    3. 시크릿 모드에서 다시 시도
echo.
pause 