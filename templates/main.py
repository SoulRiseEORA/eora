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
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, status, Request
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

# 인증 및 보안
import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# 환경변수 로드
load_dotenv()

# 환경변수 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
DATABASE_NAME = os.getenv("DATABASE_NAME", "eora_ai")

# OpenAI 클라이언트 초기화
if OPENAI_API_KEY:
    try:
        openai.api_key = OPENAI_API_KEY
        logger.info("✅ OpenAI API 키 설정 성공")
    except Exception as e:
        logger.warning(f"⚠️ OpenAI API 키 설정 실패: {e}")
        logger.info("🔧 API 키가 올바른지 확인하고 Railway 환경변수를 다시 설정해주세요.")
else:
    logger.warning("⚠️ OPENAI_API_KEY가 설정되지 않았습니다. GPT API 기능이 제한됩니다.")

# MongoDB 연결
try:
    client = MongoClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    chat_logs_collection = db["chat_logs"]
    sessions_collection = db["sessions"]
    users_collection = db["users"]
    aura_collection = db["aura"]
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
        logger.warning(f"⚠️ Redis 클라이언트 연결 실패: {e}")
        logger.info("ℹ️ Redis 없이 기본 기능으로 실행됩니다.")
        redis_connected = False

# FAISS 임베딩 매니저
class EmbeddingManager:
    def __init__(self):
        self.model = None
        self.index = None
        self.conversations = []
        
        if FAISS_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.index = faiss.IndexFlatIP(384)  # 384차원 임베딩
                logger.info("✅ FAISS 임베딩 매니저 초기화 성공")
            except Exception as e:
                logger.warning(f"⚠️ FAISS 임베딩 매니저 초기화 실패: {e}")
    
    def add_conversation(self, conversation_id: str, messages: List[str]):
        if not FAISS_AVAILABLE or not self.model:
            return
            
        try:
            # 메시지들을 하나의 텍스트로 결합
            text = " ".join(messages)
            embedding = self.model.encode([text])
            self.index.add(embedding)
            self.conversations.append(conversation_id)
            logger.info(f"✅ 대화 임베딩 추가: {conversation_id}")
        except Exception as e:
            logger.warning(f"⚠️ 대화 임베딩 추가 실패: {e}")
    
    def find_similar(self, query: str, k: int = 5):
        if not FAISS_AVAILABLE or not self.model:
            return []
            
        try:
            query_embedding = self.model.encode([query])
            scores, indices = self.index.search(query_embedding, k)
            return [(self.conversations[i], scores[0][j]) for j, i in enumerate(indices[0]) if i < len(self.conversations)]
        except Exception as e:
            logger.warning(f"⚠️ 유사 대화 검색 실패: {e}")
            return []

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

# 템플릿 및 정적 파일 설정
templates_path = Path(__file__).parent
templates = Jinja2Templates(directory=str(templates_path))

# 정적 파일 마운트
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# 전역 임베딩 매니저
embedding_manager = EmbeddingManager()

# 웹소켓 연결 관리자 인스턴스
manager = ConnectionManager()

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 토큰 검증
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

def get_current_user(token: dict = Depends(verify_token)):
    user_id = token.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"_id": user_id}

# Lifespan 이벤트 핸들러
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행
    await init_redis()
    
    # MongoDB 인덱스 생성
    try:
        chat_logs_collection.create_index([("timestamp", pymongo.DESCENDING)])
        chat_logs_collection.create_index([("user_id", pymongo.ASCENDING)])
        sessions_collection.create_index([("user_id", pymongo.ASCENDING)])
        users_collection.create_index([("email", pymongo.ASCENDING)])
        logger.info("✅ MongoDB 인덱스 생성 완료")
    except Exception as e:
        logger.warning(f"⚠️ chat_logs 인덱스 생성 실패: {e}")
    
    yield
    
    # 종료 시 실행
    if redis_connected and redis_client:
        await redis_client.close()
        logger.info("✅ Redis 연결 해제")

