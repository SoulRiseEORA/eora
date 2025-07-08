#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 감정 중심 인공지능 플랫폼
Railway 배포 최적화 버전 - 점진적 업데이트
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import time
import uuid

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

# 로깅 설정 (먼저 설정)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Redis 연결 (선택적 - Railway 환경에서 사용하지 않음)
REDIS_AVAILABLE = False
redis_client = None
redis_connected = False

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
    logger.info("✅ Redis 모듈 로드 성공")
except ImportError:
    logger.info("ℹ️ Redis 모듈이 설치되지 않았습니다. 메모리 기반 캐시를 사용합니다.")

# AI 및 임베딩 (선택적)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# FAISS 임베딩 시스템 (선택적)
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

# 인증 및 보안
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

try:
    from passlib.context import CryptContext
    PASSLIB_AVAILABLE = True
except ImportError:
    PASSLIB_AVAILABLE = False

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# 환경변수 로드
if DOTENV_AVAILABLE:
    load_dotenv()

# 환경변수 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
DATABASE_NAME = os.getenv("DATABASE_NAME", "eora_ai")

# OpenAI 클라이언트 초기화 (Railway 호환 - proxies 인수 제거)
openai_client = None
if OPENAI_API_KEY and OPENAI_AVAILABLE:
    try:
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
    if not OPENAI_API_KEY:
        logger.warning("⚠️ OPENAI_API_KEY가 설정되지 않았습니다. GPT API 기능이 제한됩니다.")
    if not OPENAI_AVAILABLE:
        logger.warning("⚠️ OpenAI 모듈이 설치되지 않았습니다. GPT API 기능이 제한됩니다.")

# MongoDB 연결 (Railway 환경 최적화)
client = None
db = None
chat_logs_collection = None
sessions_collection = None
users_collection = None
aura_collection = None
system_logs_collection = None

def clean_mongodb_url(url):
    """MongoDB URL 정리 함수 - Railway 환경 특수 케이스 처리"""
    if not url:
        return url
    
    # 따옴표 제거
    url = url.strip('"').strip("'")
    
    # Railway 환경에서 발생하는 특수한 URL 패턴 처리
    if '"MONGO_INITDB_ROOT_PASSWORD=' in url:
        # URL에서 비밀번호 부분 분리
        parts = url.split('"MONGO_INITDB_ROOT_PASSWORD=')
        if len(parts) > 1:
            base_url = parts[0]
            password_part = parts[1]
            # 비밀번호 추출 (공백이나 특수문자로 끝나는 부분까지)
            password = password_part.split()[0] if ' ' in password_part else password_part
            # 올바른 MongoDB URL 형식으로 재구성
            if '@' in base_url:
                # 이미 인증 정보가 있는 경우
                url = base_url + password
            else:
                # 인증 정보가 없는 경우
                url = base_url.replace('mongodb://', f'mongodb://root:{password}@')
    
    # 포트 파싱 오류 수정
    if '26594"MONGO_INITDB_ROOT_PASSWORD=' in url:
        # Railway 환경에서 발생하는 특수한 포트 파싱 오류 처리
        url = url.replace('26594"MONGO_INITDB_ROOT_PASSWORD=', '27017?authSource=admin&authMechanism=SCRAM-SHA-1&password=')
    
    return url

