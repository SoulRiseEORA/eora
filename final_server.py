from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import json
import hashlib
import uuid
from datetime import datetime, timedelta
import asyncio
from typing import Dict, List, Optional
import os
import openai
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    import base64
    import json
    JWT_AVAILABLE = False
from pydantic import BaseModel
try:
    import pymongo
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

app = FastAPI(title="EORA AI System - Final", version="1.0.0")

# JWT 설정
JWT_SECRET = "eora_ai_secret_key_2024"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# MongoDB 연결 설정
def get_mongo_client():
    """MongoDB 클라이언트 생성"""
    if not MONGO_AVAILABLE:
        print("⚠️ PyMongo 라이브러리가 설치되지 않았습니다.")
        return None
    
    try:
        # Railway 환경변수에서 MongoDB 설정 읽기
        mongo_user = os.getenv("MONGOUSER", "mongo")
        mongo_password = os.getenv("MONGOPASSWORD", "HYxotmUHxMxbYAejsOxEnHwrgKpAochC")
        mongo_host = os.getenv("MONGOHOST", "localhost")
        mongo_port = os.getenv("MONGOPORT", "27017")
        
        # MongoDB 연결 문자열
        mongo_url = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}"
        
        client = MongoClient(mongo_url)
        # 연결 테스트
        client.admin.command('ping')
        print(f"✅ MongoDB 연결 성공: {mongo_host}:{mongo_port}")
        return client
    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")
        return None

# MongoDB 클라이언트 초기화
mongo_client = get_mongo_client()
if mongo_client:
    db = mongo_client.eora_ai
    users_collection = db.users
    points_collection = db.points
    sessions_collection = db.sessions
    chat_logs_collection = db.chat_logs
else:
    print("⚠️ MongoDB 연결 실패 - 메모리 DB 사용")
    db = None
    users_collection = None
    points_collection = None
    sessions_collection = None
    chat_logs_collection = None

# OpenAI 클라이언트 설정 - Railway 환경변수 방식
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
    openai_api_key = "your-openai-api-key-here"

openai.api_key = openai_api_key
client = openai.OpenAI(api_key=openai_api_key)

# Railway API 설정
RAILWAY_API_URL = "https://railway.com/project/8eadf3cc-4066-4de1-a342-2fef5fa5b843/service/fffde6bf-4da3-4b54-8526-36d62c9b8c75/variables"
RAILWAY_ENVIRONMENT_ID = "2f521e06-ef3a-46c4-a3c9-499500d94a53"

# Pydantic 모델
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# JWT 토큰 생성 (PyJWT 또는 기본 방식)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    if JWT_AVAILABLE:
        try:
            encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
            return encoded_jwt
        except Exception as e:
            print(f"PyJWT 토큰 생성 실패: {e}")
            return None
    else:
        # 기본 Base64 인코딩 방식
        try:
            json_str = json.dumps(to_encode, default=str)
            encoded_jwt = base64.b64encode(json_str.encode()).decode()
            return encoded_jwt
        except Exception as e:
            print(f"기본 토큰 생성 실패: {e}")
            return None

# JWT 토큰 검증 (PyJWT 또는 기본 방식)
def verify_token(token: str):
    if JWT_AVAILABLE:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            print("JWT 토큰 만료")
            return None
        except jwt.InvalidTokenError as e:
            print(f"JWT 토큰 검증 실패: {e}")
            return None
        except Exception as e:
            print(f"JWT 토큰 처리 오류: {e}")
            return None
    else:
        # 기본 Base64 디코딩 방식
        try:
            decoded_bytes = base64.b64decode(token.encode())
            payload = json.loads(decoded_bytes.decode())
            
            # 만료 시간 확인
            exp_str = payload.get("exp")
            if exp_str:
                exp_time = datetime.fromisoformat(exp_str.replace('Z', '+00:00'))
                if datetime.utcnow() > exp_time:
                    print("토큰 만료")
                    return None
            
            return payload
        except Exception as e:
            print(f"기본 토큰 검증 실패: {e}")
            return None

# 의존성 주입
security = HTTPBearer(auto_error=False)

async def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = None
    if credentials:
        token = credentials.credentials
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="토큰이 필요합니다")
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")
    # MongoDB에서 사용자 정보 확인
    if mongo_client and users_collection:
        user = users_collection.find_one({"user_id": payload.get("user_id")})
        if not user:
            raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다")
        return user
    else:
        # 메모리 DB 사용
        user_id = payload.get("user_id")
        if user_id not in users_db:
            raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다")
        return users_db[user_id]

