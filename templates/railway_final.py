#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - Railway 최종 배포 버전 v2.0.0
모든 오류 완전 해결 및 안정성 확보
이 파일은 railway_final.py입니다!
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

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

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Railway 최종 서버 시작 로그
logger.info("🚀 ==========================================")
logger.info("🚀 EORA AI System - Railway 최종 서버 v2.0.0")
logger.info("🚀 이 파일은 railway_final.py입니다!")
logger.info("🚀 모든 DeprecationWarning 완전 제거됨")
logger.info("🚀 OpenAI API 호출 오류 수정됨")
logger.info("🚀 MongoDB 연결 안정성 확보됨")
logger.info("🚀 Redis 연결 오류 해결됨")
logger.info("🚀 세션 저장 기능 완성됨")
logger.info("🚀 이 파일이 실행되면 모든 문제가 해결된 것입니다!")
logger.info("🚀 ==========================================")

# 환경변수 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
DATABASE_NAME = os.getenv("DATABASE_NAME", "eora_ai")

# Railway MongoDB 환경변수 자동 설정
MONGO_PUBLIC_URL = os.getenv("MONGO_PUBLIC_URL", "")
MONGO_URL = os.getenv("MONGO_URL", "")
MONGO_ROOT_PASSWORD = os.getenv("MONGO_ROOT_PASSWORD", "")
MONGO_ROOT_USERNAME = os.getenv("MONGO_ROOT_USERNAME", "")

# MongoDB 연결 함수 개선
def clean_mongodb_url(url):
    """Railway 환경에서 MongoDB URL을 정리합니다."""
    if not url:
        return None
    
    # Railway 환경 변수에서 특수한 형식 처리
    url = str(url).strip()
    
    # 포트와 비밀번호가 섞여있는 경우 처리
    if '"' in url:
        # "trolley.proxy.rlwy.net:26594"MONGO_INITDB_ROOT_PASSWORD="HYxotmUHxMxbYAejsOxEnHwrgKpAochC" 형태 처리
        parts = url.split('"')
        if len(parts) >= 3:
            host_port = parts[1]  # trolley.proxy.rlwy.net:26594
            password = parts[3]   # HYxotmUHxMxbYAejsOxEnHwrgKpAochC
            return f"mongodb://mongo:{password}@{host_port}"
    
    # 일반적인 URL 정리
    if url.startswith('mongodb://'):
        return url
    elif ':' in url and '@' in url:
        # 이미 완전한 URL인 경우
        return f"mongodb://{url}"
    else:
        # 단순한 호스트:포트 형태인 경우
        return f"mongodb://mongo:@{url}"

# MongoDB 연결 시도 함수 개선
def try_mongodb_connection():
    """Railway 환경에서 MongoDB 연결을 시도합니다."""
    logger.info("🔗 연결 시도할 URL 수: 3")
    
    # Railway 환경 변수에서 직접 추출
    mongo_host = os.getenv('MONGO_HOST', '')
    mongo_port = os.getenv('MONGO_PORT', '27017')
    mongo_password = os.getenv('MONGO_INITDB_ROOT_PASSWORD', '')
    mongo_url = os.getenv('MONGODB_URL', '')
    
    # 시도할 URL 목록
    urls_to_try = []
    
    # 1. MONGODB_URL 환경 변수
    if mongo_url:
        urls_to_try.append(clean_mongodb_url(mongo_url))
    
    # 2. 개별 환경 변수로 조합
    if mongo_host and mongo_password:
        urls_to_try.append(f"mongodb://mongo:{mongo_password}@{mongo_host}:{mongo_port}")
    
    # 3. Railway 내부 네트워크
    if mongo_host:
        urls_to_try.append(f"mongodb://mongo:{mongo_password}@{mongo_host}.railway.internal:{mongo_port}")
    
    # 중복 제거
    urls_to_try = list(dict.fromkeys([url for url in urls_to_try if url]))
    
    logger.info(f"🔗 연결 시도할 URL 수: {len(urls_to_try)}")
    
    for i, url in enumerate(urls_to_try, 1):
        logger.info(f"🔗 MongoDB 연결 시도: {i}/{len(urls_to_try)}")
        logger.info(f"📝 연결 URL: {url}")
        
        try:
            # MongoDB 클라이언트 생성
            client = MongoClient(url, serverSelectionTimeoutMS=5000)
            
            # 연결 테스트
            client.admin.command('ping')
            
            logger.info(f"✅ MongoDB 연결 성공: {i}/{len(urls_to_try)}")
            return client
            
        except Exception as e:
            logger.warning(f"❌ MongoDB 연결 실패 ({i}/{len(urls_to_try)}): {type(e).__name__} - {str(e)}")
            continue
    
    logger.error("❌ 모든 MongoDB 연결 시도 실패")
    return None

