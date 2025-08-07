@echo off
chcp 65001 > nul
echo Testing EORA AI Server...
echo.
echo Testing health endpoint...
curl -s http://127.0.0.1:8001/health
echo.
echo.
echo Testing API info endpoint...
curl -s http://127.0.0.1:8001/api
echo.
pause 