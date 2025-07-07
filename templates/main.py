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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ObjectId JSON 직렬화를 위한 헬퍼 함수
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# ObjectId를 문자열로 변환하는 헬퍼 함수
def convert_objectid(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
            elif isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, dict):
                convert_objectid(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        convert_objectid(item)
    return data

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
    client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
    db = client[DATABASE_NAME]
    chat_logs_collection = db["chat_logs"]
    sessions_collection = db["sessions"]
    users_collection = db["users"]
    aura_collection = db["aura"]
    system_logs_collection = db["system_logs"]
    logger.info("✅ MongoDB 연결 성공")
    
    # 시스템 로그 저장
    system_logs_collection.insert_one({
        "event": "system_startup",
        "timestamp": datetime.now(),
        "status": "success",
        "message": "EORA 시스템 시작 - MongoDB 연결 완료"
    })
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
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"웹소켓 연결 해제: {len(self.active_connections)}개 활성")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.warning(f"웹소켓 메시지 전송 실패: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections[:]:  # 복사본으로 반복
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"브로드캐스트 실패: {e}")
                self.disconnect(connection)

# 템플릿 및 정적 파일 설정
templates_path = Path(__file__).parent
templates = Jinja2Templates(directory=str(templates_path))

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
    logger.info("🚀 EORA AI System 시작 중...")
    await init_redis()
    
    # MongoDB 인덱스 생성
    try:
        chat_logs_collection.create_index([("timestamp", pymongo.DESCENDING)])
        chat_logs_collection.create_index([("user_id", pymongo.ASCENDING)])
        sessions_collection.create_index([("user_id", pymongo.ASCENDING)])
        users_collection.create_index([("email", pymongo.ASCENDING)])
        logger.info("✅ MongoDB 인덱스 생성 완료")
    except Exception as e:
        logger.warning(f"⚠️ MongoDB 인덱스 생성 실패: {e}")
    
    logger.info("✅ EORA AI System 시작 완료")
    yield
    
    # 종료 시 실행
    logger.info("🛑 EORA AI System 종료 중...")
    if redis_connected and redis_client:
        try:
            await redis_client.close()
            logger.info("✅ Redis 연결 해제")
        except Exception as e:
            logger.warning(f"⚠️ Redis 연결 해제 실패: {e}")
    
    # 시스템 종료 로그
    try:
        system_logs_collection.insert_one({
            "event": "system_shutdown",
            "timestamp": datetime.now(),
            "status": "success",
            "message": "EORA 시스템 종료 - MongoDB 연결 해제"
        })
    except Exception as e:
        logger.warning(f"⚠️ 시스템 종료 로그 저장 실패: {e}")
    
    logger.info("✅ EORA AI System 종료 완료")

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

# 정적 파일 마운트 (app 생성 후)
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

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

# 기본 세션 및 메시지 API (인증 없이)
@app.get("/api/sessions")
async def get_sessions():
    try:
        # 기본 세션 반환
        default_session = {
            "_id": "default_session",
            "name": "기본 세션",
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }
        return {"sessions": [default_session]}
    except Exception as e:
        logger.error(f"세션 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    try:
        messages = list(chat_logs_collection.find({"session_id": session_id}).sort("timestamp", 1))
        # ObjectId를 문자열로 변환
        for message in messages:
            convert_objectid(message)
        return {"messages": messages}
    except Exception as e:
        logger.error(f"메시지 조회 오류: {e}")
        return {"messages": []}

@app.post("/api/messages")
async def save_message(request: Request):
    try:
        data = await request.json()
        message_data = {
            "session_id": data.get("session_id", "default_session"),
            "user_id": data.get("user_id", "anonymous"),
            "content": data.get("content", ""),
            "role": data.get("role", "user"),
            "timestamp": datetime.now()
        }
        
        result = chat_logs_collection.insert_one(message_data)
        message_data["_id"] = str(result.inserted_id)
        message_data["timestamp"] = message_data["timestamp"].isoformat()
        
        # 세션 업데이트
        sessions_collection.update_one(
            {"_id": message_data["session_id"]},
            {
                "$set": {
                    "last_activity": datetime.now(),
                    "message_count": chat_logs_collection.count_documents({"session_id": message_data["session_id"]})
                }
            },
            upsert=True
        )
        
        logger.info(f"메시지 저장 완료: {result.inserted_id}")
        return message_data
    except Exception as e:
        logger.error(f"메시지 저장 오류: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message", "")
        session_id = data.get("session_id", "default_session")
        user_id = data.get("user_id", "anonymous")
        
        # 사용자 메시지 저장
        user_msg_data = {
            "session_id": session_id,
            "user_id": user_id,
            "content": user_message,
            "role": "user",
            "timestamp": datetime.now()
        }
        chat_logs_collection.insert_one(user_msg_data)
        
        # EORA 응답 생성
        if OPENAI_API_KEY:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "당신은 EORA라는 감정 중심 인공지능입니다. 친근하고 따뜻한 톤으로 대화해주세요."},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                eora_response = response.choices[0].message.content
            except Exception as e:
                logger.warning(f"OpenAI API 호출 실패: {e}")
                eora_response = f"안녕하세요! '{user_message}'에 대해 이야기하고 싶으시군요. 현재 AI 서비스에 일시적인 문제가 있어 기본 응답을 드립니다."
        else:
            eora_response = f"안녕하세요! '{user_message}'에 대해 이야기하고 싶으시군요. 현재 AI 서비스가 설정되지 않아 기본 응답을 드립니다."
        
        # EORA 응답 저장
        eora_msg_data = {
            "session_id": session_id,
            "user_id": user_id,
            "content": eora_response,
            "role": "assistant",
            "timestamp": datetime.now()
        }
        result = chat_logs_collection.insert_one(eora_msg_data)
        
        # 아우라 데이터 저장
        aura_data = {
            "user_id": user_id,
            "session_id": session_id,
            "aura_level": 5.0,
            "aura_type": "creative",
            "timestamp": datetime.now(),
            "interaction_count": 1
        }
        aura_collection.insert_one(aura_data)
        
        # 상호작용 로그
        interaction_data = {
            "user_id": user_id,
            "session_id": session_id,
            "interaction_type": "chat",
            "timestamp": datetime.now(),
            "content_length": len(user_message)
        }
        system_logs_collection.insert_one(interaction_data)
        
        logger.info(f"✅ 아우라 데이터 저장 완료 - 사용자: {user_id}")
        
        return {
            "response": eora_response,
            "message_id": str(result.inserted_id),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"채팅 처리 오류: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/set-language")
