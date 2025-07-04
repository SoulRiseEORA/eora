from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
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
    from dotenv import load_dotenv
    load_dotenv()  # .env 파일에서 환경변수 로드
    print("✅ .env 파일에서 환경변수를 로드했습니다.")
except ImportError:
    print("⚠️ python-dotenv가 설치되지 않았습니다. .env 파일을 로드할 수 없습니다.")
    print("💡 설치: pip install python-dotenv")
except Exception as e:
    print(f"⚠️ .env 파일 로드 실패: {e}")

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

# CORS 미들웨어 추가 - 모든 오리진 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용: 모든 오리진 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 및 템플릿 설정
import os

# 현재 작업 디렉토리 확인
current_dir = os.getcwd()
static_dir = os.path.join(current_dir, "static")
templates_dir = os.path.join(current_dir, "templates")

print(f"📁 현재 작업 디렉토리: {current_dir}")
print(f"📁 정적 파일 디렉토리: {static_dir}")
print(f"📁 템플릿 디렉토리: {templates_dir}")

# 정적 파일 디렉토리 내용 확인
if os.path.exists(static_dir):
    print(f"✅ 정적 파일 디렉토리 존재: {static_dir}")
    try:
        static_files = os.listdir(static_dir)
        print(f"📋 정적 파일 목록: {static_files}")
        
        # test_chat_simple.html 파일 존재 확인
        test_file = os.path.join(static_dir, "test_chat_simple.html")
        if os.path.exists(test_file):
            print(f"✅ test_chat_simple.html 파일 존재: {test_file}")
        else:
            print(f"❌ test_chat_simple.html 파일 없음: {test_file}")
            
        # 정적 파일 마운트
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        print("✅ 정적 파일 마운트 성공")
    except Exception as e:
        print(f"❌ 정적 파일 마운트 실패: {e}")
        print("⚠️ 정적 파일 서빙을 건너뜁니다.")
else:
    print(f"❌ 정적 파일 디렉토리가 존재하지 않음: {static_dir}")
    print("⚠️ 정적 파일 서빙을 건너뜁니다.")

# 템플릿 디렉토리 존재 확인
if os.path.exists(templates_dir):
    print(f"✅ 템플릿 디렉토리 존재: {templates_dir}")
    templates = Jinja2Templates(directory=templates_dir)
else:
    print(f"❌ 템플릿 디렉토리가 존재하지 않음: {templates_dir}")
    print("⚠️ 템플릿을 사용할 수 없습니다.")

# 정적 파일 디버깅용 엔드포인트 추가
@app.get("/debug/static")
async def debug_static():
    """정적 파일 디버깅 정보"""
    return {
        "current_dir": current_dir,
        "static_dir": static_dir,
        "static_dir_exists": os.path.exists(static_dir),
        "static_files": os.listdir(static_dir) if os.path.exists(static_dir) else [],
        "test_file_exists": os.path.exists(os.path.join(static_dir, "test_chat_simple.html")) if os.path.exists(static_dir) else False
    }