try:
    # Railway 환경에서 MongoDB URL 파싱 문제 해결
    logger.info(f"🔗 연결 시도할 URL 수: 3")
    
    # 첫 번째 시도: 원본 URL
    logger.info(f"🔗 MongoDB 연결 시도: 1/3")
    logger.info(f"📝 연결 URL: {MONGODB_URL}")
    
    try:
        cleaned_url = clean_mongodb_url(MONGODB_URL)
        client = MongoClient(
            cleaned_url, 
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        client.admin.command('ping')
        logger.info("✅ MongoDB 연결 성공 (1/3)")
    except Exception as e1:
        logger.warning(f"❌ MongoDB 연결 실패 (1/3): {type(e1).__name__} - {e1}")
        
        # 두 번째 시도: Railway 내부 네트워크
        logger.info(f"🔗 MongoDB 연결 시도: 2/3")
        try:
            internal_url = "mongodb://mongo:@web.railway.internal:27017"
            logger.info(f"📝 연결 URL: {internal_url}")
            client = MongoClient(
                internal_url,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            client.admin.command('ping')
            logger.info("✅ MongoDB 연결 성공 (2/3)")
        except Exception as e2:
            logger.warning(f"❌ MongoDB 연결 실패 (2/3): {type(e2).__name__} - {e2}")
            
            # 세 번째 시도: 환경변수에서 직접 추출
            logger.info(f"🔗 MongoDB 연결 시도: 3/3")
            try:
                # Railway 환경변수에서 직접 추출
                mongo_host = os.getenv("MONGO_HOST", "")
                mongo_port = os.getenv("MONGO_PORT", "27017")
                mongo_user = os.getenv("MONGO_USER", "")
                mongo_password = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "")
                
                if mongo_host and mongo_password:
                    if mongo_user:
                        direct_url = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}"
                    else:
                        direct_url = f"mongodb://root:{mongo_password}@{mongo_host}:{mongo_port}"
                else:
                    direct_url = f"mongodb://localhost:27017"
                
                logger.info(f"📝 연결 URL: {direct_url}")
                client = MongoClient(
                    direct_url,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000,
                    socketTimeoutMS=5000
                )
                client.admin.command('ping')
                logger.info("✅ MongoDB 연결 성공 (3/3)")
            except Exception as e3:
                logger.warning(f"❌ MongoDB 연결 실패 (3/3): {type(e3).__name__} - {e3}")
                raise Exception("모든 MongoDB 연결 시도 실패")
    
    # 연결 성공 시 컬렉션 초기화
    db = client[DATABASE_NAME]
    chat_logs_collection = db["chat_logs"]
    sessions_collection = db["sessions"]
    users_collection = db["users"]
    aura_collection = db["aura"]
    system_logs_collection = db["system_logs"]
    
    logger.info("✅ MongoDB 연결 성공")
    logger.info(f"📊 데이터베이스: {DATABASE_NAME}")
    logger.info(f"📊 컬렉션 상태 - chat_logs: {'연결됨' if chat_logs_collection is not None else 'None'}, sessions: {'연결됨' if sessions_collection is not None else 'None'}")
    
    # 시스템 로그 저장
    if system_logs_collection is not None:
        try:
            system_logs_collection.insert_one({
                "event": "system_startup",
                "timestamp": datetime.now(),
                "status": "success",
                "message": "EORA 시스템 시작 - MongoDB 연결 완료"
            })
        except Exception as log_error:
            logger.warning(f"⚠️ 시스템 로그 저장 실패: {log_error}")
            
except Exception as e:
    logger.error(f"❌ 모든 MongoDB 연결 시도 실패")
    logger.warning("⚠️ MongoDB 연결 실패로 인해 일부 기능이 제한됩니다.")
    logger.info("🔧 Railway 환경변수 MONGODB_URL을 확인해주세요.")
    # MongoDB 연결 실패 시에도 서버는 계속 실행

# Redis 연결 (Graceful Fallback - Railway 환경에서 선택적 사용)
async def init_redis():
    global redis_client, redis_connected
    if not REDIS_AVAILABLE:
        logger.info("ℹ️ Redis 모듈이 사용 불가능합니다. 메모리 기반 캐시를 사용합니다.")
        return
        
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        await redis_client.ping()
        redis_connected = True
        logger.info("✅ Redis 연결 성공")
    except Exception as e:
        logger.warning(f"⚠️ Redis 클라이언트 연결 실패: {e}")
        logger.info("ℹ️ Redis 없이 기본 기능으로 실행됩니다.")
        redis_connected = False

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

# FAISS 임베딩 매니저 (선택적)
class EmbeddingManager:
    def __init__(self):
        self.model = None
        self.index = None
        self.conversations = []
        
        if FAISS_AVAILABLE and NUMPY_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.index = faiss.IndexFlatIP(384)  # 384차원 임베딩
                logger.info("✅ FAISS 임베딩 매니저 초기화 성공")
            except Exception as e:
                logger.warning(f"⚠️ FAISS 임베딩 매니저 초기화 실패: {e}")
        else:
            logger.info("ℹ️ FAISS 또는 NumPy가 사용 불가능합니다. 기본 대화 시스템을 사용합니다.")
    
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