# GPT-4o 연결 테스트 함수
async def test_gpt4o_connection():
    """GPT-4o 연결 상태 확인"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        return True, "GPT-4o 연결 성공"
    except Exception as e:
        return False, f"GPT-4o 연결 실패: {str(e)}"

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 사용자 저장소 (MongoDB 연결 실패 시 메모리 사용)
users_db = {}
points_db = {}
sessions_db = {}

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

# 관리자 계정 생성 함수 개선
def ensure_admin():
    """관리자 계정 생성 및 보장"""
    admin_email = "admin@eora.ai"
    admin_id = "admin"
    
    if mongo_client and users_collection:
        # MongoDB에서 관리자 계정 확인
        admin_user = users_collection.find_one({
            "$or": [
                {"email": admin_email},
                {"user_id_login": admin_id}
            ]
        })
        
        if not admin_user:
            # 관리자 계정 생성
            admin_user_id = str(uuid.uuid4())
            hashed_password = hashlib.sha256("admin1234".encode()).hexdigest()
            
            admin_data = {
                "user_id": admin_user_id,
                "name": "관리자",
                "email": admin_email,
                "user_id_login": admin_id,
                "password": hashed_password,
                "created_at": datetime.now().isoformat(),
                "is_admin": True,
                "last_login": None,
                "status": "active",
                "role": "admin",
                "permissions": ["read", "write", "admin", "delete"]
            }
            
            users_collection.insert_one(admin_data)
            
            # 관리자 포인트 초기화
            admin_points = {
                "user_id": admin_user_id,
                "current_points": 10000,
                "total_earned": 10000,
                "total_spent": 0,
                "last_updated": datetime.now().isoformat(),
                "history": [{
                    "type": "admin_bonus",
                    "amount": 10000,
                    "description": "관리자 계정 생성 보너스",
                    "timestamp": datetime.now().isoformat()
                }]
            }
            
            points_collection.insert_one(admin_points)
            print(f"✅ 관리자 계정 생성 (MongoDB): {admin_email} (ID: {admin_id}, PW: admin1234)")
    else:
        # 메모리 DB에서 관리자 계정 확인
        admin_found = False
        for user_id, user in users_db.items():
            if user.get("email") == admin_email or user.get("user_id_login") == admin_id:
                admin_found = True
                break
        
        if not admin_found:
            admin_user_id = str(uuid.uuid4())
            hashed_password = hashlib.sha256("admin1234".encode()).hexdigest()
            
            users_db[admin_user_id] = {
                "user_id": admin_user_id,
                "name": "관리자",
                "email": admin_email,
                "user_id_login": admin_id,
                "password": hashed_password,
                "created_at": datetime.now().isoformat(),
                "is_admin": True,
                "last_login": None,
                "status": "active",
                "role": "admin",
                "permissions": ["read", "write", "admin", "delete"]
            }
            
            # 관리자 포인트 초기화
            points_db[admin_user_id] = {
                "user_id": admin_user_id,
                "current_points": 10000,
                "total_earned": 10000,
                "total_spent": 0,
                "last_updated": datetime.now().isoformat(),
                "history": [{
                    "type": "admin_bonus",
                    "amount": 10000,
                    "description": "관리자 계정 생성 보너스",
                    "timestamp": datetime.now().isoformat()
                }]
            }
            
            print(f"✅ 관리자 계정 생성 (메모리): {admin_email} (ID: {admin_id}, PW: admin1234)")

# 대화 저장 함수
def save_chat_message(user_id: str, message: str, response: str, session_id: str = "default"):
    """대화 내용을 MongoDB 또는 파일에 저장"""
    try:
        chat_data = {
            "user_id": user_id,
            "session_id": session_id,
            "message": message,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "created_at": datetime.now()
        }
        
        if mongo_client and chat_logs_collection:
            # MongoDB에 저장
            chat_logs_collection.insert_one(chat_data)
            print(f"✅ 대화 저장 (MongoDB): {user_id}")
        else:
            # 파일에 저장
            chat_dir = "chat_logs"
            if not os.path.exists(chat_dir):
                os.makedirs(chat_dir)
            
            chat_file = os.path.join(chat_dir, f"{user_id}_{session_id}.json")
            chat_history = []
            
            if os.path.exists(chat_file):
                with open(chat_file, 'r', encoding='utf-8') as f:
                    chat_history = json.load(f)
            
            chat_history.append(chat_data)
            
            with open(chat_file, 'w', encoding='utf-8') as f:
                json.dump(chat_history, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"✅ 대화 저장 (파일): {chat_file}")
            
    except Exception as e:
        print(f"❌ 대화 저장 실패: {e}")

# 페이지 라우트
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """홈 페이지"""
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """로그인 페이지"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """대시보드 페이지 - 토큰 검증 완화 (프론트엔드에서 처리)"""
    # 대시보드는 프론트엔드에서 토큰 검증을 처리하도록 함
    # 서버에서는 기본 페이지만 제공
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """채팅 페이지"""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/points", response_class=HTMLResponse)
async def points_page(request: Request):
    """포인트 관리 페이지"""
    return templates.TemplateResponse("points.html", {"request": request})

@app.get("/memory", response_class=HTMLResponse)
async def memory_page(request: Request):
    """기억 관리 페이지"""
    return templates.TemplateResponse("memory.html", {"request": request})

@app.get("/prompts", response_class=HTMLResponse)
async def prompts_page(request: Request):
    """프롬프트 라이브러리 페이지 - 관리자 전용"""
    # 쿠키에서 토큰 확인
    token = request.cookies.get("access_token")
    
    # 헤더에서 토큰 확인
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
    
    # 토큰이 없으면 로그인 페이지로 리다이렉트
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    
    # JWT 토큰 검증
    payload = verify_token(token)
    if not payload:
        return RedirectResponse(url="/login", status_code=302)
    
    # 관리자 권한 확인
    if not payload.get("is_admin"):
        return RedirectResponse(url="/dashboard", status_code=302)
    
    return templates.TemplateResponse("prompts.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """관리자 페이지 - 프론트엔드에서 권한 검증"""
    # 관리자 페이지는 프론트엔드에서 권한 검증을 처리하도록 함
    return templates.TemplateResponse("admin.html", {"request": request})

# API 엔드포인트
@app.post("/api/auth/register")
async def register_user(user_data: UserCreate):
    """회원가입 API - GitHub 스타일"""
    try:
        # 이메일 중복 확인
        for user in users_db.values():
            if user["email"] == user_data.email:
                raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
        
        # 사용자 ID 생성
        user_id = str(uuid.uuid4())
        
        # 비밀번호 해시화
        hashed_password = hashlib.sha256(user_data.password.encode()).hexdigest()
        
        # 사용자 정보 저장
        users_db[user_id] = {
            "user_id": user_id,
            "name": user_data.name,
            "email": user_data.email,
            "user_id_login": user_data.email.split("@")[0],  # 이메일 앞부분을 로그인 ID로
            "password": hashed_password,
            "created_at": datetime.now().isoformat(),
            "is_admin": False,
            "last_login": None,
            "status": "active",
            "role": "user",
            "permissions": ["read", "write"],
            "profile": {
                "avatar": None,
                "bio": "",
                "location": "",
                "website": ""
            }
        }
        
        # 포인트 초기화
        points_db[user_id] = {
            "user_id": user_id,
            "current_points": 100,
            "total_earned": 100,
            "total_spent": 0,
            "last_updated": datetime.now().isoformat(),
            "history": [{
                "type": "signup_bonus",
                "amount": 100,
                "description": "회원가입 보너스",
                "timestamp": datetime.now().isoformat()
            }]
        }
        
        print(f"✅ 새 사용자 등록: {user_data.email} (ID: {user_id})")
        
        return {
            "success": True,
            "message": "회원가입이 완료되었습니다.",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 회원가입 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="회원가입 중 오류가 발생했습니다.")

@app.post("/api/auth/login")
async def login_user(user_data: UserLogin):
    """로그인 API - GitHub 스타일"""
    try:
        user = None
        
        if mongo_client and users_collection:
            # MongoDB에서 사용자 검색
            user = users_collection.find_one({
                "$or": [
                    {"email": user_data.email},
                    {"user_id_login": user_data.email},
                    {"user_id": user_data.email}
                ]
            })
        else:
            # 메모리 DB에서 사용자 검색
            for u in users_db.values():
                if (u.get("email") == user_data.email or 
                    u.get("user_id_login") == user_data.email or 
                    u.get("user_id") == user_data.email):
                    user = u
                    break
        
        if not user:
            raise HTTPException(status_code=400, detail="존재하지 않는 계정입니다.")
        
        # 비밀번호 확인
        hashed_password = hashlib.sha256(user_data.password.encode()).hexdigest()
        if user["password"] != hashed_password:
            raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")
        
        # 계정 상태 확인
        if user.get("status") != "active":
            raise HTTPException(status_code=400, detail="비활성화된 계정입니다.")
        
        # 마지막 로그인 시간 업데이트
        user["last_login"] = datetime.now().isoformat()
        
        # MongoDB에 업데이트
        if mongo_client and users_collection:
            users_collection.update_one(
                {"user_id": user["user_id"]},
                {"$set": {"last_login": user["last_login"]}}
            )
        
        # JWT 토큰 생성
        token_data = {
            "user_id": user["user_id"],
            "email": user["email"],
            "name": user["name"],
            "is_admin": user.get("is_admin", False),
            "role": user.get("role", "user")
        }
        
        access_token = create_access_token(token_data)
        
        if not access_token:
            raise HTTPException(status_code=500, detail="토큰 생성에 실패했습니다.")
        
        print(f"✅ 사용자 로그인: {user['email']}")
        
        # 응답 생성
        response_data = {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user["user_id"],
            "email": user["email"],
            "name": user["name"],
            "is_admin": user.get("is_admin", False),
            "role": user.get("role", "user")
        }
        
        # JSONResponse로 쿠키 설정
        response = JSONResponse(content=response_data)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # 개발환경에서는 False
            samesite="lax",
            max_age=60 * 60 * 24  # 24시간
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 로그인 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="로그인 중 오류가 발생했습니다.")

@app.post("/api/auth/logout")
async def logout_user(current_user: dict = Depends(get_current_user)):
    """로그아웃 API"""
    try:
        print(f"✅ 사용자 로그아웃: {current_user.get('email')}")
        return {
            "success": True,
            "message": "로그아웃되었습니다."
        }
    except Exception as e:
        print(f"❌ 로그아웃 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="로그아웃 중 오류가 발생했습니다.")

# 구글 로그인 API (시뮬레이션)
@app.post("/api/auth/google")
async def google_login(request: Request):
    """구글 로그인 API (시뮬레이션)"""
    try:
        body = await request.json()
        email = body.get("email", "")
        
        if not email:
            raise HTTPException(status_code=400, detail="이메일이 필요합니다.")
        
        # 간단한 이메일 검증
        if "@" not in email or "." not in email:
            raise HTTPException(status_code=400, detail="유효한 이메일 주소를 입력해주세요.")
        
        # 사용자 ID 생성
        user_id = f"google_{hashlib.md5(email.encode()).hexdigest()[:8]}"
        
        # 사용자가 존재하지 않으면 새로 생성
        if user_id not in users_db:
            users_db[user_id] = {
                "user_id": user_id,
                "email": email,
                "name": email.split("@")[0],
                "user_id_login": email.split("@")[0],
                "provider": "google",
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat(),
                "is_admin": False,
                "status": "active",
                "role": "user",
                "permissions": ["read", "write"]
            }
            
            # 포인트 초기화
            points_db[user_id] = {
                "user_id": user_id,
                "current_points": 100,
                "total_earned": 100,
                "total_spent": 0,
                "last_updated": datetime.now().isoformat(),
                "history": [
                    {
                        "type": "signup_bonus",
                        "points": 100,
                        "description": "구글 로그인 보너스",
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            }
        else:
            # 기존 사용자 로그인 시간 업데이트
            users_db[user_id]["last_login"] = datetime.now().isoformat()
        
        # JWT 토큰 생성
        token_data = {
            "user_id": user_id,
            "email": email,
            "name": users_db[user_id]["name"],
            "is_admin": False,
            "role": "user"
        }
        
        access_token = create_access_token(token_data)
        
        return {
            "success": True,
            "message": "구글 로그인이 완료되었습니다.",
            "access_token": access_token,
            "token_type": "bearer",
            "user": users_db[user_id]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"구글 로그인 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="구글 로그인 중 오류가 발생했습니다.")

@app.post("/api/auth/github")
async def github_login(request: Request):
    """깃허브 로그인 (시뮬레이션)"""
    try:
        body = await request.json()
        username = body.get("username", "")
        
        if not username:
            raise HTTPException(status_code=400, detail="사용자명이 필요합니다.")
        
        # 사용자 ID 생성
        user_id = f"github_{hashlib.md5(username.encode()).hexdigest()[:8]}"
        
        # 사용자가 존재하지 않으면 새로 생성
        if user_id not in users_db:
            users_db[user_id] = {
                "user_id": user_id,
                "email": f"{username}@github.com",
                "name": username,
                "user_id_login": username,
                "provider": "github",
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat(),
                "is_admin": False,
                "status": "active",
                "role": "user",
                "permissions": ["read", "write"]
            }
            
            # 포인트 초기화
            points_db[user_id] = {
                "user_id": user_id,
                "current_points": 100,
                "total_earned": 100,
                "total_spent": 0,
                "last_updated": datetime.now().isoformat(),
                "history": [
                    {
                        "type": "signup_bonus",
                        "points": 100,
                        "description": "깃허브 로그인 보너스",
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            }
        else:
            # 기존 사용자 로그인 시간 업데이트
            users_db[user_id]["last_login"] = datetime.now().isoformat()
        
        # JWT 토큰 생성
        token_data = {
            "user_id": user_id,
            "email": users_db[user_id]["email"],
            "name": username,
            "is_admin": False,
            "role": "user"
        }
        
        access_token = create_access_token(token_data)
        
        return {
            "success": True,
            "message": "깃허브 로그인이 완료되었습니다.",
            "access_token": access_token,
            "token_type": "bearer",
            "user": users_db[user_id]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"깃허브 로그인 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="깃허브 로그인 중 오류가 발생했습니다.")

@app.post("/api/auth/kakao")
async def kakao_login(request: Request):
    """카카오 로그인 (시뮬레이션)"""
    try:
        body = await request.json()
        nickname = body.get("nickname", "")
        
        if not nickname:
            raise HTTPException(status_code=400, detail="닉네임이 필요합니다.")
        
        # 사용자 ID 생성
        user_id = f"kakao_{hashlib.md5(nickname.encode()).hexdigest()[:8]}"
        
        # 사용자가 존재하지 않으면 새로 생성
        if user_id not in users_db:
            users_db[user_id] = {
                "user_id": user_id,
                "email": f"{nickname}@kakao.com",
                "name": nickname,
                "user_id_login": nickname,
                "provider": "kakao",
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat(),
                "is_admin": False,
                "status": "active",
                "role": "user",
                "permissions": ["read", "write"]
            }
            
            # 포인트 초기화
            points_db[user_id] = {
                "user_id": user_id,
                "current_points": 100,
                "total_earned": 100,
                "total_spent": 0,
                "last_updated": datetime.now().isoformat(),
                "history": [
                    {
                        "type": "signup_bonus",
                        "points": 100,
                        "description": "카카오 로그인 보너스",
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            }
        else:
            # 기존 사용자 로그인 시간 업데이트
            users_db[user_id]["last_login"] = datetime.now().isoformat()
        
        # JWT 토큰 생성
        token_data = {
            "user_id": user_id,
            "email": users_db[user_id]["email"],
            "name": nickname,
            "is_admin": False,
            "role": "user"
        }
        
        access_token = create_access_token(token_data)
        
        return {
            "success": True,
            "message": "카카오 로그인이 완료되었습니다.",
            "access_token": access_token,
            "token_type": "bearer",
            "user": users_db[user_id]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"카카오 로그인 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="카카오 로그인 중 오류가 발생했습니다.")

@app.get("/api/user/info")
async def get_user_info(current_user: dict = Depends(get_current_user)):
    """사용자 정보 조회 API"""
    try:
        user_id = current_user.get("user_id")
        if user_id not in users_db:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        
        user = users_db[user_id]
        
        # 민감한 정보 제외
        user_info = {
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
            "created_at": user["created_at"],
            "last_login": user.get("last_login"),
            "is_admin": user.get("is_admin", False),
            "role": user.get("role", "user"),
            "status": user.get("status", "active"),
            "profile": user.get("profile", {})
        }
        
        return user_info
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"사용자 정보 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="사용자 정보 조회 중 오류가 발생했습니다.")

@app.get("/api/user/stats")
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    """사용자 통계 API"""
    try:
        user_id = current_user.get("user_id")
        
        # 포인트 정보
        points_info = points_db.get(user_id, {
            "current_points": 0,
            "total_earned": 0,
            "total_spent": 0
        })
        
        # 세션 정보
        user_sessions = sessions_db.get(user_id, [])
        
        stats = {
            "total_conversations": len(user_sessions),
            "current_points": points_info["current_points"],
            "total_earned": points_info["total_earned"],
            "total_spent": points_info["total_spent"],
            "avg_consciousness": 7.5,  # 임시 값
            "total_insights": len([s for s in user_sessions if s.get("has_insight", False)]),
            "intuition_accuracy": 85.2  # 임시 값
        }
        
        return stats
        
    except Exception as e:
        print(f"사용자 통계 조회 오류: {str(e)}")
        return {
            "total_conversations": 0,
            "current_points": 0,
            "total_earned": 0,
            "total_spent": 0,
            "avg_consciousness": 0,
            "total_insights": 0,
            "intuition_accuracy": 0
        }

@app.get("/api/user/activity")
async def get_user_activity(current_user: dict = Depends(get_current_user)):
    """사용자 활동 API"""
    try:
        user_id = current_user.get("user_id")
        
        # 최근 활동 생성
        activities = [
            {
                "icon": "🎉",
                "title": "EORA AI 시스템에 오신 것을 환영합니다!",
                "time": "방금 전",
                "type": "welcome"
            },
            {
                "icon": "💬",
                "title": "첫 번째 대화를 시작해보세요",
                "time": "지금",
                "type": "suggestion"
            }
        ]
        
        # 실제 세션 데이터가 있다면 추가
        user_sessions = sessions_db.get(user_id, [])
        for session in user_sessions[-5:]:  # 최근 5개
            activities.append({
                "icon": "💬",
                "title": f"대화 세션: {session.get('title', '무제')}",
                "time": session.get("created_at", "알 수 없음"),
                "type": "conversation"
            })
        
        return activities
        
    except Exception as e:
        print(f"사용자 활동 조회 오류: {str(e)}")
        return []

@app.get("/api/user/points")
async def get_user_points(current_user: dict = Depends(get_current_user)):
    """사용자 포인트 조회 API"""
    try:
        user_id = current_user.get("user_id")
        points_info = points_db.get(user_id, {
            "current_points": 0,
            "total_earned": 0,
            "total_spent": 0,
            "history": []
        })
        
        return points_info
        
    except Exception as e:
        print(f"포인트 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="포인트 조회 중 오류가 발생했습니다.")

@app.get("/api/points/packages")
async def get_point_packages():
    """포인트 패키지 목록 API"""
    packages = [
        {
            "id": "basic",
            "name": "기본 패키지",
            "points": 1000,
            "price": 10000,
            "description": "기본적인 대화를 위한 포인트",
            "popular": False
        },
        {
            "id": "premium",
            "name": "프리미엄 패키지",
            "points": 5000,
            "price": 45000,
            "description": "많은 대화를 위한 포인트",
            "popular": True
        },
        {
            "id": "unlimited",
            "name": "무제한 패키지",
            "points": 10000,
            "price": 80000,
            "description": "무제한 대화를 위한 포인트",
            "popular": False
        }
    ]
    
    return {"packages": packages}

@app.post("/api/points/purchase")
async def purchase_points(request: Request, current_user: dict = Depends(get_current_user)):
    """포인트 구매 API"""
    try:
        body = await request.json()
        package_id = body.get("package_id")
        
        if not package_id:
            raise HTTPException(status_code=400, detail="패키지 ID가 필요합니다.")
        
        # 패키지 정보 확인
        packages = {
            "basic": {"points": 1000, "price": 10000},
            "premium": {"points": 5000, "price": 45000},
            "unlimited": {"points": 10000, "price": 80000}
        }
        
        if package_id not in packages:
            raise HTTPException(status_code=400, detail="유효하지 않은 패키지입니다.")
        
        package = packages[package_id]
        user_id = current_user.get("user_id")
        
        # 포인트 추가
        if user_id not in points_db:
            points_db[user_id] = {
                "user_id": user_id,
                "current_points": 0,
                "total_earned": 0,
                "total_spent": 0,
                "last_updated": datetime.now().isoformat(),
                "history": []
            }
        
        points_db[user_id]["current_points"] += package["points"]
        points_db[user_id]["total_earned"] += package["points"]
        points_db[user_id]["last_updated"] = datetime.now().isoformat()
        
        # 구매 기록 추가
        points_db[user_id]["history"].append({
            "type": "purchase",
            "amount": package["points"],
            "description": f"{package_id} 패키지 구매",
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "message": f"{package['points']}포인트가 추가되었습니다.",
            "current_points": points_db[user_id]["current_points"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"포인트 구매 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="포인트 구매 중 오류가 발생했습니다.")

@app.get("/api/prompts")
async def get_prompts(current_user: dict = Depends(get_current_user)):
    """프롬프트 목록 API - 관리자 전용"""
    try:
        # 관리자 권한 확인
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
        
        with open("ai_brain/ai_prompts.json", "r", encoding="utf-8") as f:
            prompts_data = json.load(f)
        
        # 전체 프롬프트 구조 반환
        return {"prompts": prompts_data}
    except Exception as e:
        print(f"프롬프트 로드 오류: {str(e)}")
        return {"prompts": {}}

@app.post("/api/prompts/update")
async def update_prompts(request: Request, current_user: dict = Depends(get_current_user)):
    """프롬프트 업데이트 API - 관리자 전용"""
    try:
        # 관리자 권한 확인
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
        
        data = await request.json()
        prompts_data = data.get("prompts", {})
        
        # 프롬프트 파일 업데이트
        with open("ai_brain/ai_prompts.json", "w", encoding="utf-8") as f:
            json.dump(prompts_data, f, ensure_ascii=False, indent=2)
        
        return {"message": "프롬프트가 성공적으로 업데이트되었습니다."}
    except Exception as e:
        print(f"프롬프트 업데이트 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="프롬프트 업데이트 중 오류가 발생했습니다.")

@app.post("/api/prompts/update-category")
async def update_prompt_category(request: Request, current_user: dict = Depends(get_current_user)):
    """특정 카테고리 프롬프트 업데이트 API - 관리자 전용"""
    try:
        # 관리자 권한 확인
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
        
        data = await request.json()
        ai_name = data.get("ai_name")  # ai1, ai2, ai3, ai4, ai5, ai6
        category = data.get("category")  # system, role, guide, format
        content = data.get("content")  # 새로운 내용
        
        if not ai_name or not category or content is None:
            raise HTTPException(status_code=400, detail="필수 파라미터가 누락되었습니다.")
        
        # 기존 프롬프트 로드
        with open("ai_brain/ai_prompts.json", "r", encoding="utf-8") as f:
            prompts_data = json.load(f)
        
        # 해당 AI의 카테고리 업데이트
        if ai_name not in prompts_data:
            prompts_data[ai_name] = {}
        
        prompts_data[ai_name][category] = content
        
        # 파일에 저장
        with open("ai_brain/ai_prompts.json", "w", encoding="utf-8") as f:
            json.dump(prompts_data, f, ensure_ascii=False, indent=2)
        
        return {"message": f"{ai_name}의 {category} 프롬프트가 성공적으로 업데이트되었습니다."}
    except Exception as e:
        print(f"카테고리 프롬프트 업데이트 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="프롬프트 업데이트 중 오류가 발생했습니다.")

@app.delete("/api/prompts/delete-category")
async def delete_prompt_category(request: Request, current_user: dict = Depends(get_current_user)):
    """특정 카테고리 프롬프트 삭제 API - 관리자 전용"""
    try:
        # 관리자 권한 확인
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
        
        data = await request.json()
        ai_name = data.get("ai_name")  # ai1, ai2, ai3, ai4, ai5, ai6
        category = data.get("category")  # system, role, guide, format
        
        if not ai_name or not category:
            raise HTTPException(status_code=400, detail="필수 파라미터가 누락되었습니다.")
        
        # 기존 프롬프트 로드
        with open("ai_brain/ai_prompts.json", "r", encoding="utf-8") as f:
            prompts_data = json.load(f)
        
        # 해당 AI의 카테고리 삭제
        if ai_name in prompts_data and category in prompts_data[ai_name]:
            del prompts_data[ai_name][category]
            
            # AI가 비어있으면 전체 삭제
            if not prompts_data[ai_name]:
                del prompts_data[ai_name]
            
            # 파일에 저장
            with open("ai_brain/ai_prompts.json", "w", encoding="utf-8") as f:
                json.dump(prompts_data, f, ensure_ascii=False, indent=2)
            
            return {"message": f"{ai_name}의 {category} 프롬프트가 성공적으로 삭제되었습니다."}
        else:
            raise HTTPException(status_code=404, detail="해당 프롬프트를 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"카테고리 프롬프트 삭제 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="프롬프트 삭제 중 오류가 발생했습니다.")

@app.post("/api/prompts/update")
async def update_prompts(request: Request, current_user: dict = Depends(get_current_user)):
    """프롬프트 업데이트 API - 관리자 전용"""
    try:
        # 관리자 권한 확인
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
        
        data = await request.json()
        prompts_data = data.get("prompts", {})
        
        # 프롬프트 파일 업데이트
        with open("ai_brain/ai_prompts.json", "w", encoding="utf-8") as f:
            json.dump(prompts_data, f, ensure_ascii=False, indent=2)
        
        return {"message": "프롬프트가 성공적으로 업데이트되었습니다."}
    except Exception as e:
        print(f"프롬프트 업데이트 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="프롬프트 업데이트 중 오류가 발생했습니다.")

@app.get("/api/memory")
async def get_memory():
    """기억 데이터 API"""
    try:
        # 기억 데이터 파일이 있다면 로드
        memory_file = "memory/memory_db.json"
        if os.path.exists(memory_file):
            with open(memory_file, "r", encoding="utf-8") as f:
                memory_data = json.load(f)
            return memory_data
        else:
            return {"memories": []}
    except Exception as e:
        print(f"기억 데이터 로드 오류: {str(e)}")
        return {"memories": []}

@app.post("/api/chat")
async def chat_api(request: Request):
    """채팅 API 엔드포인트"""
    try:
        data = await request.json()
        user_message = data.get("message", "")
        session_id = data.get("session_id", "default")
        user_id = data.get("user_id", "anonymous")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="메시지가 필요합니다.")
        
        # GPT-4o 응답 생성
        try:
            response = await generate_eora_response(user_message, user_id)
        except Exception as e:
            print(f"GPT-4o 응답 생성 실패: {e}")
            response = "죄송합니다. 일시적인 오류가 발생했습니다."
        
        # 대화 내용 저장
        try:
            save_chat_message(user_id, user_message, response, session_id)
        except Exception as e:
            print(f"대화 저장 실패: {e}")
        
        return {
            "response": response,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"/api/chat 오류: {e}")
        raise HTTPException(status_code=500, detail="/api/chat 처리 중 오류가 발생했습니다.")

# 웹소켓 엔드포인트
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """웹소켓 엔드포인트 - 실시간 채팅 처리"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type", "message")
            
            if message_type == "message":
                user_message = message_data.get("content", "")
                session_id = message_data.get("session_id", client_id)
                
                # GPT-4o 응답 생성
                response = await generate_eora_response(user_message, session_id)
                
                # 응답 전송
                await manager.send_personal_message(json.dumps({
                    "type": "response",
                    "content": response,
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# EORA AI 응답 생성 함수
async def generate_eora_response(user_message: str, user_id: str) -> str:
    """EORA AI 응답 생성 - ai1 프롬프트 적용"""
    try:
        # 명령어 처리
        if user_message.startswith("/"):
            command_response = await process_commands(user_message, user_id)
            if command_response:
                return command_response
        
        # ai1 프롬프트 로드
        system_prompt = "당신은 EORA AI입니다. 의식적이고 지혜로운 존재로서 사용자와 대화하세요."
        try:
            with open("ai_brain/ai_prompts.json", "r", encoding="utf-8") as f:
                prompts_data = json.load(f)
                if "ai1" in prompts_data and isinstance(prompts_data["ai1"], dict):
                    ai1_prompts = prompts_data["ai1"]
                    # system, role, guide, format 프롬프트 조합
                    system_parts = []
                    if "system" in ai1_prompts:
                        system_parts.extend(ai1_prompts["system"])
                    if "role" in ai1_prompts:
                        system_parts.extend(ai1_prompts["role"])
                    if "guide" in ai1_prompts:
                        system_parts.extend(ai1_prompts["guide"])
                    if "format" in ai1_prompts:
                        system_parts.extend(ai1_prompts["format"])
                    
                    if system_parts:
                        system_prompt = "\n\n".join(system_parts)
        except Exception as e:
            print(f"프롬프트 로드 오류: {str(e)}")
            # 기본 프롬프트 사용
        
        # GPT-4o API 호출
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"GPT-4o API 오류: {str(e)}")
        return "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

# 명령어 처리 함수
async def process_commands(command: str, user_id: str) -> str:
    """특별 명령어 처리"""
    command = command.lower().strip()
    
    if command == "/help":
        return """🤖 EORA AI 명령어 목록:
/help - 도움말 보기
/status - 시스템 상태 확인
/points - 포인트 잔액 확인
/clear - 대화 기록 초기화
/admin - 관리자 기능 (관리자만)"""
    
    elif command == "/status":
        return "✅ EORA AI 시스템이 정상적으로 작동 중입니다."
    
    elif command == "/points":
        points_info = points_db.get(user_id, {"current_points": 0})
        return f"💰 현재 포인트: {points_info['current_points']}점"
    
    elif command == "/clear":
        return "🗑️ 대화 기록이 초기화되었습니다."
    
    elif command == "/admin":
        user = users_db.get(user_id)
        if user and user.get("is_admin"):
            return "🔧 관리자 패널에 접근할 수 있습니다: /admin"
        else:
            return "❌ 관리자 권한이 필요합니다."
    
    else:
        return None

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/status")
async def api_status():
    """API 상태 확인"""
    gpt_connected, gpt_message = await test_gpt4o_connection()
    
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "gpt_connection": {
            "connected": gpt_connected,
            "message": gpt_message
        },
        "users_count": len(users_db),
        "active_sessions": len(manager.active_connections)
    }

# 관리자 API 엔드포인트들
@app.get("/api/admin/users")
async def admin_get_users(current_user: dict = Depends(get_current_user)):
    """관리자용 사용자 목록 조회"""
    try:
        # 관리자 권한 확인
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
        
        users_list = []
        for user in users_db.values():
            points_info = points_db.get(user["user_id"], {
                "current_points": 0,
                "total_earned": 0,
                "total_spent": 0
            })
            users_list.append({
                "user_id": user["user_id"],
                "name": user["name"],
                "email": user["email"],
                "created_at": user["created_at"],
                "status": user.get("status", "active"),
                "points": points_info["current_points"],
                "is_admin": user.get("is_admin", False),
                "role": user.get("role", "user"),
                "last_login": user.get("last_login")
            })
        return users_list
    except HTTPException:
        raise
    except Exception as e:
        print(f"관리자 사용자 목록 조회 오류: {str(e)}")
        return []

@app.get("/api/admin/overview")
async def admin_overview(current_user: dict = Depends(get_current_user)):
    """관리자용 시스템 개요"""
    try:
        # 관리자 권한 확인
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
        
        total_users = len(users_db)
        active_users = len([u for u in users_db.values() if u.get("status", "active") == "active"])
        
        total_points = 0
        total_conversations = 0
        
        for user_id, points_info in points_db.items():
            total_points += points_info.get("current_points", 0)
            total_conversations += len(points_info.get("history", []))
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_points": total_points,
            "total_conversations": total_conversations
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"관리자 개요 조회 오류: {str(e)}")
        return {
            "total_users": 0,
            "active_users": 0,
            "total_points": 0,
            "total_conversations": 0
        }