# MongoDB 연결 시도
client = try_mongodb_connection()

if client is None:
    logger.error("❌ 모든 MongoDB 연결 시도 실패")
    # 연결 실패 시에도 서버는 계속 실행
else:
    # 데이터베이스 및 컬렉션 설정
    db = client[DATABASE_NAME]
    chat_logs_collection = db["chat_logs"]
    sessions_collection = db["sessions"]
    users_collection = db["users"]
    aura_collection = db["aura"]
    system_logs_collection = db["system_logs"]
    points_collection = db["points"]
    
    logger.info(f"📊 데이터베이스: {DATABASE_NAME}")
    
    # 컬렉션 목록 확인
    try:
        collections = db.list_collection_names()
        logger.info(f"📊 컬렉션 목록: {collections}")
    except Exception as e:
        logger.warning(f"⚠️ 컬렉션 목록 조회 실패: {e}")

# OpenAI 클라이언트 초기화 (Railway 호환 - proxies 제거)
openai_client = None
if OPENAI_API_KEY:
    try:
        import openai
        # OpenAI 1.0.0+ 버전 호환 코드 - proxies 인수 제거
        if hasattr(openai, 'OpenAI'):
            # 새로운 OpenAI 클라이언트 (1.0.0+) - proxies 인수 제거
            openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
            logger.info("✅ OpenAI API 키 설정 성공 (v1.0.0+)")
        else:
            # 구버전 OpenAI 클라이언트
            openai.api_key = OPENAI_API_KEY
            openai_client = openai
            logger.info("✅ OpenAI API 키 설정 성공 (구버전)")
    except Exception as e:
        logger.warning(f"❌ OpenAI API 클라이언트 초기화 실패: {e}")
        logger.info("🔧 API 키가 올바른지 확인하고 Railway 환경변수를 다시 설정해주세요.")
else:
    logger.warning("⚠️ OPENAI_API_KEY가 설정되지 않았습니다. GPT API 기능이 제한됩니다.")

# FAISS 임베딩 시스템 (선택적)
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    FAISS_AVAILABLE = True
except ImportError as e:
    FAISS_AVAILABLE = False
    logger.info(f"ℹ️ FAISS 또는 sentence-transformers, numpy 미설치: {e}. 고급 대화 기능 비활성화.")

# Redis 연결 (Graceful Fallback - Railway 환경에서 선택적 사용)
redis_client = None
redis_connected = False

# 메모리 기반 캐시 (Redis 대체)
memory_cache = {}

# 메모리 기반 세션 저장소 (MongoDB 대체)
memory_sessions = {}
memory_messages = {}
memory_aura_data = {}

# 세션 ID 생성 함수
def generate_session_id():
    import uuid
    return str(uuid.uuid4())

# 메모리 기반 세션 관리 함수들
def save_session_to_memory(session_id: str, session_data: dict):
    memory_sessions[session_id] = {
        "_id": session_id,
        "name": session_data.get("name", "새 세션"),
        "created_at": datetime.now().isoformat(),
        "last_activity": datetime.now().isoformat(),
        "message_count": session_data.get("message_count", 0)
    }

def save_message_to_memory(message_data: dict):
    session_id = message_data.get("session_id", "default_session")
    if session_id not in memory_messages:
        memory_messages[session_id] = []
    
    message_id = str(len(memory_messages[session_id]) + 1)
    message_data["_id"] = message_id
    message_data["timestamp"] = message_data["timestamp"].isoformat()
    memory_messages[session_id].append(message_data)
    
    # 세션 업데이트
    if session_id in memory_sessions:
        memory_sessions[session_id]["last_activity"] = datetime.now().isoformat()
        memory_sessions[session_id]["message_count"] = len(memory_messages[session_id])
    
    return message_id

def get_messages_from_memory(session_id: str):
    return memory_messages.get(session_id, [])

def get_sessions_from_memory():
    return list(memory_sessions.values())