# 전역 임베딩 매니저
embedding_manager = EmbeddingManager()

# 웹소켓 연결 관리자 인스턴스
manager = ConnectionManager()

# 비밀번호 해싱 (선택적)
if PASSLIB_AVAILABLE:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
else:
    pwd_context = None

# JWT 토큰 검증 (선택적)
if JWT_AVAILABLE:
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
else:
    security = None
    verify_token = None
    get_current_user = None

# Lifespan 이벤트 핸들러 (Railway 호환 - Deprecation 경고 해결)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행
    logger.info("🚀 EORA AI System 시작 중...")
    
    # Redis 초기화 (선택적)
    await init_redis()
    
    # MongoDB 인덱스 생성 (Railway 호환)
    if client is not None:
        try:
            # 컬렉션이 존재하는지 확인 후 인덱스 생성
            if chat_logs_collection is not None:
                chat_logs_collection.create_index([("timestamp", pymongo.DESCENDING)])
                chat_logs_collection.create_index([("user_id", pymongo.ASCENDING)])
            if sessions_collection is not None:
                sessions_collection.create_index([("user_id", pymongo.ASCENDING)])
            if users_collection is not None:
                users_collection.create_index([("email", pymongo.ASCENDING)])
            logger.info("✅ MongoDB 인덱스 생성 완료")
        except Exception as e:
            logger.warning(f"⚠️ MongoDB 인덱스 생성 실패: {e}")
            logger.info("ℹ️ 인덱스가 이미 존재하거나 권한 문제일 수 있습니다.")
    
    logger.info("✅ EORA AI System 시작 완료")
    yield
    
    # 종료 시 실행
    logger.info("🛑 EORA AI System 종료 중...")
    
    # Redis 연결 해제 (선택적)
    if redis_connected and redis_client and REDIS_AVAILABLE:
        try:
            await redis_client.close()
            logger.info("✅ Redis 연결 해제")
        except Exception as e:
            logger.warning(f"⚠️ Redis 연결 해제 실패: {e}")
    
    # 시스템 종료 로그
    if system_logs_collection is not None:
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
    description="감정 중심 인공지능 플랫폼 - Railway 최적화",
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

# 정적 파일 마운트 (app 생성 후) - Railway 호환
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
            "openai": "configured" if OPENAI_API_KEY and OPENAI_AVAILABLE else "not_configured",
            "faiss": "available" if FAISS_AVAILABLE else "not_available",
            "jwt": "available" if JWT_AVAILABLE else "not_available"
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