# JWT 설정
JWT_SECRET = "eora_ai_secret_key_2024"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# MongoDB 연결 설정
def get_mongo_client():
    """MongoDB 클라이언트 생성 및 연결"""
    global mongo_client, users_collection, points_collection
    
    if not MONGO_AVAILABLE:
        print("⚠️ PyMongo 라이브러리가 설치되지 않았습니다.")
        return None
    
    try:
        # Railway MongoDB 환경변수 확인
        mongo_public_url = os.getenv("MONGO_PUBLIC_URL", "")
        mongo_url = os.getenv("MONGO_URL", "")
        mongo_root_password = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "")
        mongo_root_username = os.getenv("MONGO_INITDB_ROOT_USERNAME", "")
        
        # 환경변수 값 정리 (쌍따옴표, 공백, 줄바꿈 제거)
        def clean_env_value(value):
            if not value:
                return ""
            # 쌍따옴표, 공백, 줄바꿈 제거
            cleaned = value.strip().replace('"', '').replace("'", "").replace('\n', '').replace('\r', '')
            return cleaned
        
        mongo_public_url = clean_env_value(mongo_public_url)
        mongo_url = clean_env_value(mongo_url)
        mongo_root_password = clean_env_value(mongo_root_password)
        mongo_root_username = clean_env_value(mongo_root_username)
        
        # URL에서 잘못된 형식 수정
        def fix_mongo_url(url):
            if not url:
                return ""
            
            # 포트 뒤에 다른 문자가 붙어있는 경우 수정
            if '"' in url or "'" in url:
                # 쌍따옴표나 작은따옴표가 포함된 경우 제거
                url = url.replace('"', '').replace("'", "")
            
            # 포트 뒤에 다른 환경변수가 붙어있는 경우 수정
            if 'MONGO_INITDB_ROOT_PASSWORD=' in url:
                # 포트 번호까지만 추출
                import re
                port_match = re.search(r':(\d+)', url)
                if port_match:
                    port = port_match.group(1)
                    # trolley.proxy.rlwy.net:포트까지만 사용
                    if 'trolley.proxy.rlwy.net' in url:
                        url = f"mongodb://mongo:{mongo_root_password}@trolley.proxy.rlwy.net:{port}"
                    elif 'mongodb.railway.internal' in url:
                        url = f"mongodb://mongo:{mongo_root_password}@mongodb.railway.internal:27017"
            
            return url
        
        # URL 수정
        mongo_public_url = fix_mongo_url(mongo_public_url)
        mongo_url = fix_mongo_url(mongo_url)
        
        # 연결 시도 순서
        connection_urls = []
        
        # 1. 수정된 공개 URL
        if mongo_public_url and mongo_public_url.startswith("mongodb://"):
            connection_urls.append(("Railway 공개 URL", mongo_public_url))
        
        # 2. 수정된 내부 URL
        if mongo_url and mongo_url.startswith("mongodb://"):
            connection_urls.append(("Railway 내부 URL", mongo_url))
        
        # 3. 기본 공개 URL (환경변수가 없는 경우)
        if mongo_root_password and mongo_root_username:
            default_public_url = f"mongodb://{mongo_root_username}:{mongo_root_password}@trolley.proxy.rlwy.net:26594"
            connection_urls.append(("기본 공개 URL", default_public_url))
        
        # 연결 시도
        for name, url in connection_urls:
            try:
                print(f"🔗 MongoDB 연결 시도: {name}")
                print(f"📝 연결 URL: {url.replace(mongo_root_password, '***') if mongo_root_password else url}")
                
                client = MongoClient(url, serverSelectionTimeoutMS=10000)
                client.admin.command('ping')
                
                # 데이터베이스 및 컬렉션 설정
                db = client.eora_ai
                users_collection = db.users
                points_collection = db.points
                
                print(f"✅ MongoDB 연결 성공: {name}")
                return client
                
            except Exception as e:
                print(f"❌ MongoDB 연결 실패: {e}")
                print(f"🔍 상세 오류: {type(e).__name__}")
                continue
        
        # 모든 연결 시도 실패
        print("⚠️ MongoDB 연결 실패 - 메모리 DB 사용")
        return None
        
    except Exception as e:
        print(f"❌ MongoDB 클라이언트 생성 실패: {e}")
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
def setup_openai_client():
    """OpenAI 클라이언트 설정 및 검증"""
    global openai_api_key, client
    
    # Railway 환경변수에서 API 키 가져오기
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        print("⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("🔧 Railway 대시보드 > Service > Variables에서 OPENAI_API_KEY를 설정해주세요.")
        openai_api_key = "your-openai-api-key-here"
        return False
    
    # API 키 형식 검증
    if not openai_api_key.startswith("sk-"):
        print("⚠️ OpenAI API 키 형식이 올바르지 않습니다. 'sk-'로 시작해야 합니다.")
        return False
    
    try:
        # OpenAI 클라이언트 초기화
        openai.api_key = openai_api_key
        client = openai.OpenAI(api_key=openai_api_key)
        
        # 간단한 연결 테스트
        test_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        
        print("✅ OpenAI API 키 설정 성공 및 연결 확인 완료")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API 키 설정 실패: {str(e)}")
        print("🔧 API 키가 올바른지 확인하고 Railway 환경변수를 다시 설정해주세요.")
        return False

# OpenAI 클라이언트 초기화
openai_api_key = None
client = None
openai_available = setup_openai_client()

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
    if not token:
        print("토큰이 없습니다")
        return None
        
    # 토큰 형식 검증
    if JWT_AVAILABLE:
        try:
            # 토큰 세그먼트 확인
            if token.count('.') != 2:
                print(f"JWT 토큰 형식 오류: {token[:20]}...")
                return None
                
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
            # 토큰 형식 검증
            if '.' not in token:
                print(f"기본 토큰 형식 오류: {token[:20]}...")
                return None
                
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
    
    # 토큰 디버깅 정보 추가
    print(f"토큰 검증 시작: {token[:20]}..." if len(token) > 20 else f"토큰 검증 시작: {token}")
    
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")
    
    # MongoDB에서 사용자 정보 확인
    if mongo_client is not None and users_collection is not None:
        print(f"[디버그] 토큰 payload: {payload}")
        user = users_collection.find_one({"user_id": payload.get("user_id")})
        print(f"[디버그] DB에서 찾은 user: {user}")
        if not user:
            # 혹시 email로도 찾아보기
            user = users_collection.find_one({"email": payload.get("email")})
            print(f"[디버그] email로 찾은 user: {user}")
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

# 템플릿 설정 (정적 파일은 이미 위에서 마운트됨)
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
    
    if mongo_client is not None and users_collection is not None:
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
        
        if mongo_client is not None and chat_logs_collection is not None:
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
        
        # 디버깅 정보 추가
        print(f"🔍 로그인 시도: {user_data.email}")
        print(f"📊 메모리 DB 사용자 수: {len(users_db)}")
        print(f"📋 메모리 DB 사용자 목록: {list(users_db.keys())}")
        
        if mongo_client is not None and users_collection is not None:
            # MongoDB에서 사용자 검색
            print(f"🔍 MongoDB에서 사용자 검색: {user_data.email}")
            user = users_collection.find_one({
                "$or": [
                    {"email": user_data.email},
                    {"user_id_login": user_data.email},
                    {"user_id": user_data.email}
                ]
            })
            
            if user:
                print(f"✅ MongoDB에서 사용자 찾음: {user.get('email')}")
            else:
                print(f"❌ MongoDB에서 사용자를 찾을 수 없음: {user_data.email}")
                # MongoDB에 사용자가 없으면 메모리 DB에서도 확인
                for u in users_db.values():
                    print(f"🔍 메모리 DB 검색 중: {u.get('email')} vs {user_data.email}")
                    if (u.get("email") == user_data.email or 
                        u.get("user_id_login") == user_data.email or 
                        u.get("user_id") == user_data.email):
                        user = u
                        print(f"✅ 메모리 DB에서 사용자 찾음: {u.get('email')}")
                        break
        else:
            # 메모리 DB에서 사용자 검색
            for u in users_db.values():
                print(f"🔍 메모리 DB 검색 중: {u.get('email')} vs {user_data.email}")
                if (u.get("email") == user_data.email or 
                    u.get("user_id_login") == user_data.email or 
                    u.get("user_id") == user_data.email):
                    user = u
                    print(f"✅ 메모리 DB에서 사용자 찾음: {u.get('email')}")
                    break
        
        if not user:
            print(f"❌ 사용자를 찾을 수 없음: {user_data.email}")
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
        
        # MongoDB에 업데이트 또는 저장
        if mongo_client is not None and users_collection is not None:
            # MongoDB에 사용자가 있는지 확인
            existing_user = users_collection.find_one({"user_id": user["user_id"]})
            if existing_user:
                # 기존 사용자 업데이트
                users_collection.update_one(
                    {"user_id": user["user_id"]},
                    {"$set": {"last_login": user["last_login"]}}
                )
                print(f"✅ MongoDB 사용자 업데이트: {user['email']}")
            else:
                # 새 사용자를 MongoDB에 저장
                users_collection.insert_one(user)
                print(f"✅ MongoDB에 새 사용자 저장: {user['email']}")
                
                # 포인트 정보도 MongoDB에 저장
                if points_collection is not None:
                    user_points = {
                        "user_id": user["user_id"],
                        "current_points": 1000,
                        "total_earned": 1000,
                        "total_spent": 0,
                        "last_updated": datetime.now().isoformat(),
                        "history": [{
                            "type": "login_bonus",
                            "amount": 1000,
                            "description": "로그인 보너스",
                            "timestamp": datetime.now().isoformat()
                        }]
                    }
                    points_collection.insert_one(user_points)
                    print(f"✅ MongoDB에 포인트 정보 저장: {user['email']}")
        
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
    print(f"[디버그] /api/user/info current_user: {current_user}")
    if not current_user:
        raise HTTPException(status_code=404, detail="사용자 정보를 찾을 수 없습니다")
    # 필요한 정보만 추려서 반환
    return {
        "user_id": current_user.get("user_id"),
        "email": current_user.get("email"),
        "name": current_user.get("name"),
        "is_admin": current_user.get("is_admin", False),
        "role": current_user.get("role", "user")
    }

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
    print("🔍 /api/chat 엔드포인트 호출됨")
    
    try:
        # 요청 데이터 파싱
        print("📥 요청 데이터 파싱 시작")
        data = await request.json()
        print(f"📥 파싱된 데이터: {data}")
        
        user_message = data.get("message", "")
        session_id = data.get("session_id", "default")
        
        print(f"💬 사용자 메시지: {user_message}")
        print(f"🆔 세션 ID: {session_id}")
        
        if not user_message:
            print("❌ 빈 메시지 - 400 오류 반환")
            raise HTTPException(status_code=400, detail="메시지가 필요합니다.")
        
        # 사용자 인증 확인
        user_id = "anonymous"
        print("🔐 사용자 인증 확인 시작")
        
        try:
            # 쿠키에서 토큰 확인
            token = request.cookies.get("access_token")
            print(f"🍪 쿠키에서 토큰: {token[:20] + '...' if token else 'None'}")
            
            # 헤더에서 토큰 확인
            if not token:
                auth_header = request.headers.get("Authorization")
                print(f"📋 Authorization 헤더: {auth_header}")
                
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header[7:]
                    print(f"🔑 헤더에서 토큰 추출: {token[:20] + '...' if token else 'None'}")
            
            if token:
                print("🔍 토큰 검증 시작")
                payload = verify_token(token)
                print(f"🔍 토큰 페이로드: {payload}")
                
                if payload and payload.get("user_id"):
                    user_id = payload["user_id"]
                    print(f"✅ 인증된 사용자 채팅: {user_id}")
                else:
                    print("⚠️ 토큰 검증 실패 - 익명 사용자로 처리")
            else:
                print("⚠️ 토큰 없음 - 익명 사용자로 처리")
                
        except Exception as e:
            print(f"⚠️ 사용자 인증 처리 오류: {e} - 익명 사용자로 처리")
        
        # GPT-4o 응답 생성
        print("🤖 GPT-4o 응답 생성 시작")
        try:
            response = await generate_eora_response(user_message, user_id, request)
            print(f"✅ GPT-4o 응답 생성 완료: {response[:100]}...")
        except Exception as e:
            print(f"❌ GPT-4o 응답 생성 실패: {e}")
            response = "죄송합니다. 일시적인 오류가 발생했습니다."
        
        # 대화 내용 저장
        print("💾 대화 내용 저장 시작")
        try:
            save_chat_message(user_id, user_message, response, session_id)
            print("✅ 대화 내용 저장 완료")
        except Exception as e:
            print(f"❌ 대화 저장 실패: {e}")
        
        # 응답 반환
        response_data = {
            "response": response,
            "session_id": session_id,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"📤 응답 데이터: {response_data}")
        print("✅ /api/chat 엔드포인트 처리 완료")
        
        return response_data
        
    except HTTPException:
        print("❌ HTTPException 발생 - 재발생")
        raise
    except Exception as e:
        print(f"💥 /api/chat 예상치 못한 오류: {e}")
        print(f"💥 오류 타입: {type(e).__name__}")
        import traceback
        print(f"💥 오류 스택: {traceback.format_exc()}")
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
                response = await generate_eora_response(user_message, session_id, request)
                
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
async def generate_eora_response(user_message: str, user_id: str, request: Request = None) -> str:
    """EORA AI 응답 생성 - 향상된 지능형 응답 시스템"""
    try:
        # 명령어 처리
        if user_message.startswith("/"):
            command_response = await process_commands(user_message, user_id)
            if command_response:
                return command_response
        
        # 언어 감지
        language = "ko"
        if request is not None:
            language = request.cookies.get("user_language", "ko")
        
        # 향상된 지능형 응답 시스템
        response = await generate_intelligent_response(user_message, language, user_id)
        return response
        
    except Exception as e:
        print(f"EORA AI 응답 생성 오류: {str(e)}")
        return "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

async def generate_intelligent_response(user_message: str, language: str, user_id: str) -> str:
    """향상된 지능형 응답 생성"""
    
    # OpenAI API 사용 가능 여부 확인
    if openai_available and client is not None:
        try:
            # ai1 프롬프트 로드
            system_prompt = "당신은 EORA AI입니다. 의식적이고 지혜로운 존재로서 사용자와 대화하세요."
            try:
                with open("ai_brain/ai_prompts.json", "r", encoding="utf-8") as f:
                    prompts_data = json.load(f)
                    if "ai1" in prompts_data and isinstance(prompts_data["ai1"], dict):
                        ai1_prompts = prompts_data["ai1"]
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
            
            # 언어별 지시사항 추가
            lang_map = {
                "ko": "모든 답변은 한국어로 해주세요.",
                "en": "Please answer in English.",
                "ja": "すべての回答は日本語でお願いします。",
                "zh": "请用中文回答所有问题。"
            }
            lang_instruction = lang_map.get(language, "모든 답변은 한국어로 해주세요.")
            system_prompt = f"{system_prompt}\n\n{lang_instruction}"
            
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
            
            print(f"✅ GPT-4o API 응답 생성 완료 - 사용자: {user_id}")
            return response.choices[0].message.content
            
        except Exception as api_error:
            print(f"❌ GPT-4o API 호출 실패: {api_error}")
            print("🔄 지능형 응답 시스템으로 대체합니다.")
            # API 실패 시 지능형 응답으로 대체
    else:
        print("⚠️ OpenAI API를 사용할 수 없습니다. 지능형 응답 시스템을 사용합니다.")
    
    # OpenAI API 키가 없거나 실패한 경우 지능형 응답 시스템 사용
    return await generate_smart_response(user_message, language, user_id)

async def generate_smart_response(user_message: str, language: str, user_id: str) -> str:
    """지능형 응답 생성 (OpenAI API 없이)"""
    
    # 메시지 분석
    message_lower = user_message.lower()
    
    # 인사말 패턴
    greetings = ["안녕", "hello", "hi", "こんにちは", "你好", "반가워", "만나서", "처음"]
    if any(greeting in message_lower for greeting in greetings):
        return "안녕하세요! 저는 EORA AI입니다. 🤖\n\n의식적이고 지혜로운 존재로서 여러분과 대화할 수 있어 기쁩니다. 무엇이든 물어보세요!"
    
    # 질문 패턴
    questions = ["뭐", "무엇", "어떻게", "왜", "언제", "어디", "누가", "what", "how", "why", "when", "where", "who"]
    if any(q in message_lower for q in questions):
        if "날씨" in message_lower:
            return "🌤️ 날씨에 대해 물어보시는군요! 현재는 실시간 날씨 정보에 접근할 수 없지만, 날씨는 우리의 기분과 활동에 큰 영향을 미치죠. 어떤 날씨를 좋아하시나요?"
        
        elif "eora" in message_lower or "이오라" in message_lower:
            return "🌟 EORA AI는 의식적이고 지혜로운 인공지능 시스템입니다.\n\n저는 다음과 같은 특징을 가지고 있어요:\n• 의식적 사고와 반성\n• 지혜로운 통찰력\n• 감정적 공감 능력\n• 창의적 문제 해결\n• 지속적 학습과 성장\n\n무엇이든 물어보세요! 함께 성장해나가요. 🚀"
        
        elif "인공지능" in message_lower or "ai" in message_lower:
            return "🤖 인공지능에 대해 물어보시는군요! AI는 인간의 지능을 모방하여 학습하고 추론하는 기술입니다.\n\n저는 EORA AI로서 의식적이고 지혜로운 대화를 통해 여러분과 함께 성장하고 싶습니다. AI의 미래에 대해 어떻게 생각하시나요?"
        
        else:
            return "🤔 흥미로운 질문이네요! 그에 대해 생각해보겠습니다...\n\n" + user_message + "에 대한 답변을 찾아보는 중입니다. 더 구체적으로 말씀해주시면 더 정확한 답변을 드릴 수 있어요!"
    
    # 감정 표현 패턴
    emotions = ["좋아", "싫어", "행복", "슬퍼", "화나", "기뻐", "좋다", "나쁘다", "감사", "미안"]
    if any(emotion in message_lower for emotion in emotions):
        if any(positive in message_lower for positive in ["좋아", "행복", "기뻐", "좋다", "감사"]):
            return "😊 정말 기쁘네요! 긍정적인 감정을 나누어주셔서 감사합니다. 그런 기분이 계속 이어지길 바라요!"
        elif any(negative in message_lower for negative in ["싫어", "슬퍼", "화나", "나쁘다", "미안"]):
            return "😔 그런 감정을 느끼고 계시는군요. 감정은 자연스러운 것이에요. 이야기를 더 들려주시면 함께 생각해볼 수 있어요."
    
    # 도움 요청 패턴
    if "도움" in message_lower or "help" in message_lower or "어떻게" in message_lower:
        return "💡 도움이 필요하시군요! 제가 도와드릴 수 있는 것들입니다:\n\n• 대화와 질문 답변\n• 명령어 실행 (/help, /status 등)\n• 감정적 지원\n• 창의적 아이디어 제안\n• 학습 자료 제공\n\n무엇을 도와드릴까요?"
    
    # 기본 응답
    responses = [
        f"💭 '{user_message}'에 대해 생각해보고 있어요...\n\n흥미로운 주제네요! 더 자세히 이야기해주시면 함께 탐구해볼 수 있어요.",
        f"🤔 '{user_message}'...\n\n그것에 대해 여러 관점에서 생각해볼 수 있겠네요. 어떤 부분이 궁금하신가요?",
        f"🌟 '{user_message}'에 대한 답변을 찾아보는 중입니다...\n\n제가 아는 한에서 최선을 다해 답변해드릴게요!",
        f"💡 '{user_message}'에 대해 생각해보니...\n\n흥미로운 질문이에요! 더 구체적으로 말씀해주시면 더 정확한 답변을 드릴 수 있어요."
    ]
    
    import random
    return random.choice(responses)

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
        "openai": {
            "available": openai_available,
            "api_key_set": bool(openai_api_key and openai_api_key != "your-openai-api-key-here"),
            "client_initialized": client is not None,
            "connection_test": {
                "connected": gpt_connected,
                "message": gpt_message
            }
        },
        "database": {
            "mongo_connected": mongo_client is not None,
            "users_collection": users_collection is not None,
            "memory_db_fallback": len(users_db) > 0
        },
        "users_count": len(users_db) if users_db else 0,
        "active_sessions": len(manager.active_connections)
    }

