from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

app = FastAPI(title="Test Server", version="1.0.0")

# 템플릿 설정
templates = Jinja2Templates(directory="templates")

# 디버그 정보 출력
print(f"Current working directory: {os.getcwd()}")
print(f"Templates directory exists: {os.path.exists('templates')}")
if os.path.exists('templates'):
    print("Template files:")
    for file in os.listdir('templates'):
        if file.endswith('.html'):
            print(f"  - {file}")

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """홈 페이지"""
    print("홈페이지 요청 받음")
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/test", response_class=HTMLResponse)
async def test_page(request: Request):
    """테스트 페이지"""
    return HTMLResponse(content="<h1>서버가 정상 작동합니다!</h1>")

@app.get("/debug", response_class=HTMLResponse)
async def debug_page(request: Request):
    """디버그 페이지"""
    print("디버그 페이지 요청 받음")
    return templates.TemplateResponse("debug.html", {"request": request})

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "ok", "message": "서버가 정상 작동 중입니다"} 