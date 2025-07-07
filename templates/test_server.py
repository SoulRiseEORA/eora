#!/usr/bin/env python3
"""
간단한 테스트 서버 - 기본 기능 확인용
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 템플릿 설정
templates_path = Path(__file__).parent
templates = Jinja2Templates(directory=str(templates_path))

# FastAPI 앱 생성
app = FastAPI(title="EORA Test Server", version="1.0.0")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/test", response_class=HTMLResponse)
async def test(request: Request):
    return templates.TemplateResponse("test_chat_simple.html", {"request": request})

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "테스트 서버가 정상적으로 실행 중입니다."
    }

@app.get("/api/status")
async def api_status():
    return {
        "message": "EORA Test Server API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 간단한 테스트 서버를 시작합니다...")
    print("📍 주소: http://127.0.0.1:8003")
    print("📋 테스트 페이지: http://127.0.0.1:8003/test")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8003) 