@echo off
chcp 65001 > nul
echo Starting EORA AI System...
echo Current Directory: %CD%
python -m uvicorn src.app:app --host 127.0.0.1 --port 8001 --reload
pause 