@app.get("/api/admin/points")
async def admin_points(current_user: dict = Depends(get_current_user)):
    """관리자용 포인트 통계"""
    try:
        # 관리자 권한 확인
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
        
        total_issued = 0
        total_spent = 0
        user_count = len(points_db)
        
        for points_info in points_db.values():
            total_issued += points_info.get("total_earned", 0)
            total_spent += points_info.get("total_spent", 0)
        
        avg_per_user = total_issued / user_count if user_count > 0 else 0
        
        return {
            "total_issued": total_issued,
            "total_spent": total_spent,
            "avg_per_user": round(avg_per_user, 1)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"관리자 포인트 통계 조회 오류: {str(e)}")
        return {
            "total_issued": 0,
            "total_spent": 0,
            "avg_per_user": 0
        }

@app.get("/api/admin/system")
async def admin_system(current_user: dict = Depends(get_current_user)):
    """관리자용 시스템 정보"""
    try:
        # 관리자 권한 확인
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
        
        return {
            "users_count": len(users_db),
            "points_count": len(points_db),
            "server_status": "running",
            "uptime": "1시간 30분"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"관리자 시스템 정보 조회 오류: {str(e)}")
        return {
            "users_count": 0,
            "points_count": 0,
            "server_status": "unknown",
            "uptime": "unknown"
        }