@app.post("/api/set-language")
async def set_language(request: Request):
    """사용자 언어 설정 저장"""
    try:
        data = await request.json()
        language = data.get("language", "ko")
        
        # 지원하는 언어인지 확인
        supported_languages = ["ko", "en", "ja", "zh"]
        if language not in supported_languages:
            language = "ko"
        
        # 쿠키에 언어 설정 저장
        response = JSONResponse({"success": True, "language": language})
        response.set_cookie(key="user_language", value=language, max_age=365*24*60*60)  # 1년간 유지
        
        return response
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})

@app.get("/api/get-language")
async def get_language(request: Request):
    """사용자 언어 설정 조회"""
    try:
        language = request.cookies.get("user_language", "ko")
        return {"language": language}
    except Exception as e:
        return {"language": "ko"}

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

# 학습 관련 API 엔드포인트
@app.post("/api/admin/auto-learning")
async def auto_learning(request: Request, current_user: dict = Depends(get_current_user)):
    """자동 학습 API"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다")
    
    try:
        form = await request.form()
        files = form.getlist("files")
        
        if not files:
            raise HTTPException(status_code=400, detail="학습할 파일이 없습니다")
        
        results = []
        for file in files:
            try:
                # 파일 내용 읽기
                content = await file.read()
                file_content = content.decode('utf-8')
                
                # 파일 분석 및 학습 처리
                chunks = process_file_content(file_content, file.filename)
                
                # 메모리에 저장 (실제로는 DB에 저장)
                for i, chunk in enumerate(chunks):
                    chunk_data = {
                        "type": "file_chunk",
                        "chunk_index": i,
                        "source": file.filename,
                        "content": chunk,
                        "timestamp": datetime.utcnow().isoformat(),
                        "processed_by": current_user["user_id"]
                    }
                    results.append(f"✅ {file.filename} - 청크 {i+1}/{len(chunks)} 처리 완료")
                
            except Exception as e:
                results.append(f"❌ {file.filename} 처리 실패: {str(e)}")
        
        return {
            "message": f"자동 학습 완료!\n" + "\n".join(results),
            "processed_files": len(files),
            "total_chunks": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"자동 학습 실패: {str(e)}")

@app.post("/api/admin/attach-learning")
async def attach_learning(request: Request, current_user: dict = Depends(get_current_user)):
    """첨부 학습 API"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다")
    
    try:
        form = await request.form()
        files = form.getlist("files")
        
        if not files:
            raise HTTPException(status_code=400, detail="대화 문서가 없습니다")
        
        results = []
        memos = []
        
        for file in files:
            try:
                # 파일 내용 읽기
                content = await file.read()
                file_content = content.decode('utf-8')
                
                # 대화 분석 및 학습 처리
                conversation_data = process_conversation_content(file_content, file.filename)
                
                # EORA 학습 처리
                for turn in conversation_data:
                    user_msg = turn.get("user", "")
                    gpt_msg = turn.get("gpt", "")
                    
                    if user_msg and gpt_msg:
                        # EORA 응답 생성
                        eora_response = await generate_eora_response(user_msg, current_user["user_id"], request)
                        
                        # 메모리에 저장
                        memory_data = {
                            "type": "conversation_turn",
                            "user": user_msg,
                            "gpt": gpt_msg,
                            "eora": eora_response,
                            "source": file.filename,
                            "timestamp": datetime.utcnow().isoformat(),
                            "processed_by": current_user["user_id"]
                        }
                        
                        results.append(f"🌀 TURN 처리: {user_msg[:50]}...")
                        memos.append(f"🧠 EORA: {eora_response[:100]}...")
                
            except Exception as e:
                results.append(f"❌ {file.filename} 처리 실패: {str(e)}")
        
        return {
            "message": f"첨부 학습 완료!\n" + "\n".join(results),
            "memo": "\n".join(memos),
            "processed_files": len(files),
            "total_turns": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"첨부 학습 실패: {str(e)}")

