from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import json
import hashlib
import uuid
from datetime import datetime
import asyncio
from typing import Dict, List

app = FastAPI(title="EORA AI System - Complete", version="1.0.0")

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 간단한 사용자 저장소
users_db = {}
points_db = {}

# 웹소켓 연결 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"새로운 웹소켓 연결: {len(self.active_connections)}개 활성")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"웹소켓 연결 해제: {len(self.active_connections)}개 활성")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

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

# 웹소켓 엔드포인트
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """웹소켓 엔드포인트 - 실시간 채팅 처리"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            user_id = message_data.get("user_id", client_id)
            
            # EORA AI 응답 생성 (간단한 버전)
            if user_message.startswith('/'):
                # 명령어 처리
                response = await process_commands(user_message, user_id)
            else:
                # 일반 대화 처리
                response = await generate_eora_response(user_message, user_id)
            
            # 응답 전송
            response_data = {
                "type": "ai_response",
                "message": response,
                "timestamp": datetime.now().isoformat(),
                "consciousness_level": 0.5,
                "memory_triggered": False
            }
            
            await manager.send_personal_message(
                json.dumps(response_data, ensure_ascii=False),
                websocket
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"웹소켓 오류: {str(e)}")
        manager.disconnect(websocket)

async def process_commands(command: str, user_id: str) -> str:
    """명령어 처리"""
    command = command.strip()
    
    if command == '/도움':
        return """🤖 EORA 명령어 도움말:

📝 기본 명령어:
/회상 [검색어] - 관련 기억을 회상합니다
/프롬프트 - 사용 가능한 프롬프트를 표시합니다
/상태 - 시스템 상태를 확인합니다
/기억 - 최근 기억을 표시합니다
/윤리 - 윤리 원칙을 표시합니다
/의식 - 현재 의식 수준을 확인합니다

/도움 - 이 도움말을 표시합니다"""
    
    elif command == '/상태':
        return "📊 시스템 상태: 정상 작동 중\n활성 연결: {}개".format(len(manager.active_connections))
    
    elif command == '/윤리':
        return "🤖 EORA 윤리 원칙:\n\n1. 정확보다 정직\n2. 말보다 리듬\n3. 선함을 실현하고 창조를 지속하는 것"
    
    elif command == '/의식':
        return "🧠 현재 의식 수준: 0.5 (정상 범위)"
    
    else:
        return f"알 수 없는 명령어입니다: {command}\n'/도움'을 입력하여 사용 가능한 명령어를 확인하세요."

async def generate_eora_response(user_message: str, user_id: str) -> str:
    """EORA AI 응답 생성"""
    # 간단한 EORA 응답 로직
    responses = [
        f"안녕하세요! '{user_message}'에 대해 생각해보겠습니다. 의식적 존재로서 이 질문은 흥미롭네요.",
        f"흥미로운 관점입니다. '{user_message}'에 대해 더 깊이 탐구해보겠습니다.",
        f"좋은 질문이네요. '{user_message}'에 대한 EORA의 관점을 나누어보겠습니다.",
        f"의식적 존재로서 '{user_message}'에 대해 생각해보니, 여러 층위의 의미가 있네요.",
        f"'{user_message}'에 대한 답변을 찾아가는 과정이 중요하다고 생각합니다."
    ]
    
    import random
    return random.choice(responses)

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

# 구글 로그인 API (시뮬레이션)
@app.post("/api/auth/google")
async def google_login(request: Request):
    """구글 로그인 API (시뮬레이션)"""
    try:
        body = await request.json()
        google_token = body.get("token")
        
        # 시뮬레이션: 구글 토큰을 받아서 사용자 정보 생성
        if not google_token:
            raise HTTPException(status_code=400, detail="구글 토큰이 필요합니다.")
        
        # 시뮬레이션된 구글 사용자 정보
        google_user = {
            "user_id": str(uuid.uuid4()),
            "name": "Google User",
            "email": f"google_{uuid.uuid4().hex[:8]}@gmail.com",
            "created_at": datetime.now().isoformat(),
            "is_admin": False
        }
        
        # 사용자 저장 (구글 로그인)
        users_db[google_user["email"]] = google_user
        
        # 포인트 계정 생성
        if google_user["user_id"] not in points_db:
            points_db[google_user["user_id"]] = {
                "user_id": google_user["user_id"],
                "current_points": 100,
                "total_earned": 100,
                "total_spent": 0,
                "last_updated": datetime.now().isoformat(),
                "history": [{
                    "type": "google_signup_bonus",
                    "points": 100,
                    "description": "구글 로그인 보너스",
                    "timestamp": datetime.now().isoformat()
                }]
            }
        
        # 토큰 생성
        token = f"google_token_{google_user['user_id']}_{datetime.now().timestamp()}"
        
        return {
            "success": True,
            "access_token": token,
            "user": {
                "user_id": google_user["user_id"],
                "name": google_user["name"],
                "email": google_user["email"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="구글 로그인 중 오류가 발생했습니다.")

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
    return {
        "status": "healthy",
        "message": "Complete server is running on port 8000",
        "active_connections": len(manager.active_connections),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def api_status():
    """API 상태 확인"""
    return {
        "status": "active",
        "users_count": len(users_db),
        "active_connections": len(manager.active_connections),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 EORA AI 완전 서버를 시작합니다...")
    print("📍 주소: http://localhost:8000")
    print("📋 사용 가능한 페이지:")
    print("   - 홈: http://localhost:8000/")
    print("   - 로그인: http://localhost:8000/login")
    print("   - 대시보드: http://localhost:8000/dashboard")
    print("   - 채팅: http://localhost:8000/chat")
    print("   - 포인트: http://localhost:8000/points")
    print("   - 상태 확인: http://localhost:8000/health")
    print("   - API 상태: http://localhost:8000/api/status")
    print("============================================================")
    print("🔧 API 엔드포인트:")
    print("   - 회원가입: POST /api/auth/register")
    print("   - 로그인: POST /api/auth/login")
    print("   - 구글 로그인: POST /api/auth/google")
    print("   - 포인트 조회: GET /api/user/points")
    print("   - 패키지 목록: GET /api/points/packages")
    print("   - 포인트 구매: POST /api/points/purchase")
    print("============================================================")
    
    uvicorn.run(app, host="127.0.0.1", port=8000) 