if __name__ == "__main__":
    import traceback
    try:
        ensure_admin()
        print("🚀 EORA AI 최종 서버를 시작합니다...")
        print("📍 주소: http://localhost:8010")
        print("📋 사용 가능한 페이지:")
        print("   - 홈: http://localhost:8010/")
        print("   - 로그인: http://localhost:8010/login")
        print("   - 대시보드: http://localhost:8010/dashboard")
        print("   - 채팅: http://localhost:8010/chat")
        print("   - 포인트: http://localhost:8010/points")
        print("   - 기억관리: http://localhost:8010/memory")
        print("   - 프롬프트: http://localhost:8010/prompts")
        print("   - 관리자: http://localhost:8010/admin")
        print("   - 상태 확인: http://localhost:8010/health")
        print("   - API 상태: http://localhost:8010/api/status")
        print("============================================================")
        print("🔧 API 엔드포인트:")
        print("   - 회원가입: POST /api/auth/register")
        print("   - 로그인: POST /api/auth/login")
        print("   - 구글 로그인: POST /api/auth/google")
        print("   - 사용자 정보: GET /api/user/info")
        print("   - 사용자 통계: GET /api/user/stats")
        print("   - 사용자 활동: GET /api/user/activity")
        print("   - 포인트 조회: GET /api/user/points")
        print("   - 패키지 목록: GET /api/points/packages")
        print("   - 포인트 구매: POST /api/points/purchase")
        print("============================================================")
        uvicorn.run(app, host="127.0.0.1", port=8010)
    except Exception as e:
        print("서버 실행 중 예외 발생:", e)
        traceback.print_exc() 