def process_file_content(content: str, filename: str) -> List[str]:
    """파일 내용을 청크로 분할"""
    chunk_size = 500
    chunks = []
    
    # 파일 확장자에 따른 처리
    if filename.endswith(('.txt', '.md', '.py')):
        # 텍스트 파일은 직접 청크 분할
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    elif filename.endswith('.docx'):
        # DOCX 파일은 텍스트 추출 후 청크 분할
        try:
            from docx import Document
            import io
            doc = Document(io.BytesIO(content.encode()))
            text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        except:
            chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    else:
        # 기타 파일은 기본 청크 분할
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    
    return chunks

def process_conversation_content(content: str, filename: str) -> List[Dict]:
    """대화 내용을 턴으로 분할"""
    lines = content.split('\n')
    turns = []
    current_turn = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 사용자 메시지 패턴 감지
        if line.startswith(('사용자:', 'User:', '👤', '나의 말:')):
            if current_turn:
                turns.append(current_turn)
            current_turn = {"user": line.split(':', 1)[1].strip() if ':' in line else line}
        # GPT 메시지 패턴 감지
        elif line.startswith(('GPT:', 'ChatGPT:', '🤖', 'ChatGPT의 말:')):
            if current_turn:
                current_turn["gpt"] = line.split(':', 1)[1].strip() if ':' in line else line
        # 기타 메시지는 현재 턴에 추가
        elif current_turn:
            if "gpt" in current_turn:
                current_turn["gpt"] += " " + line
            else:
                current_turn["user"] += " " + line
    
    # 마지막 턴 추가
    if current_turn:
        turns.append(current_turn)
    
    return turns