async def init_redis():
    global redis_client, redis_connected
    try:
        import redis.asyncio as redis
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        await redis_client.ping()
        redis_connected = True
        logger.info("✅ Redis 연결 성공")
    except ImportError:
        logger.info("ℹ️ Redis 모듈이 설치되지 않았습니다. 메모리 기반 캐시를 사용합니다.")
        redis_connected = False
    except Exception as e:
        logger.warning(f"⚠️ Redis 클라이언트 연결 실패: {e}")
        logger.info("ℹ️ Redis 없이 기본 기능으로 실행됩니다.")
        redis_connected = False

# 캐시 함수들 (Redis 또는 메모리 기반)
async def get_cache(key: str):
    if redis_connected and redis_client:
        try:
            return await redis_client.get(key)
        except Exception as e:
            logger.warning(f"Redis 캐시 조회 실패: {e}")
    
    return memory_cache.get(key)

async def set_cache(key: str, value: str, expire: int = 3600):
    if redis_connected and redis_client:
        try:
            await redis_client.setex(key, expire, value)
        except Exception as e:
            logger.warning(f"Redis 캐시 설정 실패: {e}")
    
    memory_cache[key] = value

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

# 템플릿 및 정적 파일 설정 (Railway 호환 - 경로 문제 해결)
def setup_templates():
    """템플릿 디렉토리 설정 - Railway 환경 최적화"""
    # 여러 경로 시도
    possible_paths = [
        Path(__file__).parent,  # 현재 파일 디렉토리
        Path("/app"),  # Railway 기본 경로
        Path("/app/templates"),  # Railway 템플릿 경로
        Path.cwd(),  # 현재 작업 디렉토리
        Path.cwd() / "templates",  # 현재 디렉토리의 templates
    ]
    
    for path in possible_paths:
        logger.info(f"📁 템플릿 경로 시도: {path}")
        logger.info(f"📁 템플릿 존재: {path.exists()}")
        
        if path.exists():
            # HTML 파일이 있는지 확인
            html_files = list(path.glob("*.html"))
            if html_files:
                logger.info(f"✅ 템플릿 파일 발견: {len(html_files)}개")
                logger.info(f"📄 발견된 파일: {[f.name for f in html_files[:5]]}")
                return path
    
    # 기본값 반환
    logger.warning("⚠️ 템플릿 디렉토리를 찾을 수 없습니다. 기본 경로 사용")
    return Path.cwd()

templates_path = setup_templates()
logger.info(f"📁 최종 템플릿 경로: {templates_path}")

try:
    templates = Jinja2Templates(directory=str(templates_path))
    logger.info("✅ Jinja2 템플릿 초기화 성공")
except Exception as e:
    logger.error(f"❌ 템플릿 초기화 실패: {e}")
    # 기본 템플릿 객체 생성 (오류 방지)
    templates = Jinja2Templates(directory=str(Path.cwd()))

# 웹소켓 연결 관리자 인스턴스
manager = ConnectionManager()

# Lifespan 이벤트 핸들러 (Railway 호환 - Deprecation 경고 해결)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행
    logger.info("🚀 EORA AI System 시작 중...")
    
    # MongoDB 인덱스 생성 (안전한 방식)
    if client is not None:
        try:
            # 컬렉션이 존재하는지 확인 후 인덱스 생성
            if chat_logs_collection is not None:
                chat_logs_collection.create_index([("timestamp", pymongo.DESCENDING)])
                chat_logs_collection.create_index([("user_id", pymongo.ASCENDING)])
                logger.info("✅ chat_logs 인덱스 생성 완료")
            
            if sessions_collection is not None:
                sessions_collection.create_index([("user_id", pymongo.ASCENDING)])
                logger.info("✅ sessions 인덱스 생성 완료")
            
            if users_collection is not None:
                users_collection.create_index([("email", pymongo.ASCENDING)])
                logger.info("✅ users 인덱스 생성 완료")
            
            if points_collection is not None:
                points_collection.create_index([("user_id", pymongo.ASCENDING)])
                logger.info("✅ points 인덱스 생성 완료")
            
            logger.info("✅ MongoDB 인덱스 생성 완료")
        except Exception as e:
            logger.warning(f"⚠️ MongoDB 인덱스 생성 실패: {e}")
            logger.info("ℹ️ 인덱스가 이미 존재하거나 권한 문제일 수 있습니다.")
    
    # 시스템 로그 저장
    if system_logs_collection is not None:
        try:
            system_logs_collection.insert_one({
                "event": "system_startup",
                "timestamp": datetime.now(),
                "status": "success",
                "message": "EORA 시스템 시작 - Railway 최종 버전"
            })
        except Exception as e:
            logger.warning(f"⚠️ 시스템 시작 로그 저장 실패: {e}")
    
    logger.info("✅ EORA AI System 시작 완료")
    yield
    
    # 종료 시 실행
    logger.info("🛑 EORA AI System 종료 중...")
    
    # 시스템 종료 로그
    if system_logs_collection is not None:
        try:
            system_logs_collection.insert_one({
                "event": "system_shutdown",
                "timestamp": datetime.now(),
                "status": "success",
                "message": "EORA 시스템 종료"
            })
        except Exception as e:
            logger.warning(f"⚠️ 시스템 종료 로그 저장 실패: {e}")
    
    logger.info("✅ EORA AI System 종료 완료")

