#!/usr/bin/env python3
"""
EORA AI System - 감정 중심 인공지능 플랫폼
FAISS 기반 임베딩 대화 관리 시스템 포함
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

# FastAPI 및 관련 라이브러리
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# 데이터베이스 및 캐시
import pymongo
from pymongo import MongoClient
from bson import ObjectId
import redis.asyncio as redis

# AI 및 임베딩
import openai
import numpy as np

# FAISS 임베딩 시스템 (선택적)
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    FAISS_AVAILABLE = True
    logger.info("✅ FAISS 및 Sentence Transformers 로드 성공")
except ImportError as e:
    FAISS_AVAILABLE = False
    logger.warning(f"⚠️ FAISS 모듈 로드 실패: {e}")
    logger.info("🔄 기본 대화 시스템을 사용합니다.")

# 인증 및 보안
import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

# 보안 설정
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 환경 변수
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

# OpenAI 클라이언트 초기화 (proxies 인자 제거)
if OPENAI_API_KEY:
    try:
        openai.api_key = OPENAI_API_KEY
        logger.info("✅ OpenAI 클라이언트 초기화 성공")
    except Exception as e:
        logger.warning(f"⚠️ OpenAI 클라이언트 초기화 실패: {e}")
else:
    logger.warning("⚠️ OPENAI_API_KEY가 설정되지 않았습니다. GPT API 기능이 제한됩니다.")

# MongoDB 연결
try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client.eora_ai
    users_collection = db.users
    sessions_collection = db.sessions
    chat_logs_collection = db.chat_logs
    points_collection = db.points
    
    # 컬렉션 인덱스 생성
    users_collection.create_index("email", unique=True)
    sessions_collection.create_index("user_id")
    chat_logs_collection.create_index("session_id")
    
    logger.info("✅ MongoDB 연결 성공")
except Exception as e:
    logger.error(f"❌ MongoDB 연결 실패: {e}")
    raise

# Redis 연결 (Graceful Fallback)
redis_client = None
redis_connected = False

async def init_redis():
    global redis_client, redis_connected
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        await redis_client.ping()
        redis_connected = True
        logger.info("✅ Redis 연결 성공")
    except Exception as e:
        logger.warning(f"⚠️ Redis 연결 실패: {e}")
        logger.info("🔄 Redis 없이 기본 기능으로 실행됩니다.")
        redis_connected = False

# FAISS 임베딩 시스템
class EmbeddingManager:
    def __init__(self):
        self.model = None
        self.index = None
        self.embeddings = []
        self.messages = []
        self.dimension = 384  # sentence-transformers 기본 차원
        self.available = False
        
    def initialize(self):
        if not FAISS_AVAILABLE:
            logger.warning("⚠️ FAISS 모듈이 사용할 수 없습니다. 기본 대화 시스템을 사용합니다.")
            return False
            
        try:
            # 한국어에 최적화된 모델 사용
            self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product for cosine similarity
            self.available = True
            logger.info("✅ FAISS 임베딩 시스템 초기화 성공")
            return True
        except Exception as e:
            logger.warning(f"⚠️ FAISS 임베딩 시스템 초기화 실패: {e}")
            logger.info("🔄 기본 대화 시스템을 사용합니다.")
            return False
    
    def add_message(self, message: str, role: str, session_id: str):
        """메시지를 임베딩하여 FAISS 인덱스에 추가"""
        if not self.available or self.model is None:
            return False
            
        try:
            # 메시지 임베딩 생성
            embedding = self.model.encode([message])[0]
            
            # FAISS 인덱스에 추가
            self.index.add(embedding.reshape(1, -1))
            
            # 메타데이터 저장
            self.messages.append({
                'message': message,
                'role': role,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })
            
            return True
        except Exception as e:
            logger.error(f"임베딩 추가 실패: {e}")
            return False
    
    def search_similar(self, query: str, k: int = 5):
        """유사한 메시지 검색"""
        if not self.available or self.model is None or self.index is None:
            return []
            
        try:
            # 쿼리 임베딩 생성
            query_embedding = self.model.encode([query])[0]
            
            # FAISS로 유사도 검색
            similarities, indices = self.index.search(
                query_embedding.reshape(1, -1), 
                min(k, len(self.messages))
            )
            
            # 결과 반환
            results = []
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if idx < len(self.messages):
                    results.append({
                        'message': self.messages[idx]['message'],
                        'role': self.messages[idx]['role'],
                        'session_id': self.messages[idx]['session_id'],
                        'similarity': float(similarity),
                        'timestamp': self.messages[idx]['timestamp']
                    })
            
            return results
        except Exception as e:
            logger.error(f"유사도 검색 실패: {e}")
            return []

# 전역 임베딩 매니저
embedding_manager = EmbeddingManager()

# 웹소켓 연결 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"새로운 웹소켓 연결: {len(self.active_connections)}개 활성")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"웹소켓 연결 해제: {len(self.active_connections)}개 활성")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# 유틸리티 함수들
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = users_collection.find_one({"email": email})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Lifespan 이벤트 핸들러 (deprecation 경고 해결)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 EORA AI 시스템 시작")
    
    # Redis 초기화
    await init_redis()
    
    # FAISS 임베딩 시스템 초기화
    if embedding_manager.initialize():
        logger.info("✅ FAISS 임베딩 시스템 로드 성공")
    else:
        logger.warning("⚠️ FAISS 임베딩 시스템 로드 실패 - 기본 대화 시스템을 사용합니다.")
    
    yield
    
    # Shutdown
    logger.info("🛑 EORA AI 시스템 종료")
    
    # Redis 연결 종료
    if redis_client:
        await redis_client.close()
    
    # MongoDB 연결 종료
    if client:
        client.close()

# FastAPI 앱 초기화
app = FastAPI(
    title="EORA AI System",
    description="감정 중심 인공지능 플랫폼",
    version="2.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 템플릿 및 정적 파일 설정
templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# 정적 파일 마운트
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# 라우트 정의
@app.get("/", response_class=HTMLResponse)
async def home(request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chat(request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/api_test", response_class=HTMLResponse)
async def api_test(request):
    return templates.TemplateResponse("api_test.html", {"request": request})

@app.get("/debug", response_class=HTMLResponse)
async def debug(request):
    return templates.TemplateResponse("debug.html", {"request": request})

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "mongodb": "connected" if client else "disconnected",
            "redis": "connected" if redis_connected else "disconnected",
            "openai": "available" if OPENAI_API_KEY else "unavailable",
            "faiss": "initialized" if embedding_manager.available else "uninitialized"
        }
    }

@app.post("/api/auth/register")
async def register(email: str, password: str):
    # 기존 사용자 확인
    if users_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 새 사용자 생성
    hashed_password = get_password_hash(password)
    user = {
        "email": email,
        "hashed_password": hashed_password,
        "created_at": datetime.now(),
        "points": 1000
    }
    
    result = users_collection.insert_one(user)
    user["_id"] = str(result.inserted_id)
    
    return {"message": "User registered successfully", "user_id": str(result.inserted_id)}

@app.post("/api/auth/login")
async def login(email: str, password: str):
    user = users_collection.find_one({"email": email})
    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/chat")
async def chat_api(message: str, session_id: str = "default", current_user: dict = Depends(get_current_user)):
    try:
        # 임베딩 매니저에 사용자 메시지 추가
        embedding_manager.add_message(message, "user", session_id)
        
        # 유사한 과거 대화 검색
        similar_messages = embedding_manager.search_similar(message, k=3)
        
        # 컨텍스트 구성
        context = ""
        if similar_messages:
            context = "관련된 과거 대화:\n"
            for msg in similar_messages:
                context += f"{msg['role']}: {msg['message']}\n"
            context += "\n"
        
        # OpenAI API 호출
        if OPENAI_API_KEY:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "당신은 EORA AI입니다. 감정을 이해하고 공감하는 AI 동반자입니다. 한국어로 대화해주세요."},
                        {"role": "user", "content": f"{context}사용자: {message}"}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                ai_response = response.choices[0].message.content
            except Exception as e:
                logger.error(f"OpenAI API 오류: {e}")
                ai_response = "죄송합니다. 현재 AI 서비스에 문제가 있습니다. 잠시 후 다시 시도해주세요."
        else:
            ai_response = "AI 서비스가 현재 사용할 수 없습니다. 관리자에게 문의해주세요."
        
        # AI 응답을 임베딩 매니저에 추가
        embedding_manager.add_message(ai_response, "assistant", session_id)
        
        # MongoDB에 대화 저장
        chat_log = {
            "session_id": session_id,
            "user_id": str(current_user["_id"]),
            "user_message": message,
            "ai_response": ai_response,
            "timestamp": datetime.now(),
            "similar_messages": similar_messages
        }
        chat_logs_collection.insert_one(chat_log)
        
        return {"response": ai_response, "session_id": session_id}
        
    except Exception as e:
        logger.error(f"채팅 API 오류: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/sessions")
async def get_sessions(current_user: dict = Depends(get_current_user)):
    try:
        sessions = list(sessions_collection.find({"user_id": str(current_user["_id"])}))
        for session in sessions:
            session["_id"] = str(session["_id"])
        return {"sessions": sessions}
    except Exception as e:
        logger.error(f"세션 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # 임베딩 매니저에 메시지 추가
            embedding_manager.add_message(message_data["message"], "user", session_id)
            
            # 유사한 과거 대화 검색
            similar_messages = embedding_manager.search_similar(message_data["message"], k=3)
            
            # AI 응답 생성 (간단한 응답)
            ai_response = f"세션 {session_id}에서 '{message_data['message']}'에 대한 응답입니다."
            
            # AI 응답을 임베딩 매니저에 추가
            embedding_manager.add_message(ai_response, "assistant", session_id)
            
            # 웹소켓으로 응답 전송
            await manager.send_personal_message(
                json.dumps({"response": ai_response, "session_id": session_id}),
                websocket
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 