# FastAPI 앱 생성
app = FastAPI(
    title="EORA AI System",
    description="감정 중심 인공지능 플랫폼",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우트 정의
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/debug", response_class=HTMLResponse)
async def debug(request: Request):
    return templates.TemplateResponse("debug.html", {"request": request})

@app.get("/simple-chat", response_class=HTMLResponse)
async def simple_chat(request: Request):
    return templates.TemplateResponse("test_chat_simple.html", {"request": request})

@app.get("/points", response_class=HTMLResponse)
async def points(request: Request):
    return templates.TemplateResponse("points.html", {"request": request})

@app.get("/memory", response_class=HTMLResponse)
async def memory(request: Request):
    return templates.TemplateResponse("memory.html", {"request": request})

@app.get("/prompts", response_class=HTMLResponse)
async def prompts(request: Request):
    return templates.TemplateResponse("prompts.html", {"request": request})

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "mongodb": "connected" if client else "disconnected",
            "redis": "connected" if redis_connected else "disconnected",
            "openai": "configured" if OPENAI_API_KEY else "not_configured",
            "faiss": "available" if FAISS_AVAILABLE else "not_available"
        }
    }

@app.get("/api/status")
async def api_status():
    return {
        "message": "EORA AI System API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

# API 엔드포인트들
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
            
            # 메시지 처리
            response = {
                "type": "message",
                "content": f"Echo: {message_data.get('content', '')}",
                "timestamp": datetime.now().isoformat()
            }
            
            await manager.send_personal_message(json.dumps(response), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# 추가 API 엔드포인트들...
@app.get("/api/user/points")
async def get_user_points(current_user: dict = Depends(get_current_user)):
    return {"points": 1000, "user_id": str(current_user["_id"])}

@app.get("/api/points/packages")
async def get_point_packages():
    return {
        "packages": [
            {"id": 1, "name": "기본 패키지", "points": 100, "price": 1000},
            {"id": 2, "name": "프리미엄 패키지", "points": 500, "price": 5000},
            {"id": 3, "name": "VIP 패키지", "points": 1000, "price": 10000}
        ]
    }

@app.post("/api/points/purchase")
async def purchase_points(package_id: int, current_user: dict = Depends(get_current_user)):
    return {"message": "포인트 구매 완료", "package_id": package_id}

# 아우라 시스템 API
@app.get("/api/aura/status")
async def get_aura_status(current_user: dict = Depends(get_current_user)):
    return {"aura_level": 5, "aura_type": "creative"}

@app.post("/api/aura/save")
async def save_aura(aura_data: dict, current_user: dict = Depends(get_current_user)):
    return {"message": "아우라 저장 완료"}

@app.get("/api/aura/recall")
async def recall_aura(current_user: dict = Depends(get_current_user)):
    return {"aura_memories": ["기억1", "기억2", "기억3"]}

@app.get("/api/aura/memory/stats")
async def get_aura_stats(current_user: dict = Depends(get_current_user)):
    return {"total_memories": 150, "recent_activity": 25}

# 대화 불러오기 API
@app.get("/api/conversations")
async def get_conversations(current_user: dict = Depends(get_current_user)):
    return {"conversations": []}

@app.get("/api/conversations/{session_id}/messages")
async def get_session_messages(session_id: str, current_user: dict = Depends(get_current_user)):
    return {"messages": []}

@app.get("/api/conversations/{session_id}/history")
async def get_conversation_history(session_id: str, current_user: dict = Depends(get_current_user)):
    return {"history": []}

@app.get("/api/user/{user_id}/sessions")
async def get_user_sessions(user_id: str, current_user: dict = Depends(get_current_user)):
    return {"sessions": []}

@app.delete("/api/conversations/{session_id}")
async def delete_conversation(session_id: str, current_user: dict = Depends(get_current_user)):
    return {"message": "대화 삭제 완료"}

@app.get("/api/conversations/{session_id}/export")
async def export_conversation(session_id: str, current_user: dict = Depends(get_current_user)):
    return {"export_data": "대화 내보내기 데이터"}

@app.get("/api/conversations/{session_id}/realtime")
async def get_realtime_conversation(session_id: str, current_user: dict = Depends(get_current_user)):
    return {"realtime_data": "실시간 대화 데이터"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8016) 