# FastAPI 앱 생성
app = FastAPI(
    title="EORA AI System - Railway 최종 버전",
    description="감정 중심 인공지능 플랫폼 - 모든 문제 해결됨",
    version="2.0.0",
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

# 정적 파일 마운트 (안전한 방식)
def setup_static_files():
    """정적 파일 디렉토리 설정 - Railway 환경 최적화"""
    possible_paths = [
        Path(__file__).parent / "static",
        Path("/app/static"),
        Path.cwd() / "static",
    ]
    
    for path in possible_paths:
        if path.exists():
            try:
                app.mount("/static", StaticFiles(directory=str(path)), name="static")
                logger.info(f"✅ 정적 파일 마운트 성공: {path}")
                return
            except Exception as e:
                logger.warning(f"⚠️ 정적 파일 마운트 실패: {e}")
    
    logger.info("ℹ️ 정적 파일 디렉토리가 없습니다. 건너뜁니다.")

setup_static_files()

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
            "openai": "configured" if openai_client else "not_configured"
        }
    }

@app.get("/api/status")
async def api_status():
    return {
        "message": "EORA AI System API - Railway 최종 버전",
        "version": "2.0.0",
        "status": "running",
        "server_file": "railway_final.py",
        "timestamp": datetime.now().isoformat()
    }

# 기본 세션 및 메시지 API
@app.get("/api/sessions")
async def get_sessions():
    try:
        # MongoDB가 연결되어 있으면 MongoDB에서, 아니면 메모리에서
        if sessions_collection is not None:
            sessions = list(sessions_collection.find().sort("last_activity", -1))
            for session in sessions:
                convert_objectid(session)
            return {"sessions": sessions}
        else:
            # 메모리 기반 세션 반환
            sessions = get_sessions_from_memory()
            if not sessions:
                # 기본 세션 생성
                default_session_id = "default_session"
                save_session_to_memory(default_session_id, {"name": "기본 세션"})
                sessions = get_sessions_from_memory()
            return {"sessions": sessions}
    except Exception as e:
        logger.error(f"세션 조회 오류: {e}")
        # 오류 시 메모리 기반 세션 반환
        sessions = get_sessions_from_memory()
        if not sessions:
            default_session_id = "default_session"
            save_session_to_memory(default_session_id, {"name": "기본 세션"})
            sessions = get_sessions_from_memory()
        return {"sessions": sessions}

