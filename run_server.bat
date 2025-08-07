@echo off
echo Starting EORA AI System...
python -m uvicorn src.app:app --host 127.0.0.1 --port 8001 --reload
pause 