# 세션 관리 API
@app.get("/api/sessions")
async def get_sessions():
    try:
        if sessions_collection is not None:
            # null session_id 데이터 정리
            try:
                sessions_collection.delete_many({"session_id": None})
                logger.info("null session_id 데이터 정리 완료")
            except Exception as e:
                logger.warning(f"null session_id 정리 실패: {e}")
            
            # undefined, null, 빈 문자열 세션 ID 데이터 정리
            try:
                sessions_collection.delete_many({
                    "$or": [
                        {"session_id": "undefined"},
                        {"session_id": "null"},
                        {"session_id": ""},
                        {"session_id": {"$exists": False}}
                    ]
                })
                logger.info("유효하지 않은 session_id 데이터 정리 완료")
            except Exception as e:
                logger.warning(f"유효하지 않은 session_id 정리 실패: {e}")
            
            # MongoDB에서 실제 세션 목록 조회 (유효한 세션만)
            sessions = list(sessions_collection.find({
                "session_id": {
                    "$ne": None,
                    "$nin": ["undefined", "null", ""],
                    "$exists": True
                }
            }).sort("created_at", -1))
            
            # 추가 필터링: 유효하지 않은 세션 ID 완전 제거
            valid_sessions = []
            for session in sessions:
                session_id = session.get("session_id")
                
                # 완전한 유효성 검사
                if not session_id:
                    logger.warning(f"🚫 null/undefined 세션 ID 발견 및 제거")
                    continue
                    
                if not isinstance(session_id, str):
                    logger.warning(f"🚫 문자열이 아닌 세션 ID 발견 및 제거: {type(session_id)}")
                    continue
                
                session_id = session_id.strip()
                
                # undefined, null, 빈 문자열 완전 차단
                if (session_id == "undefined" or 
                    session_id == "null" or 
                    session_id == "" or
                    session_id.lower() == "undefined" or
                    session_id.lower() == "null" or
                    len(session_id) == 0):
                    logger.warning(f"🚫 유효하지 않은 세션 ID 발견 및 제거: '{session_id}'")
                    continue
                
                # session_ 접두사 또는 충분한 길이 확인
                if not session_id.startswith("session_") and len(session_id) < 10:
                    logger.warning(f"🚫 잘못된 세션 ID 형식 발견 및 제거: '{session_id}'")
                    continue
                
                # 프론트엔드 호환성을 위해 id 필드 추가
                session["id"] = session_id
                
                convert_objectid(session)
                valid_sessions.append(session)
                logger.debug(f"✅ 유효한 세션 추가: {session_id}")
            
            sessions = valid_sessions
            
            # 세션이 없으면 기본 세션 생성
            if not sessions:
                default_session = {
                    "_id": str(ObjectId()),
                    "session_id": "default",
                    "id": "default",  # 프론트엔드 호환성
                    "name": "기본 세션",
                    "created_at": datetime.now(),
                    "last_activity": datetime.now(),
                    "message_count": 0,
                    "user_id": "anonymous"
                }
                try:
                    sessions_collection.insert_one(default_session)
                    convert_objectid(default_session)
                    sessions = [default_session]
                    logger.info("기본 세션 생성 완료")
                except Exception as e:
                    logger.error(f"기본 세션 생성 실패: {e}")
                    # 메모리 기반 세션으로 fallback
                    default_session = {
                        "_id": "default",
                        "session_id": "default",
                        "id": "default",  # 프론트엔드 호환성
                        "name": "기본 세션",
                        "created_at": datetime.now().isoformat(),
                        "last_activity": datetime.now().isoformat(),
                        "message_count": 0,
                        "user_id": "anonymous"
                    }
                    sessions = [default_session]
            
            logger.info(f"세션 조회 완료: {len(sessions)}개 세션")
            return {"sessions": sessions}
        else:
            # MongoDB 연결 실패 시 기본 세션 반환
            default_session = {
                "_id": "default",
                "session_id": "default",
                "id": "default",  # 프론트엔드 호환성
                "name": "기본 세션",
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "message_count": 0,
                "user_id": "anonymous"
            }
            return {"sessions": [default_session]}
    except Exception as e:
        logger.error(f"세션 조회 오류: {e}")
        # 오류 시에도 기본 세션 반환
        default_session = {
            "_id": "default",
            "session_id": "default",
            "id": "default",  # 프론트엔드 호환성
            "name": "기본 세션",
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "message_count": 0,
            "user_id": "anonymous"
        }
        return {"sessions": [default_session]}