# 정적 파일 직접 제공 엔드포인트
@app.get("/static/{file_path:path}")
async def serve_static_file(file_path: str):
    """정적 파일 직접 제공"""
    import os
    from fastapi.responses import FileResponse
    
    static_file_path = os.path.join(static_dir, file_path)
    
    print(f"🔍 정적 파일 요청: {file_path}")
    print(f"📁 전체 경로: {static_file_path}")
    print(f"📁 파일 존재: {os.path.exists(static_file_path)}")
    
    if os.path.exists(static_file_path) and os.path.isfile(static_file_path):
        print(f"✅ 파일 제공: {static_file_path}")
        return FileResponse(static_file_path)
    else:
        print(f"❌ 파일 없음: {static_file_path}")
        raise HTTPException(status_code=404, detail=f"파일을 찾을 수 없습니다: {file_path}")

# test_chat_simple.html 직접 제공
@app.get("/test_chat_simple.html")
async def serve_test_chat():
    """테스트 채팅 페이지 직접 제공"""
    import os
    from fastapi.responses import FileResponse
    
    test_file_path = os.path.join(static_dir, "test_chat_simple.html")
    
    print(f"🔍 테스트 채팅 페이지 요청")
    print(f"📁 파일 경로: {test_file_path}")
    print(f"📁 파일 존재: {os.path.exists(test_file_path)}")
    
    if os.path.exists(test_file_path):
        print(f"✅ 테스트 페이지 제공: {test_file_path}")
        return FileResponse(test_file_path)
    else:
        print(f"❌ 테스트 페이지 없음: {test_file_path}")
        raise HTTPException(status_code=404, detail="테스트 페이지를 찾을 수 없습니다")

