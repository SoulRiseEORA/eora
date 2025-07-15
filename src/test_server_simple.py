from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI(title="EORA AI System - Test Server", version="1.0.0")

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """홈 페이지"""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """로그인 페이지"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """대시보드 페이지"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """채팅 페이지"""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/points", response_class=HTMLResponse)
async def points_page(request: Request):
    """포인트 관리 페이지"""
    return templates.TemplateResponse("points.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Test server is running on port 8080"}

if __name__ == "__main__":
    print("🚀 서버를 시작합니다...")
    print("📍 주소: http://localhost:8080")
    print("📋 사용 가능한 페이지:")
    print("   - 홈: http://localhost:8080/")
    print("   - 로그인: http://localhost:8080/login")
    print("   - 대시보드: http://localhost:8080/dashboard")
    print("   - 채팅: http://localhost:8080/chat")
    print("   - 포인트: http://localhost:8080/points")
    print("   - 상태 확인: http://localhost:8080/health")
    print("=" * 50)
    
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info") 