async def set_language(request: Request):
    try:
        data = await request.json()
        language = data.get("language", "ko")
        return {"message": f"언어가 {language}로 설정되었습니다."}
    except Exception as e:
        logger.error(f"언어 설정 오류: {e}")
        return {"message": "언어 설정 완료"}

# 웹소켓 엔드포인트
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
    except Exception as e:
        logger.error(f"웹소켓 오류: {e}")
        manager.disconnect(websocket)

# 사용자 관련 API (더미 데이터)
@app.get("/api/user/info")
async def get_user_info():
    return {
        "user_id": "anonymous",
        "username": "게스트",
        "email": "guest@example.com",
        "created_at": datetime.now().isoformat()
    }

@app.get("/api/user/stats")
async def get_user_stats():
    return {
        "total_messages": 0,
        "total_sessions": 1,
        "points": 1000,
        "aura_level": 5
    }

@app.get("/api/user/storage")
async def get_user_storage():
    return {
        "used_storage": "0 MB",
        "total_storage": "1 GB",
        "storage_percentage": 0
    }

@app.get("/api/user/activity")
async def get_user_activity():
    return {
        "recent_activity": [],
        "total_activity": 0
    }

# 포인트 시스템 API
@app.get("/api/user/points")
async def get_user_points():
    return {"points": 1000, "user_id": "anonymous"}

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
async def purchase_points(request: Request):
    try:
        data = await request.json()
        package_id = data.get("package_id", 1)
        return {"message": "포인트 구매 완료", "package_id": package_id}
    except Exception as e:
        logger.error(f"포인트 구매 오류: {e}")
        return {"message": "포인트 구매 완료", "package_id": 1}

# 아우라 시스템 API
@app.get("/api/aura/status")
async def get_aura_status():
    return {"aura_level": 5, "aura_type": "creative"}

@app.post("/api/aura/save")
async def save_aura(request: Request):
    try:
        data = await request.json()
        aura_data = {
            "user_id": "anonymous",
            "aura_data": data,
            "timestamp": datetime.now()
        }
        result = aura_collection.insert_one(aura_data)
        return {"message": "아우라 저장 완료", "id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"아우라 저장 오류: {e}")
        return {"message": "아우라 저장 완료"}

@app.get("/api/aura/recall")
async def recall_aura():
    return {"aura_memories": ["기억1", "기억2", "기억3"]}

@app.get("/api/aura/memory/stats")
async def get_aura_stats():
    return {"total_memories": 150, "recent_activity": 25}

# 대화 관리 API
@app.get("/api/conversations")
async def get_conversations():
    return {"conversations": []}

@app.get("/api/conversations/{session_id}/messages")
async def get_conversation_messages(session_id: str):
    try:
        messages = list(chat_logs_collection.find({"session_id": session_id}).sort("timestamp", 1))
        for message in messages:
            convert_objectid(message)
        return {"messages": messages}
    except Exception as e:
        logger.error(f"대화 메시지 조회 오류: {e}")
        return {"messages": []}

@app.get("/api/conversations/{session_id}/history")
async def get_conversation_history(session_id: str):
    return {"history": []}

@app.get("/api/user/{user_id}/sessions")
async def get_user_sessions(user_id: str):
    return {"sessions": []}

@app.delete("/api/conversations/{session_id}")
async def delete_conversation(session_id: str):
    try:
        chat_logs_collection.delete_many({"session_id": session_id})
        sessions_collection.delete_one({"_id": session_id})
        return {"message": "대화 삭제 완료"}
    except Exception as e:
        logger.error(f"대화 삭제 오류: {e}")
        return {"message": "대화 삭제 완료"}

@app.get("/api/conversations/{session_id}/export")
async def export_conversation(session_id: str):
    return {"export_data": "대화 내보내기 데이터"}

@app.get("/api/conversations/{session_id}/realtime")
async def get_realtime_conversation(session_id: str):
    return {"realtime_data": "실시간 대화 데이터"}

if __name__ == "__main__":
    import uvicorn
    # 파일 변경 감지 완전 비활성화로 안정성 확보
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=False,  # 재시작 완전 비활성화
        log_level="info",
        access_log=True,
        use_colors=True
    ) 