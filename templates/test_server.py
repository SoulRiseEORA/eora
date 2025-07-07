#!/usr/bin/env python3
"""
간단한 테스트 서버
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="EORA Test Server", version="1.0.0")

# 템플릿 설정
templates_path = Path(__file__).parent
templates = Jinja2Templates(directory=str(templates_path))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/test", response_class=HTMLResponse)
async def test(request: Request):
    return {"message": "서버가 정상적으로 실행되고 있습니다!", "status": "success"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "message": "EORA 테스트 서버가 정상적으로 실행 중입니다."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8016) 