# 세션 생성 API에서 session_id 유효성 검사 추가
@app.post("/api/sessions")
async def create_session(request: Request):
    data = await request.json()
    session_id = data.get("id")
    if not session_id or str(session_id).lower() in ["undefined", "null", "", None]:
        # 강제 생성
        session_id = f"session_{int(time.time())}_{uuid.uuid4().hex[:12]}"
    session_name = data.get("name", f"세션 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    if sessions_collection is not None:
        try:
            sessions_collection.delete_many({"session_id": None})
            logger.info("null session_id 데이터 정리 완료")
        except Exception as e:
            logger.warning(f"null session_id 정리 실패: {e}")
        new_session = {
            "session_id": session_id,
            "id": session_id,  # 프론트엔드 호환성
            "name": session_name,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "message_count": 0,
            "user_id": data.get("user_id", "anonymous")
        }
        result = sessions_collection.insert_one(new_session)
        new_session["_id"] = str(result.inserted_id)
        convert_objectid(new_session)
        logger.info(f"새 세션 생성 완료 (MongoDB): {session_id}")
        return new_session
    else:
        new_session = {
            "_id": session_id,
            "session_id": session_id,
            "id": session_id,  # 프론트엔드 호환성
            "name": session_name,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "message_count": 0,
            "user_id": data.get("user_id", "anonymous")
        }
        logger.info(f"새 세션 생성 완료 (메모리): {session_id}")
        return new_session

@app.put("/api/sessions/{session_id}")
async def update_session(session_id: str, request: Request):
    try:
        data = await request.json()
        new_name = data.get("name", "")
        
        if not new_name:
            return {"error": "세션 이름이 필요합니다."}
        
        if sessions_collection is not None:
            result = sessions_collection.update_one(
                {"session_id": session_id},
                {"$set": {"name": new_name, "last_activity": datetime.now()}}
            )
            
            if result.modified_count > 0:
                logger.info(f"세션 이름 변경 완료: {session_id} -> {new_name}")
                return {"message": "세션 이름이 변경되었습니다.", "session_id": session_id, "name": new_name}
            else:
                logger.warning(f"세션 이름 변경 실패 - 세션을 찾을 수 없음: {session_id}")
                return {"error": "세션을 찾을 수 없습니다."}
        else:
            logger.warning("MongoDB 연결 없음 - 세션 이름 변경 불가")
            return {"error": "데이터베이스 연결 오류"}
    except Exception as e:
        logger.error(f"세션 이름 변경 오류: {e}")
        return {"error": "세션 이름 변경 실패"}

def is_valid_session_id(session_id):
    return (
        isinstance(session_id, str)
        and session_id
        and session_id != 'undefined'
        and session_id != 'null'
        and session_id.strip() != ''
    )

@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    if not is_valid_session_id(session_id):
        return JSONResponse(status_code=400, content={"error": "유효하지 않은 세션 ID입니다."})
    try:
        # undefined/null/빈 문자열 방지 및 실제 메시지가 있는 세션으로 보정
        if not session_id or session_id in ["undefined", "null", "", None]:
            # chat_logs에서 실제로 메시지가 있는 세션을 찾아서 보정
            if chat_logs_collection is not None:
                # 가장 최근에 메시지가 저장된 세션을 찾음
                recent_message = chat_logs_collection.find_one(
                    {"session_id": {"$ne": None}},
                    sort=[("timestamp", -1)]
                )
                if recent_message:
                    session_id = recent_message["session_id"]
                    logger.info(f"메시지 조회 세션 보정: {session_id}")
                else:
                    # 메시지가 없으면 default 세션 사용 (채팅 API에서 사용하는 세션)
                    session_id = "default"
                    logger.info(f"기본 세션 사용: {session_id}")
            else:
                session_id = "default"
                logger.info(f"기본 세션 사용 (MongoDB 연결 없음): {session_id}")
        
        if chat_logs_collection is not None:
            messages = list(chat_logs_collection.find({"session_id": session_id}).sort("timestamp", 1))
            for message in messages:
                convert_objectid(message)
            logger.info(f"세션 메시지 조회: {session_id}, 메시지 수: {len(messages)}")
            return {"messages": messages}
        else:
            logger.info(f"메모리 기반 메시지 조회: {session_id}")
            return {"messages": []}
    except Exception as e:
        logger.error(f"메시지 조회 오류: {e}")
        return {"messages": []}

@app.post("/api/messages")
async def save_message(request: Request):
    try:
        data = await request.json()
        session_id = data.get("session_id")
        
        # undefined/null/빈 문자열 세션 ID 처리 및 최근 세션 자동 보정
        if not session_id or session_id in ["undefined", "null", "", None]:
            # 가장 최근 세션의 session_id로 보정
            if sessions_collection is not None:
                recent_session = sessions_collection.find_one(
                    {"session_id": {"$ne": None}},
                    sort=[("created_at", -1)]
                )
                if recent_session:
                    session_id = recent_session["session_id"]
                else:
                    session_id = "default"
            else:
                session_id = "default"
        
        # 세션이 존재하지 않으면 자동 생성
        if sessions_collection is not None and not sessions_collection.find_one({"session_id": session_id}):
            new_session = {
                "session_id": session_id,
                "name": f"자동 생성 세션 ({session_id})",
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "message_count": 0,
                "user_id": data.get("user_id", "anonymous")
            }
            sessions_collection.insert_one(new_session)
            logger.info(f"자동 세션 생성: {session_id}")
        
        # HTML 내용을 원본 그대로 저장 (이스케이프하지 않음)
        content = data.get("content", "")
        
        # 시간 처리 - 프론트엔드에서 전송한 시간이 있으면 사용, 없으면 현재 시간
        timestamp = data.get("timestamp")
        if timestamp:
            try:
                # ISO 형식 문자열을 datetime 객체로 변환
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                elif isinstance(timestamp, (int, float)):
                    timestamp = datetime.fromtimestamp(timestamp)
                else:
                    timestamp = datetime.now()
            except (ValueError, TypeError, OSError):
                logger.warning(f"잘못된 시간 형식: {timestamp}, 현재 시간 사용")
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()
        
        message_data = {
            "session_id": session_id,
            "user_id": data.get("user_id", "anonymous"),
            "content": content,  # 원본 HTML 그대로 저장
            "role": data.get("role", "user"),
            "timestamp": timestamp
        }
        
        if chat_logs_collection is not None:
            try:
                result = chat_logs_collection.insert_one(message_data)
                message_data["_id"] = str(result.inserted_id)
                message_data["timestamp"] = message_data["timestamp"].isoformat()
                # 세션 업데이트
                if sessions_collection is not None:
                    sessions_collection.update_one(
                        {"session_id": session_id},
                        {"$set": {
                            "last_activity": datetime.now(),
                            "message_count": chat_logs_collection.count_documents({"session_id": session_id})
                        }},
                        upsert=True
                    )
                logger.info(f"메시지 저장 완료: {result.inserted_id}, 세션: {session_id}")
            except Exception as db_error:
                logger.error(f"MongoDB 메시지 저장 실패: {db_error}")
                message_data["_id"] = f"temp_{int(datetime.now().timestamp())}"
                message_data["timestamp"] = message_data["timestamp"].isoformat()
        else:
            message_data["_id"] = f"temp_{int(datetime.now().timestamp())}"
            message_data["timestamp"] = message_data["timestamp"].isoformat()
        return message_data
    except Exception as e:
        logger.error(f"메시지 저장 오류: {e}")
        fallback_message = {
            "_id": f"error_{int(datetime.now().timestamp())}",
            "session_id": "default",
            "user_id": "anonymous",
            "content": data.get("content", "") if 'data' in locals() else "",
            "role": data.get("role", "user") if 'data' in locals() else "user",
            "timestamp": datetime.now().isoformat()
        }
        return fallback_message

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message", "")
        session_id = data.get("session_id", "default_session")
        user_id = data.get("user_id", "anonymous")
        
        logger.info(f"채팅 요청 수신 - 사용자: {user_id}, 세션: {session_id}, 메시지: {user_message[:50]}...")
        logger.info(f"MongoDB 상태 - chat_logs_collection: {'연결됨' if chat_logs_collection is not None else 'None'}")
        
        # undefined/null/빈 문자열 세션 ID 처리 및 최근 세션 자동 보정
        if not session_id or session_id in ["undefined", "null", "", None]:
            # 가장 최근 세션의 session_id로 보정
            if sessions_collection is not None:
                recent_session = sessions_collection.find_one(
                    {"session_id": {"$ne": None}},
                    sort=[("created_at", -1)]
                )
                if recent_session:
                    session_id = recent_session["session_id"]
                    logger.info(f"세션 ID 보정: {session_id}")
                else:
                    session_id = "default"
                    logger.info(f"기본 세션 사용: {session_id}")
            else:
                session_id = "default"
                logger.info(f"기본 세션 사용 (MongoDB 연결 없음): {session_id}")
        
        # 사용자 메시지는 프론트엔드에서 저장하므로 여기서는 저장하지 않음
        logger.info(f"사용자 메시지 - 프론트엔드에서 저장 예정: {user_message[:50]}...")
        
        # EORA 응답 생성
        if OPENAI_API_KEY and OPENAI_AVAILABLE:
            try:
                # OpenAI API 1.0.0 호환성
                client = openai.OpenAI(api_key=OPENAI_API_KEY)
                response = client.chat.completions.create(
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
        
        # EORA 응답은 프론트엔드에서 저장하므로 여기서는 저장하지 않음
        message_id = f"temp_{int(datetime.now().timestamp())}"
        logger.info(f"EORA 응답 - 프론트엔드에서 저장 예정: {eora_response[:50]}...")
        
        # 아우라 데이터 저장
        if aura_collection is not None:
            try:
                aura_data = {
                    "user_id": user_id,
                    "session_id": session_id,
                    "aura_level": 5.0,
                    "aura_type": "creative",
                    "timestamp": datetime.now(),
                    "interaction_count": 1
                }
                aura_collection.insert_one(aura_data)
                logger.info(f"✅ 아우라 데이터 저장 완료 - 사용자: {user_id}")
            except Exception as e:
                logger.error(f"❌ 아우라 데이터 저장 실패: {e}")
        else:
            logger.warning("⚠️ aura_collection이 None입니다. 아우라 데이터 저장 건너뜀")
        
        # 상호작용 로그
        if system_logs_collection is not None:
            try:
                interaction_data = {
                    "user_id": user_id,
                    "session_id": session_id,
                    "interaction_type": "chat",
                    "timestamp": datetime.now(),
                    "content_length": len(user_message)
                }
                system_logs_collection.insert_one(interaction_data)
                logger.info(f"✅ 상호작용 로그 저장 완료")
            except Exception as e:
                logger.error(f"❌ 상호작용 로그 저장 실패: {e}")
        else:
            logger.warning("⚠️ system_logs_collection이 None입니다. 상호작용 로그 저장 건너뜀")
        
        logger.info(f"채팅 처리 완료 - 세션: {session_id}, 응답 길이: {len(eora_response)}")
        
        return {
            "response": eora_response,
            "message_id": message_id,
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
        if aura_collection is not None:
            result = aura_collection.insert_one(aura_data)
            return {"message": "아우라 저장 완료", "id": str(result.inserted_id)}
        else:
            return {"message": "아우라 저장 완료", "id": "temp_id"}
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
        if chat_logs_collection is not None:
            messages = list(chat_logs_collection.find({"session_id": session_id}).sort("timestamp", 1))
            for message in messages:
                convert_objectid(message)
            return {"messages": messages}
        else:
            return {"messages": []}
    except Exception as e:
        logger.error(f"대화 메시지 조회 오류: {e}")
        return {"messages": []}

@app.get("/api/conversations/{session_id}/history")
async def get_conversation_history(session_id: str):
    return {"history": []}

@app.get("/api/user/{user_id}/sessions")
async def get_user_sessions(user_id: str):
    return {"sessions": []}

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    if not is_valid_session_id(session_id):
        return JSONResponse(status_code=400, content={"error": "유효하지 않은 세션 ID입니다."})
    try:
        # 완전한 유효성 검사 - undefined, null, 빈 문자열 완전 차단
        if not session_id:
            logger.warning(f"🚫 빈 세션 ID로 삭제 요청 차단")
            return {"message": "빈 세션 ID", "session_id": session_id, "blocked": True, "deleted": False}
        
        session_id_str = str(session_id).strip()
        
        # undefined, null, 빈 문자열 완전 차단
        if (session_id_str in ["undefined", "null", ""] or 
            session_id_str.lower() in ["undefined", "null"] or
            session_id_str == "undefined" or
            session_id_str == "null"):
            logger.warning(f"🚫 유효하지 않은 세션 ID로 삭제 요청 차단: '{session_id_str}'")
            return {"message": "유효하지 않은 세션 ID", "session_id": session_id_str, "blocked": True, "deleted": False}
        
        # session_ 접두사 또는 충분한 길이 확인
        if not (session_id_str.startswith("session_") or len(session_id_str) > 10):
            logger.warning(f"🚫 잘못된 세션 ID 형식 차단: '{session_id_str}'")
            return {"message": "잘못된 세션 ID 형식", "session_id": session_id_str, "blocked": True, "deleted": False}
        
        logger.info(f"✅ 유효한 세션 삭제 요청: {session_id_str}")
        
        # 실제로 해당 세션이 존재하는지 확인
        if sessions_collection is not None:
            existing_session = sessions_collection.find_one({"session_id": session_id_str})
            if not existing_session:
                logger.warning(f"⚠️ 존재하지 않는 세션 삭제 시도: {session_id_str}")
                return {"message": "존재하지 않는 세션", "session_id": session_id_str, "deleted": False}
        
        # 메시지 삭제
        deleted_messages_count = 0
        if chat_logs_collection is not None:
            deleted_messages = chat_logs_collection.delete_many({"session_id": session_id_str})
            deleted_messages_count = deleted_messages.deleted_count
            logger.info(f"📝 세션 메시지 삭제: {session_id_str}, 삭제된 메시지 수: {deleted_messages_count}")
        
        # 세션 삭제
        deleted_session_count = 0
        if sessions_collection is not None:
            deleted_session = sessions_collection.delete_one({"session_id": session_id_str})
            deleted_session_count = deleted_session.deleted_count
            logger.info(f"🗑️ 세션 삭제: {session_id_str}, 삭제됨: {deleted_session_count > 0}")
        
        if deleted_session_count > 0 or deleted_messages_count > 0:
            logger.info(f"✅ 세션 삭제 완료: {session_id_str}")
            return {"message": "세션 삭제 완료", "session_id": session_id_str, "deleted": True}
        else:
            logger.warning(f"⚠️ 삭제할 세션이 없음: {session_id_str}")
            return {"message": "삭제할 세션이 없음", "session_id": session_id_str, "deleted": False}
            
    except Exception as e:
        logger.error(f"❌ 세션 삭제 오류: {e}")
        return {"message": "세션 삭제 실패", "error": str(e), "deleted": False}

@app.delete("/api/conversations/{session_id}")
async def delete_conversation(session_id: str):
    try:
        if chat_logs_collection is not None:
            chat_logs_collection.delete_many({"session_id": session_id})
        if sessions_collection is not None:
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
    import sys
    
    # Railway 환경 감지 및 최적화
    is_railway = os.environ.get("RAILWAY_ENVIRONMENT", "").lower() in ["production", "true", "1"]
    is_railway_port = os.environ.get("PORT", "").isdigit()
    
    # 명령행 인수에서 포트 확인
    port = 8000
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            try:
                port = int(sys.argv[i + 1])
                break
            except ValueError:
                pass
    
    # 환경변수에서 포트 확인 (Railway 우선)
    if is_railway or is_railway_port:
        port = int(os.environ.get("PORT", 8000))
    elif port == 8000:
        port = int(os.environ.get("PORT", 8000))
    
    # Railway 환경 로깅
    if is_railway or is_railway_port:
        logger.info("🚂 Railway 환경에서 실행 중")
        logger.info(f"🔧 Railway 포트: {port}")
        logger.info(f"🔧 Railway 환경변수: {list(os.environ.keys())}")
        
        # Railway 환경에서 MongoDB 연결 재시도
        if client is None:
            logger.info("🔄 Railway 환경에서 MongoDB 연결 재시도 중...")
            try:
                # Railway 환경변수에서 직접 추출
                mongo_host = os.getenv("MONGO_HOST", "")
                mongo_port = os.getenv("MONGO_PORT", "27017")
                mongo_user = os.getenv("MONGO_USER", "")
                mongo_password = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "")
                
                if mongo_host and mongo_password:
                    if mongo_user:
                        direct_url = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}"
                    else:
                        direct_url = f"mongodb://root:{mongo_password}@{mongo_host}:{mongo_port}"
                    
                    logger.info(f"🔄 Railway MongoDB 재연결 시도: {direct_url}")
                    client = MongoClient(
                        direct_url,
                        serverSelectionTimeoutMS=10000,
                        connectTimeoutMS=10000,
                        socketTimeoutMS=10000
                    )
                    client.admin.command('ping')
                    
                    db = client[DATABASE_NAME]
                    chat_logs_collection = db["chat_logs"]
                    sessions_collection = db["sessions"]
                    users_collection = db["users"]
                    aura_collection = db["aura"]
                    system_logs_collection = db["system_logs"]
                    
                    logger.info("✅ Railway MongoDB 재연결 성공")
                else:
                    logger.warning("⚠️ Railway MongoDB 환경변수가 설정되지 않음")
            except Exception as e:
                logger.warning(f"⚠️ Railway MongoDB 재연결 실패: {e}")
    
    logger.info(f"🚀 EORA AI System 서버 시작 - 포트: {port}")
    
    # Railway 환경에서 최적화된 설정
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        reload=False,  # Railway에서는 reload 비활성화
        log_level="info",
        access_log=True,
        use_colors=False if (is_railway or is_railway_port) else True,  # Railway에서는 색상 비활성화
        workers=1  # Railway에서는 단일 워커 사용
    ) 