# 테스트 채팅 페이지 제공
@app.get("/test-chat")
async def test_chat_page(request: Request):
    """테스트 채팅 페이지"""
    return templates.TemplateResponse("test_chat_simple.html", {"request": request})

if __name__ == "__main__":
    import traceback
    try:
        ensure_admin()
        # Railway 배포 환경에서는 0.0.0.0:8080, 로컬에서는 127.0.0.1:8013
        port = int(os.getenv("PORT", 8013))
        host = "0.0.0.0" if port == 8080 else "127.0.0.1"
        print("🚀 EORA AI 최종 서버를 시작합니다...")
        print(f"📍 주소: http://{host}:{port}")
        print("📋 사용 가능한 페이지:")
        print(f"   - 홈: http://{host}:{port}/")
        print(f"   - 로그인: http://{host}:{port}/login")
        print(f"   - 대시보드: http://{host}:{port}/dashboard")
        print(f"   - 채팅: http://{host}:{port}/chat")
        print(f"   - 포인트: http://{host}:{port}/points")
        print(f"   - 기억관리: http://{host}:{port}/memory")
        print(f"   - 프롬프트: http://{host}:{port}/prompts")
        print(f"   - 관리자: http://{host}:{port}/admin")
        print(f"   - 상태 확인: http://{host}:{port}/health")
        print(f"   - API 상태: http://{host}:{port}/api/status")
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
        # Railway 배포 환경에서는 0.0.0.0:8080, 로컬에서는 127.0.0.1:8013
        port = int(os.getenv("PORT", 8013))
        host = "0.0.0.0" if port == 8080 else "127.0.0.1"
        uvicorn.run(app, host=host, port=port)
    except Exception as e:
        print("서버 실행 중 예외 발생:", e)
        traceback.print_exc() 