from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import json
import hashlib
import uuid
from datetime import datetime

app = FastAPI(title="EORA AI System - Test", version="1.0.0")

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 간단한 사용자 저장소
users_db = {}
points_db = {}

# 페이지 라우트
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

# 인증 API
@app.post("/api/auth/register")
async def register_user(request: Request):
    """회원가입 API"""
    try:
        body = await request.json()
        name = body.get("name")
        email = body.get("email")
        password = body.get("password")
        
        if not all([name, email, password]):
            raise HTTPException(status_code=400, detail="모든 필드를 입력해주세요.")
        
        if email in users_db:
            raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
        
        # 비밀번호 해싱
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # 사용자 생성
        user_id = str(uuid.uuid4())
        users_db[email] = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.now().isoformat(),
            "is_admin": False
        }
        
        # 포인트 계정 생성 (회원가입 보너스 100포인트)
        points_db[user_id] = {
            "user_id": user_id,
            "current_points": 100,
            "total_earned": 100,
            "total_spent": 0,
            "last_updated": datetime.now().isoformat(),
            "history": [{
                "type": "signup_bonus",
                "points": 100,
                "description": "회원가입 보너스",
                "timestamp": datetime.now().isoformat()
            }]
        }
        
        return {"success": True, "message": "회원가입이 완료되었습니다."}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="회원가입 중 오류가 발생했습니다.")

@app.post("/api/auth/login")
async def login_user(request: Request):
    """로그인 API"""
    try:
        body = await request.json()
        email = body.get("email")
        password = body.get("password")
        
        if not all([email, password]):
            raise HTTPException(status_code=400, detail="이메일과 비밀번호를 입력해주세요.")
        
        if email not in users_db:
            raise HTTPException(status_code=400, detail="존재하지 않는 이메일입니다.")
        
        user = users_db[email]
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        if user["password"] != hashed_password:
            raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")
        
        # 간단한 JWT 토큰 생성
        token = f"test_token_{user['user_id']}_{datetime.now().timestamp()}"
        
        return {
            "success": True,
            "access_token": token,
            "user": {
                "user_id": user["user_id"],
                "name": user["name"],
                "email": user["email"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="로그인 중 오류가 발생했습니다.")

# 포인트 시스템 API
@app.get("/api/user/points")
async def get_user_points(request: Request):
    """사용자 포인트 조회"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    
    token = auth_header.split(" ")[1]
    user_id = token.split("_")[2] if len(token.split("_")) > 2 else None
    
    if not user_id or user_id not in points_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    return points_db[user_id]

@app.get("/api/points/packages")
async def get_point_packages():
    """포인트 패키지 조회"""
    packages = [
        {
            "id": "starter",
            "name": "스타터 패키지",
            "points": 100,
            "price": 5000,
            "description": "처음 시작하는 분들을 위한 패키지",
            "is_popular": False
        },
        {
            "id": "basic",
            "name": "기본 패키지",
            "points": 500,
            "price": 20000,
            "description": "일반적인 사용을 위한 패키지",
            "is_popular": True
        },
        {
            "id": "premium",
            "name": "프리미엄 패키지",
            "points": 1500,
            "price": 50000,
            "description": "많은 대화를 원하는 분들을 위한 패키지",
            "discount_percent": 10
        },
        {
            "id": "unlimited",
            "name": "무제한 패키지",
            "points": 5000,
            "price": 150000,
            "description": "무제한 대화를 위한 패키지",
            "discount_percent": 20
        }
    ]
    return packages

@app.post("/api/points/purchase")
async def purchase_points(request: Request):
    """포인트 구매 (시뮬레이션)"""
    try:
        body = await request.json()
        package_id = body.get("package_id")
        payment_method = body.get("payment_method")
        
        # 간단한 토큰 검증
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="인증이 필요합니다.")
        
        token = auth_header.split(" ")[1]
        user_id = token.split("_")[2] if len(token.split("_")) > 2 else None
        
        if not user_id or user_id not in points_db:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        
        # 패키지 정보 가져오기
        packages = await get_point_packages()
        package = next((p for p in packages if p["id"] == package_id), None)
        
        if not package:
            raise HTTPException(status_code=400, detail="존재하지 않는 패키지입니다.")
        
        # 포인트 추가
        points_db[user_id]["current_points"] += package["points"]
        points_db[user_id]["total_earned"] += package["points"]
        points_db[user_id]["last_updated"] = datetime.now().isoformat()
        
        # 구매 기록 추가
        points_db[user_id]["history"].append({
            "type": "purchase",
            "points": package["points"],
            "description": f"{package['name']} 구매",
            "payment_method": payment_method,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "message": f"{package['name']} 구매가 완료되었습니다.",
            "points_added": package["points"],
            "current_points": points_db[user_id]["current_points"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="포인트 구매 중 오류가 발생했습니다.")

# 상태 확인 API
@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/status")
async def api_status():
    """API 상태 확인"""
    return {
        "status": "active",
        "users_count": len(users_db),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 EORA AI 테스트 서버를 시작합니다...")
    print("📍 주소: http://localhost:8000")
    print("📋 사용 가능한 페이지:")
    print("   - 홈: http://localhost:8000/")
    print("   - 로그인: http://localhost:8000/login")
    print("   - 대시보드: http://localhost:8000/dashboard")
    print("   - 채팅: http://localhost:8000/chat")
    print("   - 포인트: http://localhost:8000/points")
    print("   - 상태 확인: http://localhost:8000/health")
    print("==================================================")
    
    uvicorn.run(app, host="127.0.0.1", port=8000) 