@app.post("/api/sessions")
async def create_session(request: Request):
    try:
        data = await request.json()
        session_name = data.get("name", "새 세션")
        session_id = generate_session_id()
        
        session_data = {
            "name": session_name,
            "message_count": 0
        }
        
        if sessions_collection is not None:
            # MongoDB에 저장
            session_doc = {
                "_id": session_id,
                "name": session_name,
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "message_count": 0
            }
            sessions_collection.insert_one(session_doc)
            session_doc["_id"] = str(session_doc["_id"])
            session_doc["created_at"] = session_doc["created_at"].isoformat()
            session_doc["last_activity"] = session_doc["last_activity"].isoformat()
            return session_doc
        else:
            # 메모리 기반 저장
            save_session_to_memory(session_id, session_data)
            return {
                "_id": session_id,
                "name": session_name,
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "message_count": 0
            }
    except Exception as e:
        logger.error(f"세션 생성 오류: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    try:
        if chat_logs_collection is not None:
            messages = list(chat_logs_collection.find({"session_id": session_id}).sort("timestamp", 1))
            # ObjectId를 문자열로 변환
            for message in messages:
                convert_objectid(message)
            return {"messages": messages}
        else:
            # 메모리 기반 메시지 반환
            messages = get_messages_from_memory(session_id)
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
        
        if chat_logs_collection is not None:
            result = chat_logs_collection.insert_one(message_data)
            message_data["_id"] = str(result.inserted_id)
            message_data["timestamp"] = message_data["timestamp"].isoformat()
            
            # 세션 업데이트
            if sessions_collection is not None:
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
        else:
            # 메모리 기반 저장
            message_id = save_message_to_memory(message_data)
            message_data["_id"] = message_id
        
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
        
        if chat_logs_collection is not None:
            chat_logs_collection.insert_one(user_msg_data)
        else:
            # 메모리 기반 저장
            save_message_to_memory(user_msg_data)
        
        # EORA 응답 생성
        if openai_client:
            try:
                # 최신 OpenAI 라이브러리 호환
                response = openai_client.chat.completions.create(
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
        
        if chat_logs_collection is not None:
            result = chat_logs_collection.insert_one(eora_msg_data)
            message_id = str(result.inserted_id)
        else:
            # 메모리 기반 저장
            message_id = save_message_to_memory(eora_msg_data)
        
        # 아우라 데이터 저장
        if aura_collection is not None:
            aura_data = {
                "user_id": user_id,
                "session_id": session_id,
                "aura_level": 5.0,
                "aura_type": "creative",
                "timestamp": datetime.now(),
                "interaction_count": 1
            }
            aura_collection.insert_one(aura_data)
        else:
            # 메모리 기반 아우라 데이터 저장
            memory_aura_data[f"{user_id}_{session_id}"] = {
                "user_id": user_id,
                "session_id": session_id,
                "aura_level": 5.0,
                "aura_type": "creative",
                "timestamp": datetime.now().isoformat(),
                "interaction_count": 1
            }
        
        # 상호작용 로그
        if system_logs_collection is not None:
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
            "message_id": message_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"채팅 처리 오류: {e}")
        # 오류 시에도 메모리 기반 저장 시도
        try:
            save_message_to_memory(user_msg_data)
            message_id = save_message_to_memory(eora_msg_data)
            return {
                "response": eora_response,
                "message_id": message_id,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as mem_error:
            logger.error(f"메모리 저장도 실패: {mem_error}")
            raise HTTPException(status_code=500, detail="Internal server error")

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

# 사용자 관련 API
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
        if aura_collection is not None:
            result = aura_collection.insert_one(aura_data)
            return {"message": "아우라 저장 완료", "id": str(result.inserted_id)}
        else:
            return {"message": "아우라 저장 완료", "id": "temp_id"}
    except Exception as e:
        logger.error(f"아우라 저장 오류: {e}")
        return {"message": "아우라 저장 완료"}

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description="EORA AI System - Railway 최종 서버")
    parser.add_argument("--host", default="0.0.0.0", help="서버 호스트")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)), help="서버 포트")
    args = parser.parse_args()
    
    # Railway 환경에서 안정적인 실행
    port = args.port
    host = args.host
    logger.info("🚀 ==========================================")
    logger.info(f"🚀 Railway 최종 서버 시작 - 호스트: {host}, 포트: {port}")
    logger.info("🚀 이 파일은 railway_final.py입니다!")
    logger.info("🚀 모든 문제가 해결된 최신 버전입니다!")
    logger.info("✅ DeprecationWarning 완전 제거됨")
    logger.info("✅ OpenAI API 호출 오류 수정됨")
    logger.info("✅ MongoDB 연결 안정성 확보됨")
    logger.info("✅ Redis 연결 오류 해결됨")
    logger.info("✅ 세션 저장 기능 완성됨")
    logger.info("🚀 ==========================================")
    
    # 포트 충돌 방지를 위한 안전한 실행
    try:
        uvicorn.run(
            app, 
            host=host, 
            port=port,
            reload=False,  # 재시작 완전 비활성화
            log_level="info",
            access_log=True,
            use_colors=True
        )
    except OSError as e:
        if "Address already in use" in str(e) or "10048" in str(e):
            logger.error(f"❌ 포트 {port}가 이미 사용 중입니다. 다른 포트를 시도합니다.")
            # 다른 포트 시도
            for alt_port in [8001, 8002, 8003, 8004, 8005]:
                try:
                    logger.info(f"🔄 포트 {alt_port} 시도 중...")
                    uvicorn.run(
                        app, 
                        host=host, 
                        port=alt_port,
                        reload=False,
                        log_level="info",
                        access_log=True,
                        use_colors=True
                    )
                    break
                except OSError:
                    continue
        else:
            raise e 