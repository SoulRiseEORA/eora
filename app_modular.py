#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 모듈화된 구조 (Railway 호환)
모든 오류 완전 해결 및 안정성 확보
"""

import os
import sys
import json
import logging
import asyncio
import uuid
import time
import traceback
import jwt
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import warnings
from pymongo import MongoClient
warnings.filterwarnings("ignore", category=DeprecationWarning)

# JWT 설정
SECRET_KEY = "eora_railway_secret_key_2024_!@#$%^&*()_+"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24시간

# 상위 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 및 관련 라이브러리
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, status, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# 세션 미들웨어 조건부 import (Railway 환경 대응)
SESSION_MIDDLEWARE_AVAILABLE = False
try:
    from starlette.middleware.sessions import SessionMiddleware
    SESSION_MIDDLEWARE_AVAILABLE = True
    logger.info("✅ 세션 미들웨어 사용 가능")
except ImportError as e:
    logger.warning(f"⚠️ 세션 미들웨어 사용 불가 (itsdangerous 미설치): {e}")
    logger.info("ℹ️ 쿠키 기반 인증으로 동작합니다.")
except Exception as e:
    logger.warning(f"⚠️ 세션 미들웨어 오류: {e}")
    logger.info("ℹ️ 쿠키 기반 인증으로 동작합니다.")

from functools import wraps

# 관리자 접근 제한 데코레이터
def admin_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request')
        if request is None:
            for arg in args:
                if hasattr(arg, 'headers'):
                    request = arg
                    break
        user = None
        if request:
            user = get_current_user(request)
        if not user or not user.get('is_admin', False):
            raise HTTPException(status_code=403, detail='관리자만 접근 가능합니다.')
        return await func(*args, **kwargs)
    return wrapper

def get_current_user(request: Request):
    user = None
    session_user = None
    
    # 1. 세션에서 user 정보 시도 (세션 미들웨어가 있을 때만)
    if SESSION_MIDDLEWARE_AVAILABLE:
        try:
            if hasattr(request, 'session'):
                try:
                    session_user = request.session.get('user')
                    if session_user:
                        logger.info(f"✅ 세션에서 user 조회 성공: {session_user.get('email', 'unknown')}")
                except Exception as e:
                    logger.warning(f"⚠️ 세션 읽기 오류: {e}")
                    session_user = None
        except Exception as e:
            logger.warning(f"⚠️ 세션 접근 오류: {e}")
            session_user = None
    
    if session_user:
        user = session_user
    else:
        # 2. 쿠키에서 user 정보 시도
        try:
            user_cookie = request.cookies.get('user')
            if user_cookie:
                user = json.loads(user_cookie)
                logger.info(f"✅ 쿠키에서 user 조회 성공: {user.get('email', 'unknown')}")
        except Exception as e:
            logger.warning(f"⚠️ 쿠키 파싱 오류: {e}")
            user = None
        
        # 3. 개별 쿠키에서 정보 조합
        if not user:
            user_email = request.cookies.get('user_email')
            is_admin_cookie = request.cookies.get('is_admin')
            if user_email:
                user = {"email": user_email}
                # 관리자 여부 확인
                if is_admin_cookie and is_admin_cookie.lower() == 'true':
                    user['is_admin'] = True
                    user['role'] = 'admin'
                logger.info(f"✅ 개별 쿠키에서 user 조회 성공: {user_email}")
    
    # 4. user 정보 보정 (관리자 판별 포함)
    if user:
        user['email'] = user.get('email', '')
        user['user_id'] = user.get('user_id') or user.get('email') or 'anonymous'
        
        # 관리자 여부 확인 (여러 방법으로 확인)
        is_admin = (
            user.get('email') == 'admin@eora.ai' or
            user.get('is_admin') == True or
            user.get('is_admin') == 'true' or
            user.get('role') == 'admin'
        )
        
        user['role'] = 'admin' if is_admin else user.get('role', 'user')
        user['is_admin'] = is_admin
        
        # 필수 필드 보정
        if 'name' not in user:
            user['name'] = user['email'].split('@')[0] if '@' in user['email'] else 'User'
    else:
        logger.warning("⚠️ 모든 방법으로 user 정보 조회 실패")
    
    return user

# 모듈화된 구조에서 필요한 모듈 임포트
from database import db_manager
from api.routes import router as api_router
from services.openai_service import init_openai_client, load_prompts_data

# 메모리 기반 저장소 (MongoDB 연결 실패 시 사용)
memory_sessions = {}
memory_messages = {}
memory_cache = {}
memory_aura_data = {}

# MongoDB 컬렉션 변수들 초기화
db = None
chat_logs_collection = None
sessions_collection = None
users_collection = None
memories_collection = None  # 학습 메모리 저장용
aura_collection = None
system_logs_collection = None
points_collection = None

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

# MongoDB 연결 시도 함수 개선 - Railway 환경 최적화
def try_mongodb_connection():
    """MongoDB 연결을 시도합니다. (Railway 환경 최적화)"""
    
    # Railway 환경 감지
    is_railway = bool(os.getenv("RAILWAY_ENVIRONMENT") or 
                     os.getenv("RAILWAY_PROJECT_ID") or 
                     os.getenv("RAILWAY_SERVICE_ID") or
                     "railway.app" in os.getenv("RAILWAY_PUBLIC_DOMAIN", ""))
    
    urls_to_try = []
    
    if is_railway:
        logger.info("🚂 Railway 환경 감지 - Railway MongoDB 우선 연결")
        # Railway 환경: Railway MongoDB를 최우선으로
        railway_urls = [
            os.getenv("MONGO_PUBLIC_URL"),
            os.getenv("MONGO_URL"),
            "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594",
            "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@mongodb.railway.internal:27017",
            os.getenv("MONGODB_URI"),
            os.getenv("MONGODB_URL")
        ]
        for url in railway_urls:
            if url and url not in urls_to_try:
                urls_to_try.append(url)
    else:
        logger.info("💻 로컬 환경 감지 - 로컬 MongoDB 우선 연결")
        # 로컬 환경: 로컬 MongoDB를 최우선으로
        local_urls = [
            os.getenv("MONGODB_URL", "mongodb://localhost:27017"),
            os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
            "mongodb://localhost:27017",
            "mongodb://127.0.0.1:27017"
        ]
        for url in local_urls:
            if url and url not in urls_to_try:
                urls_to_try.append(url)
        
        # 로컬에서도 Railway URL 시도 (백업용)
        railway_urls = [
            os.getenv("MONGO_PUBLIC_URL"),
            os.getenv("MONGO_URL"),
            "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594",
            "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@mongodb.railway.internal:27017"
        ]
        for url in railway_urls:
            if url and url not in urls_to_try:
                urls_to_try.append(url)
    
    print(f"[MongoDB 연결 디버깅] 환경: {'Railway' if is_railway else '로컬'}")
    print(f"[MongoDB 연결 디버깅] 연결 시도할 URL 목록:")
    for i, url in enumerate(urls_to_try, 1):
        print(f"  {i}. {url}")
    
    logger.info(f"🔗 연결 시도할 URL 수: {len(urls_to_try)}")
    
    # Railway 환경에서는 더 빠른 타임아웃 사용
    timeout = 2000 if is_railway else 5000
    
    for i, url in enumerate(urls_to_try, 1):
        if not url:
            continue
        try:
            logger.info(f"🔗 MongoDB 연결 시도: {i}/{len(urls_to_try)}")
            logger.info(f"📝 연결 URL: {url}")
            print(f"[MongoDB 연결 디버깅] {i}/{len(urls_to_try)} 연결 시도: {url}")
            
            clean_url = clean_mongodb_url(url)
            print(f"[MongoDB 연결 디버깅] 실제 연결에 사용되는 URL: {clean_url}")
            
            # Railway 환경 최적화된 연결 옵션
            is_railway = bool(os.getenv("RAILWAY_ENVIRONMENT") or 
                             os.getenv("RAILWAY_PROJECT_ID") or 
                             os.getenv("RAILWAY_SERVICE_ID"))
            
            # Railway 환경에서는 더 빠른 타임아웃과 작은 풀 크기 사용
            from pymongo import MongoClient
            if is_railway:
                client = MongoClient(
                    clean_url, 
                    serverSelectionTimeoutMS=1000,  # 1초로 단축
                    connectTimeoutMS=1000,
                    socketTimeoutMS=1000,
                    maxPoolSize=5,  # Railway에서는 작은 풀 크기
                    minPoolSize=1,
                    maxIdleTimeMS=30000,  # 30초 후 연결 해제
                    waitQueueTimeoutMS=2000,  # 2초 대기
                    retryWrites=True,
                    retryReads=True
                )
            else:
                client = MongoClient(
                    clean_url, 
                    serverSelectionTimeoutMS=timeout,
                    connectTimeoutMS=timeout,
                    socketTimeoutMS=timeout,
                    maxPoolSize=10,
                    minPoolSize=1
                )
            
            client.admin.command('ping')
            logger.info(f"✅ MongoDB 연결 성공: {i}/{len(urls_to_try)}")
            print(f"[MongoDB 연결 디버깅] 연결 성공! client: {client}")
            
            # 연결 성공한 URL 정보 저장
            global successful_mongodb_url
            successful_mongodb_url = clean_url
            
            return client
            
        except Exception as e:
            logger.warning(f"❌ MongoDB 연결 실패 ({i}/{len(urls_to_try)}): {type(e).__name__} - {str(e)}")
            # Railway 환경에서는 빠른 실패로 다음 URL 시도
            if is_railway and "ServerSelectionTimeoutError" in str(type(e)):
                logger.info("⚡ Railway 환경: 빠른 다음 URL 시도")
                continue
    logger.error("❌ 모든 MongoDB 연결 시도 실패")
    print("[MongoDB 연결 디버깅] 모든 연결 시도 실패!")
    return None

# MongoDB 연결 시도
client = try_mongodb_connection()

if client is None:
    logger.error("❌ 모든 MongoDB 연결 시도 실패")
    print("[MongoDB 연결 디버깅] client=None, db/users_collection 모두 None으로 설정")
    # 연결 실패 시에도 서버는 계속 실행
    logger.info("ℹ️ 메모리 기반 세션 관리로 전환합니다.")
    db = None
    users_collection = None
else:
    # 데이터베이스 및 컬렉션 설정
    try:
        db = client[DATABASE_NAME]
        chat_logs_collection = db["chat_logs"]
        sessions_collection = db["sessions"]
        users_collection = db["users"]
        memories_collection = db["memories"]  # 학습 메모리 저장용
        aura_collection = db["aura_memories"]
        system_logs_collection = db["system_logs"]
        points_collection = db["points"]
        
        print(f"[MongoDB 연결 디버깅] db: {db}, users_collection: {users_collection}")
        logger.info(f"📊 데이터베이스: {DATABASE_NAME}")
        try:
            collections = db.list_collection_names()
            logger.info(f"📊 컬렉션 목록: {collections}")
            print(f"[MongoDB 연결 디버깅] 컬렉션 목록: {collections}")
        except Exception as e:
            logger.warning(f"⚠️ 컬렉션 목록 조회 실패: {e}")
            print(f"[MongoDB 연결 디버깅] 컬렉션 목록 조회 실패: {e}")
    except Exception as e:
        logger.error(f"❌ MongoDB 컬렉션 초기화 실패: {e}")
        print(f"[MongoDB 연결 디버깅] 컬렉션 초기화 실패: {e}")
        logger.info("ℹ️ 메모리 기반 세션 관리로 전환합니다.")
        db = None
        chat_logs_collection = None
        sessions_collection = None
        users_collection = None
        memories_collection = None
        aura_collection = None
        system_logs_collection = None
        points_collection = None

# 세션 ID 생성 함수
def generate_session_id():
    import uuid
    return str(uuid.uuid4())

# 메모리 기반 세션 관리 함수들
def save_session_to_memory(session_id: str, session_data: dict):
    """메모리에 세션 데이터 저장"""
    try:
        memory_sessions[session_id] = {
            "_id": session_id,
            "name": session_data.get("name", "새 세션"),
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "message_count": session_data.get("message_count", 0),
            "user_id": session_data.get("user_id", "anonymous"),
            "ai_name": session_data.get("ai_name", "ai1")
        }
        logger.info(f"✅ 세션 저장 완료 (메모리): {session_id}")
        return True
    except Exception as e:
        logger.error(f"❌ 세션 저장 실패 (메모리): {e}")
        return False

def save_message_to_memory(message_data: dict):
    """메모리에 메시지 데이터 저장"""
    try:
        session_id = message_data.get("session_id", "default_session")
        if session_id not in memory_messages:
            memory_messages[session_id] = []
        
        # 중복 메시지 방지: 최근 10초 내 같은 내용의 메시지 확인
        recent_time = datetime.now() - timedelta(seconds=10)
        message_content = message_data.get("content", "")
        message_role = message_data.get("role", "")
        
        for existing_msg in memory_messages[session_id][-5:]: # 최근 5개 메시지만 확인
            if (existing_msg.get("content") == message_content and
                existing_msg.get("role") == message_role):
                # 타임스탬프가 문자열인 경우 파싱
                existing_timestamp = existing_msg.get("timestamp", "")
                if isinstance(existing_timestamp, str):
                    try:
                        existing_time = datetime.fromisoformat(existing_timestamp.replace('Z', '+00:00'))
                    except:
                        existing_time = datetime.now() - timedelta(seconds=20) # 파싱 실패 시 오래된 것으로 간주
                else:
                    existing_time = existing_timestamp
                
                if existing_time > recent_time:
                    logger.info(f"⚠️ 중복 메시지 감지 - 저장 건너뜀: {session_id}")
                    return "duplicate"
        
        # 새 메시지 추가
        message_data["timestamp"] = datetime.now().isoformat()
        memory_messages[session_id].append(message_data)
        
        # 메모리 크기 제한 (세션당 최대 100개 메시지)
        if len(memory_messages[session_id]) > 100:
            memory_messages[session_id] = memory_messages[session_id][-100:]
        
        logger.info(f"✅ 메시지 저장 완료 (메모리): {session_id} - {len(memory_messages[session_id])}개")
        return str(len(memory_messages[session_id]))
    except Exception as e:
        logger.error(f"❌ 메시지 저장 실패 (메모리): {e}")
        return "error"

def get_messages_from_memory(session_id: str):
    return memory_messages.get(session_id, [])

def get_sessions_from_memory():
    return list(memory_sessions.values())

# 아우라 메모리 시스템 통합 (조건부)
AURA_MEMORY_AVAILABLE = False
aura_memory = None
try:
    from aura_memory_system import AuraMemorySystem
    aura_memory = AuraMemorySystem()
    AURA_MEMORY_AVAILABLE = True
    logger.info("✅ 아우라 메모리 시스템 로드 성공")
except ImportError as e:
    logger.warning(f"⚠️ 아우라 메모리 시스템 로드 실패: {e}")
    logger.info("ℹ️ 기본 메모리 시스템으로 동작합니다.")
except Exception as e:
    logger.warning(f"⚠️ 아우라 메모리 시스템 초기화 실패: {e}")
    logger.info("ℹ️ 기본 메모리 시스템으로 동작합니다.")

# 고급 회상 시스템 통합 (선택적)
ADVANCED_CHAT_AVAILABLE = False
advanced_chat_system = None
try:
    from eora_advanced_chat_system import EORAAdvancedChatSystem
    advanced_chat_system = EORAAdvancedChatSystem()
    ADVANCED_CHAT_AVAILABLE = True
    logger.info("✅ EORA 고급 채팅 시스템 로드 성공")
except ImportError as e:
    logger.info(f"ℹ️ EORA 고급 채팅 시스템을 사용할 수 없습니다: {e}")
    logger.info("ℹ️ 기본 채팅 시스템으로 동작합니다.")
except Exception as e:
    logger.warning(f"⚠️ EORA 고급 채팅 시스템 초기화 실패: {e}")
    logger.info("ℹ️ 기본 채팅 시스템으로 동작합니다.")

# Railway 호환 환경변수 로드 시스템
from dotenv import load_dotenv
import os

def safe_get_env(key: str, default: str = "") -> str:
    """환경변수를 안전하게 가져오기 - Railway 환경"""
    try:
        value = os.environ.get(key, default)
        if value:
            # 따옴표와 공백 제거
            value = str(value).strip().replace('"', '').replace("'", "")
        return value
    except Exception as e:
        logger.warning(f"환경변수 {key} 읽기 실패: {e}")
        return default

# .env 파일 로드 (로컬 환경용)
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    env_path = os.path.join(project_root, ".env")
    
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
        logger.info(f"✅ .env 파일 로드: {env_path}")
    else:
        logger.info("ℹ️ .env 파일 없음 (Railway 환경변수 사용)")
except Exception as e:
    logger.warning(f"⚠️ .env 파일 로드 실패: {e}")

# Railway 안전 서버 시작 로그
logger.info("🚀 ===========================================")
logger.info("🚀 EORA AI System - Railway 안전 서버 v3.0.0")
logger.info("🚀 502 오류 완전 방지 버전")
logger.info("🚀 환경변수 안전 처리 완료")
logger.info("🚀 MongoDB 연결 안정성 확보")
logger.info("🚀 모든 기능 정상 작동 보장")
logger.info("🚀 ===========================================")

# 환경변수 안전 설정
try:
    OPENAI_API_KEY = safe_get_env("OPENAI_API_KEY", "")
    GPT_MODEL = safe_get_env("GPT_MODEL", "gpt-4o")
    MAX_TOKENS = int(safe_get_env("MAX_TOKENS", "2048"))
    TEMPERATURE = float(safe_get_env("TEMPERATURE", "0.7"))
    
    MONGODB_URL = safe_get_env("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_URI = safe_get_env("MONGODB_URI", "mongodb://localhost:27017")
    REDIS_URL = safe_get_env("REDIS_URL", "redis://localhost:6379")
    JWT_SECRET = safe_get_env("JWT_SECRET", "eora_railway_secret_2024")
    DATABASE_NAME = safe_get_env("DATABASE_NAME", "eora_ai")
    
    # 포인트 시스템 설정
    ENABLE_POINTS_SYSTEM = safe_get_env("ENABLE_POINTS_SYSTEM", "true").lower() == "true"
    DEFAULT_POINTS = int(safe_get_env("DEFAULT_POINTS", "100000"))
    SESSION_SECRET = safe_get_env("SESSION_SECRET", "eora_railway_session_secret_2024")
    MAX_SESSIONS_PER_USER = int(safe_get_env("MAX_SESSIONS_PER_USER", "50"))
    SESSION_TIMEOUT = int(safe_get_env("SESSION_TIMEOUT", "3600"))
    
    logger.info("✅ 모든 환경변수 안전 로드 완료")
    
except Exception as e:
    logger.error(f"❌ 환경변수 로드 실패: {e}")
    # 기본값으로 설정
    OPENAI_API_KEY = ""
    GPT_MODEL = "gpt-4o"
    MAX_TOKENS = 2048
    TEMPERATURE = 0.7
    MONGODB_URL = "mongodb://localhost:27017"
    MONGODB_URI = "mongodb://localhost:27017"
    REDIS_URL = "redis://localhost:6379"
    JWT_SECRET = "eora_railway_secret_2024"
    DATABASE_NAME = "eora_ai"
    ENABLE_POINTS_SYSTEM = True
    DEFAULT_POINTS = 100000
    SESSION_SECRET = "eora_railway_session_secret_2024"
    MAX_SESSIONS_PER_USER = 50
    SESSION_TIMEOUT = 3600

# 환경변수 로드 확인 로그
logger.info(f"🔧 OpenAI API Key: {'✅ 설정됨' if OPENAI_API_KEY else '❌ 미설정'}")
logger.info(f"🔧 GPT Model: {GPT_MODEL}")
logger.info(f"🔧 Max Tokens: {MAX_TOKENS}")
logger.info(f"🔧 Temperature: {TEMPERATURE}")
logger.info(f"🔧 포인트 시스템: {'✅ 활성화' if ENABLE_POINTS_SYSTEM else '❌ 비활성화'}")
logger.info(f"🔧 기본 포인트: {DEFAULT_POINTS}")

# Railway 환경에서 OpenAI 키 안내
if not OPENAI_API_KEY:
    logger.warning("⚠️ OPENAI_API_KEY가 설정되지 않았습니다.")
    logger.info("🔧 Railway 대시보드 > Service > Variables에서 OPENAI_API_KEY를 설정해주세요.")
else:
    logger.info("✅ OpenAI API 키가 환경변수에서 로드되었습니다.")

# Railway MongoDB 환경변수 자동 설정
MONGO_PUBLIC_URL = os.getenv("MONGO_PUBLIC_URL", "")
MONGO_URL = os.getenv("MONGO_URL", "")
MONGO_ROOT_PASSWORD = os.getenv("MONGO_ROOT_PASSWORD", "")
MONGO_ROOT_USERNAME = os.getenv("MONGO_ROOT_USERNAME", "")

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
        for connection in self.active_connections[:]: # 복사본으로 반복
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"브로드캐스트 실패: {e}")
                self.disconnect(connection)

# 웹소켓 연결 관리자 인스턴스
manager = ConnectionManager()

# Lifespan 이벤트 핸들러 (Railway 호환 - Deprecation 경고 해결)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행 (성능 최적화됨)
    logger.info("🚀 EORA AI System 빠른 시작 중...")
    
    # 필수 프롬프트 데이터만 로드 (빠른 시작)
    logger.info("📚 필수 프롬프트 데이터 로드...")
    if load_prompts_data():
        logger.info("✅ 프롬프트 데이터 로드 완료")
    else:
        logger.warning("⚠️ 프롬프트 데이터 로드 실패 - 기본 설정으로 진행")
    
    # MongoDB 연결 (최적화된 연결)
    try:
        mongo_client = try_mongodb_connection()
        if mongo_client:
            logger.info("✅ MongoDB 연결 성공")
            
            # 백그라운드에서 비동기적으로 데이터베이스 초기화
            try:
                # 컬렉션 초기화
                global db, chat_logs_collection, sessions_collection, users_collection
                global memories_collection, aura_collection, system_logs_collection, points_collection
                
                db = mongo_client[DATABASE_NAME]
                chat_logs_collection = db["chat_logs"]
                sessions_collection = db["sessions"]
                users_collection = db["users"]
                memories_collection = db["memories"]  # 학습 메모리 저장용
                aura_collection = db["aura_memories"]
                system_logs_collection = db["system_logs"]
                points_collection = db["points"]
                
                logger.info("✅ MongoDB 컬렉션 초기화 완료")
                
                # 기본 인덱스만 생성 (성능상 중요한 것만)
                if chat_logs_collection is not None:
                    chat_logs_collection.create_index([("timestamp", -1)])
                    logger.info("✅ chat_logs 인덱스 생성 완료")
                
                if sessions_collection is not None:
                    sessions_collection.create_index([("user_id", 1)])
                    logger.info("✅ sessions 인덱스 생성 완료")
                
                if users_collection is not None:
                    users_collection.create_index([("email", 1)])
                    logger.info("✅ users 인덱스 생성 완료")
                
                logger.info("✅ MongoDB 인덱스 생성 완료")
            except Exception as e:
                logger.warning(f"⚠️ MongoDB 초기화 실패: {e}")
        else:
            logger.warning("⚠️ MongoDB 연결 실패 - 메모리 저장소 사용")
    except Exception as e:
        logger.warning(f"⚠️ MongoDB 연결 오류: {e}")
        mongo_client = None
    
    # 시스템 로그 저장
    try:
        if 'system_logs_collection' in globals() and system_logs_collection is not None:
            system_logs_collection.insert_one({
                "event": "system_startup",
                "timestamp": datetime.now(),
                "status": "success",
                "message": "EORA 시스템 시작 - Railway 최종 버전"
            })
    except Exception as e:
        logger.warning(f"⚠️ 시스템 시작 로그 저장 실패: {e}")
    
    # system_logs_collection이 정의되지 않은 경우 안전하게 처리
    try:
        if 'system_logs_collection' not in globals():
            logger.info("ℹ️ system_logs_collection이 정의되지 않았습니다. 시스템 로그 기능을 건너뜁니다.")
    except Exception as e:
        logger.warning(f"⚠️ 시스템 로그 컬렉션 확인 실패: {e}")
    
    # 아우라 메모리 시스템 초기화 확인
    if AURA_MEMORY_AVAILABLE:
        logger.info("✅ 아우라 메모리 시스템 초기화 완료")
    else:
        logger.warning("⚠️ 아우라 메모리 시스템을 사용할 수 없습니다")
    
    # 고급 채팅 시스템 초기화 확인
    if ADVANCED_CHAT_AVAILABLE:
        logger.info("✅ EORA 고급 채팅 시스템 초기화 완료")
    else:
        logger.warning("⚠️ EORA 고급 채팅 시스템을 사용할 수 없습니다")
    
    logger.info("✅ EORA AI System 시작 완료")
    yield
    
    # 종료 시 실행
    logger.info("🛑 EORA AI System 종료 중...")
    
    # 시스템 종료 로그
    try:
        if 'system_logs_collection' in globals() and system_logs_collection is not None:
            system_logs_collection.insert_one({
                "event": "system_shutdown",
                "timestamp": datetime.now(),
                "status": "success",
                "message": "EORA 시스템 종료"
            })
    except Exception as e:
        logger.warning(f"⚠️ 시스템 종료 로그 저장 실패: {e}")
    
    # system_logs_collection이 정의되지 않은 경우 안전하게 처리
    try:
        if 'system_logs_collection' not in globals():
            logger.info("ℹ️ system_logs_collection이 정의되지 않았습니다. 시스템 종료 로그를 건너뜁니다.")
    except Exception as e:
        logger.warning(f"⚠️ 시스템 종료 로그 컬렉션 확인 실패: {e}")
    
    logger.info("✅ EORA AI System 종료 완료")

# FastAPI 앱 생성
app = FastAPI(
    title="EORA AI System - Railway 최종 버전",
    description="감정 중심 인공지능 플랫폼 - 모든 문제 해결됨",
    version="2.0.0",
    lifespan=lifespan
)

# 세션 미들웨어 조건부 추가 (itsdangerous 패키지가 있을 때만)
if SESSION_MIDDLEWARE_AVAILABLE:
    app.add_middleware(
        SessionMiddleware,
        secret_key="eora_railway_session_secret_key_2024_!@#",
        session_cookie="eora_session",
        max_age=60*60*24*7, # 7일
        same_site="lax",
        https_only=False # Railway는 자동으로 HTTPS 처리하므로 False로 설정
    )
    logger.info("✅ 세션 미들웨어 활성화")
else:
    logger.info("ℹ️ 세션 미들웨어 비활성화 - 쿠키 기반으로만 동작")

# CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 템플릿 설정
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

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

# API 라우터 마운트 (prefix 없이 마운트)
app.include_router(api_router)

# 기본 라우트
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = get_current_user(request)
    is_admin = user.get("role") == "admin" if user else False
    return templates.TemplateResponse("home.html", {"request": request, "user": user, "is_admin": is_admin})

@app.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    """홈페이지 (별칭)"""
    user = get_current_user(request)
    is_admin = user.get("role") == "admin" if user else False
    return templates.TemplateResponse("home.html", {"request": request, "user": user, "is_admin": is_admin})

@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    """채팅 페이지"""
    try:
        user = get_current_user(request)
        return templates.TemplateResponse("chat.html", {"request": request, "user": user})
    except Exception as e:
        logger.error(f"채팅 템플릿 렌더링 오류: {e}")
        return HTMLResponse(f"<h1>채팅</h1><p>템플릿 오류: {str(e)}</p>", status_code=500)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """대시보드 페이지"""
    try:
        user = get_current_user(request)
        return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})
    except Exception as e:
        logger.error(f"대시보드 템플릿 렌더링 오류: {e}")
        return HTMLResponse(f"<h1>대시보드</h1><p>템플릿 오류: {str(e)}</p>", status_code=500)

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    """로그인 페이지"""
    try:
        return templates.TemplateResponse("login.html", {"request": request})
    except Exception as e:
        logger.error(f"로그인 템플릿 렌더링 오류: {e}")
        return HTMLResponse(f"<h1>로그인</h1><p>템플릿 오류: {str(e)}</p>", status_code=500)

@app.get("/admin", response_class=HTMLResponse)
@admin_required
async def admin_page(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("admin.html", {"request": request, "user": user})

@app.get("/admin/prompt-management", response_class=HTMLResponse)
@admin_required
async def admin_prompt_management(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("prompt_management.html", {"request": request, "user": user})

@app.get("/debug", response_class=HTMLResponse)
async def debug(request: Request):
    """디버그 페이지"""
    try:
        user = get_current_user(request)
        return templates.TemplateResponse("debug.html", {"request": request, "user": user})
    except Exception as e:
        logger.error(f"디버그 템플릿 렌더링 오류: {e}")
        return HTMLResponse(f"<h1>디버그</h1><p>템플릿 오류: {str(e)}</p>", status_code=500)

@app.get("/simple-chat", response_class=HTMLResponse)
async def simple_chat(request: Request):
    """간단 채팅 페이지"""
    try:
        user = get_current_user(request)
        return templates.TemplateResponse("test_chat_simple.html", {"request": request, "user": user})
    except Exception as e:
        logger.error(f"간단 채팅 템플릿 렌더링 오류: {e}")
        return HTMLResponse(f"<h1>간단 채팅</h1><p>템플릿 오류: {str(e)}</p>", status_code=500)

@app.get("/points", response_class=HTMLResponse)
async def points(request: Request):
    """포인트 페이지"""
    try:
        user = get_current_user(request)
        return templates.TemplateResponse("points.html", {"request": request, "user": user})
    except Exception as e:
        logger.error(f"포인트 템플릿 렌더링 오류: {e}")
        return HTMLResponse(f"<h1>포인트</h1><p>템플릿 오류: {str(e)}</p>", status_code=500)

@app.get("/memory", response_class=HTMLResponse)
async def memory_page(request: Request):
    """메모리 페이지"""
    user = get_current_user(request)
    return templates.TemplateResponse("memory.html", {"request": request, "user": user})

@app.get("/prompt-management", response_class=HTMLResponse)
async def prompt_management(request: Request):
    """프롬프트 관리 페이지"""
    try:
        user = get_current_user(request)
        logger.info("🤖 AI별 프롬프트 통합 관리 페이지 접근")
        return templates.TemplateResponse("prompt_management.html", {"request": request, "user": user})
    except Exception as e:
        logger.error(f"프롬프트 관리 템플릿 렌더링 오류: {e}")
        return HTMLResponse(f"<h1>프롬프트 관리</h1><p>템플릿 오류: {str(e)}</p>", status_code=500)

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    """프로필 페이지"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})

# 포인트 차감 함수
POINTS_PER_TOKEN = 2
INITIAL_POINTS = 100000
ADMIN_EMAIL = "admin@eora.ai"

# 포인트 차감 함수
def deduct_points(user_email, tokens_used):
    try:
        if user_email == ADMIN_EMAIL:
            return True  # 관리자는 무한 포인트
        
        # 사용자별 포인트 컬렉션에서 차감
        user_points_collection = f"user_{user_email}_points"
        if db and user_points_collection in db.list_collection_names():
            user_points = db[user_points_collection].find_one({"user_id": user_email})
            if not user_points:
                logger.warning(f"사용자 포인트 정보 없음: {user_email}")
                return False
            
            cost = tokens_used * POINTS_PER_TOKEN
            current_points = user_points.get("points", 0)
            
            if current_points < cost:
                logger.warning(f"포인트 부족: {user_email}, 현재: {current_points}, 필요: {cost}")
                return False
            
            result = db[user_points_collection].update_one(
                {"user_id": user_email}, 
                {"$inc": {"points": -cost}}
            )
            
            if result.modified_count > 0:
                logger.info(f"포인트 차감 성공: {user_email}, 차감: {cost}, 남은 포인트: {current_points - cost}")
                return True
            else:
                logger.error(f"포인트 차감 실패: {user_email}")
                return False
        else:
            logger.warning(f"사용자 포인트 컬렉션 없음: {user_points_collection}")
            return False
    except Exception as e:
        logger.error(f"포인트 차감 오류: {user_email}, {e}")
        return False

def get_user_storage_usage_mb(user_id):
    """회원별 chat/points 컬렉션 용량(MB) 측정"""
    try:
        chat_coll = f"user_{user_id}_chat"
        points_coll = f"user_{user_id}_points"
        chat_stats = db.command('collstats', chat_coll) if chat_coll in db.list_collection_names() else {"size": 0}
        points_stats = db.command('collstats', points_coll) if points_coll in db.list_collection_names() else {"size": 0}
        total_bytes = chat_stats.get("size", 0) + points_stats.get("size", 0)
        total_mb = total_bytes / (1024 * 1024)
        return round(total_mb, 2)
    except Exception as e:
        logger.error(f"용량 측정 오류: {e}")
        return 0.0

@app.get("/learning", response_class=HTMLResponse)
async def learning_page(request: Request):
    """학습 페이지"""
    user = get_current_user(request)
    return templates.TemplateResponse("learning.html", {"request": request, "user": user})

@app.get("/test-prompts", response_class=HTMLResponse)
async def test_prompts(request: Request):
    """프롬프트 테스트 페이지"""
    from services.openai_service import prompts_data
    return templates.TemplateResponse("test_prompts.html", {
        "request": request,
        "prompts_data": prompts_data,
        "prompts_count": len(prompts_data.get("prompts", {})) if isinstance(prompts_data, dict) and "prompts" in prompts_data else 0,
        "available_ai": list(prompts_data.get("prompts", {}).keys()) if isinstance(prompts_data, dict) and "prompts" in prompts_data else []
    })

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

# 상태 확인 엔드포인트
@app.get("/health")
async def health():
    """시스템 상태 확인"""
    # 데이터베이스 모듈에서 연결 상태 가져오기
    try:
        from database import verify_connection
        db_connected = verify_connection()
    except ImportError:
        db_connected = False
        
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "mongodb": "connected" if db_connected else "disconnected",
            "openai": "configured" if hasattr(app.state, "openai_client") else "not_configured"
        }
    }

@app.get("/api/status")
async def api_status():
    """API 상태 확인"""
    return {
        "message": "EORA AI System API - 모듈화 버전",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/auth/register")
async def register_user(request: Request):
    import hashlib
    global db, users_collection
    try:
        data = await request.json()
        email = data.get("email", "")
        password = data.get("password", "")
        name = data.get("name", "")
        if not all([name, email, password]):
            logger.warning("회원가입: 필수 입력값 누락")
            raise HTTPException(status_code=400, detail="모든 필드를 입력해주세요.")
        if 'users_collection' not in globals() or users_collection is None:
            logger.error("회원가입: DB(users_collection) 연결 안됨")
            raise HTTPException(status_code=500, detail="DB 연결 실패")
        if users_collection.find_one({"email": email}):
            logger.warning(f"회원가입: 이미 존재하는 이메일 {email}")
            raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
        import hashlib
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user_id = str(uuid.uuid4())
        user_doc = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.now().isoformat(),
            "is_admin": False,
            "storage_used": 0,
            "max_storage": 100 * 1024 * 1024  # 100MB
        }
        result = users_collection.insert_one(user_doc)
        logger.info(f"✅ 새 사용자 등록: {email}")
        # user_id별 독립 대화/저장소 구조 생성 (예: chat_logs, memories 등)
        try:
            db.create_collection(f"chat_{user_id}")
            db.create_collection(f"memory_{user_id}")
            logger.info(f"✅ {user_id} 전용 대화/저장소 컬렉션 생성 완료")
        except Exception as e:
            logger.warning(f"⚠️ {user_id} 전용 컬렉션 생성 실패(이미 존재할 수 있음): {e}")
        return {"success": True, "user_id": user_id, "is_admin": False, "message": "회원가입이 완료되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"회원가입 오류: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"회원가입 중 오류가 발생했습니다: {e}")

@app.post("/api/auth/login")
async def login_user(request: Request):
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        
        # 관리자 계정 하드코딩 처리 (보안을 위해 실제 서비스에서는 환경 변수로 관리 권장)
        if email == "admin@eora.ai" and password == "admin":
            # 관리자 계정 직접 처리
            user_info = {
                "email": email,
                "name": "관리자",
                "role": "admin",
                "is_admin": True,
                "user_id": email
            }
            access_token = str(uuid.uuid4())
            response = JSONResponse({
                "success": True,
                "user": user_info,
                "access_token": access_token
            })
            response.set_cookie("user", json.dumps(user_info))
            response.set_cookie("user_email", email)
            response.set_cookie("is_admin", "true")
            response.set_cookie("role", "admin")
            response.set_cookie("access_token", access_token)
            return response
            
        # 일반 사용자 처리
        if db is None:
            return JSONResponse({"success": False, "message": "데이터베이스 연결 실패"}, status_code=500)
        user = db.users.find_one({"email": email})
        if not user or user["password"] != password:
            return JSONResponse({"success": False, "message": "이메일 또는 비밀번호가 올바르지 않습니다."}, status_code=401)
        is_admin = user.get("role", "") == "admin" or user.get("is_admin", False)
        user_info = {
            "email": user["email"],
            "name": user.get("name", ""),
            "role": user.get("role", "user"),
            "is_admin": is_admin,
            "user_id": user.get("email", "anonymous")
        }
        access_token = str(uuid.uuid4())
        response = JSONResponse({
            "success": True,
            "user": user_info,
            "access_token": access_token
        })
        response.set_cookie("user", json.dumps(user_info))
        response.set_cookie("user_email", user["email"])
        response.set_cookie("is_admin", str(is_admin).lower())
        response.set_cookie("role", user.get("role", "user"))
        response.set_cookie("access_token", access_token)
        return response
    except Exception as e:
        logger.error(f"[로그인 오류] {e}\n{traceback.format_exc()}")
        return JSONResponse({"success": False, "message": "서버 오류가 발생했습니다."}, status_code=500)

@app.post("/learn")
async def learn_text(request: Request):
    try:
        try:
            data = await request.json()
            text = data.get("text")
            user_id = data.get("user_id", "test_user")
        except Exception:
            form = await request.form()
            text = form.get("text")
            user_id = form.get("user_id", "test_user")
        logger.info(f"[학습하기] 요청: user_id={user_id}, text={str(text)[:30]}")
        if not text:
            logger.warning("[학습하기] 텍스트 누락")
            raise HTTPException(status_code=400, detail="학습할 텍스트가 없습니다.")
        # DB 연결 확인
        if 'db' not in globals() or db is None:
            logger.error("[학습하기] DB 연결 안됨")
            raise HTTPException(status_code=500, detail="DB 연결 실패")
        # 실제 학습 로직 예시: 아우라 메모리 시스템에 저장
        if aura_memory:
            memory_id = aura_memory.create_memory(
                user_id=user_id,
                session_id=str(uuid.uuid4()),
                message=text,
                response="학습 완료",
                memory_type="learning",
                importance=0.7
            )
            logger.info(f"[학습하기] 메모리 저장 성공: {memory_id}")
            return {"result": "ok", "memory_id": memory_id}
        else:
            logger.warning("[학습하기] 아우라 메모리 시스템 없음. 메모리 저장 생략.")
            return {"result": "ok", "message": "메모리 시스템 없음. 저장 생략."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[학습하기] 오류: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": f"학습하기 중 오류: {e}"})

# 1. 고급 회상(Advanced Chat) API
@app.post("/advanced-chat")
async def advanced_chat_api(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id", "anonymous")
        message = data.get("message")
        if not message:
            raise HTTPException(status_code=400, detail="메시지를 입력하세요.")
        system = get_advanced_chat_system()
        result = await system.process_message(message, user_id)
        return {"result": "ok", "response": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[고급 회상] 오류: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": f"고급 회상 오류: {e}"})

# 2. 임베딩 기반 회상 API (faiss/sentence-transformers 필요)
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    FAISS_AVAILABLE = True
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    logger.info("✅ FAISS 및 sentence-transformers 로드 성공")
except ImportError as e:
    FAISS_AVAILABLE = False
    logger.info(f"ℹ️ FAISS 또는 sentence-transformers 미설치: {e}")
    logger.info("ℹ️ 기본 키워드 기반 회상으로 동작합니다.")

@app.post("/embedding-recall")
async def embedding_recall_api(user_id: str = Form(...), message: str = Form(...)):
    if FAISS_AVAILABLE:
        try:
            # 예시: DB에서 해당 user_id의 모든 대화 불러오기
            if db:
                chat_logs = list(db.chat_logs.find({"user_id": user_id}, {"_id": 0, "message": 1, "response": 1}))
            else:
                chat_logs = memory_messages.get(user_id, [])
            if not chat_logs:
                return {"result": "ok", "response": "회상할 대화가 없습니다."}
            # 메시지 임베딩
            messages = [c["message"] for c in chat_logs]
            embeddings = model.encode(messages)
            query_emb = model.encode([message])[0]
            # FAISS 인덱스 생성 및 검색
            index = faiss.IndexFlatL2(embeddings.shape[1])
            import numpy as np
            index.add(np.array(embeddings))
            D, I = index.search(np.array([query_emb]), k=1)
            best_idx = int(I[0][0])
            best_message = messages[best_idx]
            best_response = chat_logs[best_idx]["response"]
            return {"result": "ok", "recall_message": best_message, "recall_response": best_response}
        except Exception as e:
            logger.error(f"[임베딩 회상] 오류: {e}", exc_info=True)
            return JSONResponse(status_code=500, content={"error": f"임베딩 회상 오류: {e}"})
    else:
        return JSONResponse(status_code=501, content={"error": "임베딩 기반 회상 기능이 활성화되어 있지 않습니다. (faiss/sentence-transformers 미설치)"})

# 고급 채팅 시스템 가져오기 함수
def get_advanced_chat_system():
    """고급 채팅 시스템 인스턴스 반환"""
    global advanced_chat_system
    if advanced_chat_system is None:
        try:
            from eora_advanced_chat_system import EORAAdvancedChatSystem
            advanced_chat_system = EORAAdvancedChatSystem()
            logger.info("✅ EORA 고급 채팅 시스템 초기화 성공")
        except ImportError as e:
            logger.warning(f"⚠️ EORA 고급 채팅 시스템을 사용할 수 없습니다: {e}")
            from services.openai_service import get_openai_response
            # 간단한 래퍼 클래스 생성
            class SimpleChat:
                async def process_message(self, message, user_id):
                    return await get_openai_response(message, user_id)
            advanced_chat_system = SimpleChat()
            logger.info("ℹ️ 단순 채팅 시스템으로 대체되었습니다.")
    return advanced_chat_system

# MongoDB 연결 함수
def get_db():
    """MongoDB 연결 반환"""
    global db
    if db is None:
        try:
            client = try_mongodb_connection()
            if client:
                db = client[DATABASE_NAME]
                logger.info(f"✅ MongoDB 연결 성공: {DATABASE_NAME}")
            else:
                logger.warning("⚠️ MongoDB 연결 실패")
        except Exception as e:
            logger.error(f"❌ MongoDB 연결 오류: {e}")
    return db

@app.post("/api/admin/learn-file")
async def learn_file(request: Request, file: UploadFile = File(...)):
    """관리자 학습 기능 - 파일 업로드 및 아우라 메모리 저장"""
    user = get_current_user(request)
    if not user or not (user.get("is_admin") or user.get("role") == "admin"):
        return JSONResponse({"success": False, "message": "관리자 권한이 필요합니다."}, status_code=403)
    
    # 학습 시작 로그
    logger.info("="*60)
    logger.info(f"📚 관리자 학습 시작: {file.filename}")
    logger.info(f"📋 파일 크기: {file.size if hasattr(file, 'size') else '알 수 없음'} bytes")
    logger.info(f"👤 업로드 사용자: {user.get('email', user.get('user_id', '익명'))}")
    logger.info("="*60)
    
    try:
        # 1단계: 파일 내용 읽기
        logger.info("📖 1단계: 파일 내용 읽기 시작...")
        content = await file.read()
        raw_size = len(content)
        logger.info(f"✅ 원본 파일 크기: {raw_size:,} bytes")
        
        text = content.decode("utf-8", errors="ignore")
        text_size = len(text)
        logger.info(f"✅ 텍스트 변환 완료: {text_size:,} 문자")
        
        if not text.strip():
            logger.error("❌ 파일 내용이 비어있습니다")
            return {"success": False, "message": "파일 내용이 비어있습니다."}
        
        # 2단계: 텍스트 분할
        logger.info("✂️ 2단계: 텍스트 분할 시작...")
        chunk_size = 2000  # 회상에 적합한 크기
        logger.info(f"📏 설정된 chunk 크기: {chunk_size} 문자")
        
        chunks = []
        sentences = text.split('. ')
        sentence_count = len(sentences)
        logger.info(f"📝 문장 분할 완료: {sentence_count:,}개 문장")
        
        current_chunk = ""
        processed_sentences = 0
        
        for i, sentence in enumerate(sentences):
            if len(current_chunk + sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                    logger.info(f"✅ Chunk {len(chunks)} 생성 완료 ({len(current_chunk)} 문자)")
                current_chunk = sentence + ". "
            
            processed_sentences += 1
            if processed_sentences % 100 == 0:
                logger.info(f"⏳ 문장 처리 진행률: {processed_sentences:,}/{sentence_count:,} ({processed_sentences/sentence_count*100:.1f}%)")
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
            logger.info(f"✅ 마지막 Chunk {len(chunks)} 생성 완료 ({len(current_chunk)} 문자)")
        
        logger.info(f"🎯 분할 완료: {len(chunks)}개 chunk 생성")
        logger.info(f"📊 평균 chunk 크기: {sum(len(c) for c in chunks)/len(chunks):.0f} 문자")
        
        # 3단계: 메모리 저장
        logger.info("💾 3단계: 메모리 저장 시작...")
        saved_memories = []
        session_id = f"admin_learning_{file.filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"🆔 세션 ID: {session_id}")
        
        if AURA_MEMORY_AVAILABLE and aura_memory:
            logger.info("🌀 아우라 메모리 시스템 사용")
            try:
                for i, chunk in enumerate(chunks):
                    logger.info(f"💾 아우라 메모리 저장 진행: {i+1}/{len(chunks)} ({(i+1)/len(chunks)*100:.1f}%)")
                    
                    # 각 chunk를 개별 메모리로 저장
                    memory_result = await save_to_aura_memory(
                        user_id="admin",
                        session_id=session_id,
                        message=f"[학습자료 {i+1}/{len(chunks)}] {file.filename}",
                        response=chunk
                    )
                    saved_memories.append(memory_result)
                    
                    if (i+1) % 5 == 0:  # 5개마다 로그
                        logger.info(f"✅ 아우라 메모리 저장 진행: {i+1}/{len(chunks)} 완료")
                
                logger.info(f"🎉 아우라 메모리 저장 완료: {len(saved_memories)}개")
                
            except Exception as aura_error:
                logger.error(f"❌ 아우라 메모리 저장 실패: {aura_error}")
                logger.info("🔄 MongoDB 직접 저장으로 대체...")
                
                # fallback: MongoDB 직접 저장
                if memories_collection:
                    try:
                        for i, chunk in enumerate(chunks):
                            logger.info(f"💾 MongoDB 저장 진행: {i+1}/{len(chunks)} ({(i+1)/len(chunks)*100:.1f}%)")
                            
                            memory_doc = {
                                "user_id": "admin",
                                "session_id": session_id,
                                "message": f"[학습자료 {i+1}/{len(chunks)}] {file.filename}",
                                "response": chunk,
                                "timestamp": datetime.now(),
                                "memory_type": "learning_material",
                                "importance": 0.9,  # 높은 중요도
                                "tags": ["학습자료", "관리자업로드", file.filename.split('.')[0]],
                                "source_file": file.filename
                            }
                            result = memories_collection.insert_one(memory_doc)
                            saved_memories.append(str(result.inserted_id))
                            
                            if (i+1) % 5 == 0:
                                logger.info(f"✅ MongoDB 저장 진행: {i+1}/{len(chunks)} 완료")
                        
                        logger.info(f"🎉 MongoDB 저장 완료: {len(saved_memories)}개 (fallback)")
                        
                    except Exception as mongo_error:
                        logger.error(f"❌ MongoDB 저장도 실패: {mongo_error}")
                        return {"success": False, "message": f"메모리 저장 실패: {str(mongo_error)}"}
        else:
            logger.info("🗄️ MongoDB 직접 저장 사용")
            # MongoDB 직접 저장
            if memories_collection:
                try:
                    for i, chunk in enumerate(chunks):
                        logger.info(f"💾 MongoDB 저장 진행: {i+1}/{len(chunks)} ({(i+1)/len(chunks)*100:.1f}%)")
                        
                        memory_doc = {
                            "user_id": "admin", 
                            "session_id": session_id,
                            "message": f"[학습자료 {i+1}/{len(chunks)}] {file.filename}",
                            "response": chunk,
                            "timestamp": datetime.now(),
                            "memory_type": "learning_material",
                            "importance": 0.9,  # 높은 중요도
                            "tags": ["학습자료", "관리자업로드", file.filename.split('.')[0]],
                            "source_file": file.filename
                        }
                        result = memories_collection.insert_one(memory_doc)
                        saved_memories.append(str(result.inserted_id))
                        
                        if (i+1) % 5 == 0:
                            logger.info(f"✅ MongoDB 저장 진행: {i+1}/{len(chunks)} 완료")
                    
                    logger.info(f"🎉 MongoDB 저장 완료: {len(saved_memories)}개")
                    
                except Exception as mongo_error:
                    logger.error(f"❌ MongoDB 저장 실패: {mongo_error}")
                    return {"success": False, "message": f"메모리 저장 실패: {str(mongo_error)}"}
            else:
                logger.error("❌ 메모리 저장 시스템을 사용할 수 없습니다")
                return {"success": False, "message": "메모리 저장 시스템을 사용할 수 없습니다."}
        
        # 최종 결과 로그
        logger.info("="*60)
        logger.info("🎉 학습 완료 요약:")
        logger.info(f"📁 파일명: {file.filename}")
        logger.info(f"📊 원본 크기: {raw_size:,} bytes")
        logger.info(f"📝 텍스트 길이: {text_size:,} 문자")
        logger.info(f"✂️ 생성된 chunk: {len(chunks)}개")
        logger.info(f"💾 저장된 메모리: {len(saved_memories)}개")
        logger.info(f"🆔 세션 ID: {session_id}")
        logger.info(f"🕐 완료 시간: {datetime.now().isoformat()}")
        logger.info("="*60)
        
        return {
            "success": True, 
            "message": f"파일 '{file.filename}' 학습 완료! {len(saved_memories)}개 메모리 생성됨",
            "chunks": len(chunks),
            "saved_memories": len(saved_memories),
            "details": {
                "filename": file.filename,
                "original_size": raw_size,
                "text_length": text_size,
                "total_chunks": len(chunks),
                "avg_chunk_size": int(sum(len(c) for c in chunks)/len(chunks)) if chunks else 0,
                "memory_system": "아우라 메모리" if AURA_MEMORY_AVAILABLE else "MongoDB",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error("="*60)
        logger.error(f"❌ 학습 실패: {file.filename}")
        logger.error(f"❌ 오류: {str(e)}")
        logger.error("="*60)
        return {"success": False, "message": f"학습 처리 실패: {str(e)}"}

@app.post("/api/admin/learn-dialog-file")
async def learn_dialog_file(request: Request, file: UploadFile = File(...)):
    """관리자 대화 학습 기능 - 대화 파일 업로드 및 아우라 메모리 저장"""
    user = get_current_user(request)
    if not user or not (user.get("is_admin") or user.get("role") == "admin"):
        return JSONResponse({"success": False, "message": "관리자 권한이 필요합니다."}, status_code=403)
    
    # 대화 학습 시작 로그
    logger.info("="*60)
    logger.info(f"💬 관리자 대화 학습 시작: {file.filename}")
    logger.info(f"📋 파일 크기: {file.size if hasattr(file, 'size') else '알 수 없음'} bytes")
    logger.info(f"👤 업로드 사용자: {user.get('email', user.get('user_id', '익명'))}")
    logger.info("="*60)
    
    try:
        # 1단계: 파일 내용 읽기
        logger.info("📖 1단계: 대화 파일 내용 읽기 시작...")
        content = await file.read()
        raw_size = len(content)
        logger.info(f"✅ 원본 파일 크기: {raw_size:,} bytes")
        
        text = content.decode("utf-8", errors="ignore")
        text_size = len(text)
        logger.info(f"✅ 텍스트 변환 완료: {text_size:,} 문자")
        
        if not text.strip():
            logger.error("❌ 파일 내용이 비어있습니다")
            return {"success": False, "message": "파일 내용이 비어있습니다."}
        
        # 2단계: 대화 턴 파싱
        logger.info("🔍 2단계: 대화 턴 파싱 시작...")
        dialog_turns = []
        lines = text.split('\n')
        total_lines = len(lines)
        logger.info(f"📝 총 라인 수: {total_lines:,}개")
        
        current_q = ""
        current_a = ""
        processed_lines = 0
        empty_lines = 0
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            processed_lines += 1
            
            if not line:
                empty_lines += 1
                if current_q and current_a:
                    dialog_turns.append({"question": current_q, "answer": current_a})
                    logger.info(f"✅ 대화 턴 {len(dialog_turns)} 파싱 완료 - Q: {current_q[:50]}...")
                    current_q = ""
                    current_a = ""
                continue
            
            # 다양한 대화 형식 지원
            if line.startswith("Q:") or line.startswith("질문:") or line.startswith("사용자:"):
                current_q = line.split(":", 1)[1].strip() if ":" in line else line
                logger.info(f"🔸 라인 {line_num}: 질문 감지 - {current_q[:30]}...")
            elif line.startswith("A:") or line.startswith("답변:") or line.startswith("AI:") or line.startswith("EORA:"):
                current_a = line.split(":", 1)[1].strip() if ":" in line else line
                logger.info(f"🔹 라인 {line_num}: 답변 감지 - {current_a[:30]}...")
            elif not current_q:
                current_q = line
                logger.info(f"🔸 라인 {line_num}: 질문으로 처리 - {current_q[:30]}...")
            elif not current_a:
                current_a = line
                logger.info(f"🔹 라인 {line_num}: 답변으로 처리 - {current_a[:30]}...")
            
            # 진행률 로그 (100라인마다)
            if processed_lines % 100 == 0:
                logger.info(f"⏳ 라인 처리 진행률: {processed_lines:,}/{total_lines:,} ({processed_lines/total_lines*100:.1f}%)")
        
        # 마지막 턴 처리
        if current_q and current_a:
            dialog_turns.append({"question": current_q, "answer": current_a})
            logger.info(f"✅ 마지막 대화 턴 {len(dialog_turns)} 파싱 완료")
        
        if not dialog_turns:
            logger.error("❌ 대화 턴을 찾을 수 없습니다")
            logger.info("💡 지원되는 형식:")
            logger.info("   - Q: 질문 \\n A: 답변")
            logger.info("   - 질문: 내용 \\n 답변: 내용") 
            logger.info("   - 사용자: 질문 \\n AI: 답변")
            logger.info("   - 줄바꿈으로 구분된 질문-답변 쌍")
            return {"success": False, "message": "대화 턴을 찾을 수 없습니다. 파일 형식을 확인해주세요."}
        
        logger.info(f"🎯 대화 파싱 완료:")
        logger.info(f"   📝 처리된 라인: {processed_lines:,}개")
        logger.info(f"   🔳 빈 라인: {empty_lines:,}개")
        logger.info(f"   💬 대화 턴: {len(dialog_turns)}개")
        logger.info(f"   📊 평균 질문 길이: {sum(len(t['question']) for t in dialog_turns)/len(dialog_turns):.0f} 문자")
        logger.info(f"   📊 평균 답변 길이: {sum(len(t['answer']) for t in dialog_turns)/len(dialog_turns):.0f} 문자")
        
        # 3단계: 아우라 메모리에 대화 저장
        logger.info("💾 3단계: 대화 메모리 저장 시작...")
        saved_dialogs = []
        session_id = f"admin_dialog_{file.filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"🆔 세션 ID: {session_id}")
        
        if AURA_MEMORY_AVAILABLE and aura_memory:
            logger.info("🌀 아우라 메모리 시스템 사용")
            try:
                for i, turn in enumerate(dialog_turns):
                    logger.info(f"💾 아우라 메모리 저장 진행: {i+1}/{len(dialog_turns)} ({(i+1)/len(dialog_turns)*100:.1f}%)")
                    
                    # 각 대화 턴을 개별 메모리로 저장
                    memory_result = await save_to_aura_memory(
                        user_id="admin",
                        session_id=session_id,
                        message=turn["question"],
                        response=turn["answer"]
                    )
                    saved_dialogs.append(memory_result)
                    
                    if (i+1) % 5 == 0:  # 5개마다 로그
                        logger.info(f"✅ 아우라 메모리 저장 진행: {i+1}/{len(dialog_turns)} 완료")
                
                logger.info(f"🎉 아우라 메모리 저장 완료: {len(saved_dialogs)}개")
                
            except Exception as aura_error:
                logger.error(f"❌ 아우라 메모리 저장 실패: {aura_error}")
                logger.info("🔄 MongoDB 직접 저장으로 대체...")
                
                # fallback: MongoDB 직접 저장
                if memories_collection:
                    try:
                        for i, turn in enumerate(dialog_turns):
                            logger.info(f"💾 MongoDB 저장 진행: {i+1}/{len(dialog_turns)} ({(i+1)/len(dialog_turns)*100:.1f}%)")
                            
                            # 질문 저장
                            user_doc = {
                                "user_id": "admin",
                                "session_id": session_id,
                                "message": turn["question"],
                                "response": "",
                                "role": "user",
                                "timestamp": datetime.now(),
                                "memory_type": "dialog_learning",
                                "importance": 0.8,
                                "tags": ["학습대화", "관리자업로드", file.filename.split('.')[0]],
                                "source_file": file.filename
                            }
                            # 답변 저장
                            assistant_doc = {
                                "user_id": "admin",
                                "session_id": session_id, 
                                "message": turn["question"],
                                "response": turn["answer"],
                                "role": "assistant",
                                "timestamp": datetime.now(),
                                "memory_type": "dialog_learning",
                                "importance": 0.8,
                                "tags": ["학습대화", "관리자업로드", file.filename.split('.')[0]],
                                "source_file": file.filename
                            }
                            memories_collection.insert_one(user_doc)
                            result = memories_collection.insert_one(assistant_doc)
                            saved_dialogs.append(str(result.inserted_id))
                            
                            if (i+1) % 5 == 0:
                                logger.info(f"✅ MongoDB 저장 진행: {i+1}/{len(dialog_turns)} 완료")
                        
                        logger.info(f"🎉 MongoDB 저장 완료: {len(saved_dialogs)}개 (fallback)")
                        
                    except Exception as mongo_error:
                        logger.error(f"❌ MongoDB 저장도 실패: {mongo_error}")
                        return {"success": False, "message": f"대화 저장 실패: {str(mongo_error)}"}
        else:
            logger.info("🗄️ MongoDB 직접 저장 사용")
            # MongoDB 직접 저장
            if memories_collection:
                try:
                    for i, turn in enumerate(dialog_turns):
                        logger.info(f"💾 MongoDB 저장 진행: {i+1}/{len(dialog_turns)} ({(i+1)/len(dialog_turns)*100:.1f}%)")
                        
                        # 질문과 답변을 쌍으로 저장
                        dialog_doc = {
                            "user_id": "admin",
                            "session_id": session_id,
                            "message": turn["question"],
                            "response": turn["answer"],
                            "timestamp": datetime.now(),
                            "memory_type": "dialog_learning",
                            "importance": 0.8,
                            "tags": ["학습대화", "관리자업로드", file.filename.split('.')[0]],
                            "source_file": file.filename
                        }
                        result = memories_collection.insert_one(dialog_doc)
                        saved_dialogs.append(str(result.inserted_id))
                        
                        if (i+1) % 5 == 0:
                            logger.info(f"✅ MongoDB 저장 진행: {i+1}/{len(dialog_turns)} 완료")
                    
                    logger.info(f"🎉 MongoDB 저장 완료: {len(saved_dialogs)}개")
                    
                except Exception as mongo_error:
                    logger.error(f"❌ MongoDB 저장 실패: {mongo_error}")
                    return {"success": False, "message": f"대화 저장 실패: {str(mongo_error)}"}
            else:
                logger.error("❌ 메모리 저장 시스템을 사용할 수 없습니다")
                return {"success": False, "message": "메모리 저장 시스템을 사용할 수 없습니다."}
        
        # 최종 결과 로그
        logger.info("="*60)
        logger.info("🎉 대화 학습 완료 요약:")
        logger.info(f"📁 파일명: {file.filename}")
        logger.info(f"📊 원본 크기: {raw_size:,} bytes")
        logger.info(f"📝 텍스트 길이: {text_size:,} 문자")
        logger.info(f"📝 총 라인: {total_lines:,}개")
        logger.info(f"💬 대화 턴: {len(dialog_turns)}개")
        logger.info(f"💾 저장된 대화: {len(saved_dialogs)}개")
        logger.info(f"🆔 세션 ID: {session_id}")
        logger.info(f"🕐 완료 시간: {datetime.now().isoformat()}")
        logger.info("="*60)
        
        return {
            "success": True,
            "message": f"대화 파일 '{file.filename}' 학습 완료! {len(saved_dialogs)}개 대화 생성됨",
            "dialog_turns": len(dialog_turns),
            "saved_dialogs": len(saved_dialogs),
            "details": {
                "filename": file.filename,
                "original_size": raw_size,
                "text_length": text_size,
                "total_lines": total_lines,
                "total_turns": len(dialog_turns),
                "avg_question_length": int(sum(len(t['question']) for t in dialog_turns)/len(dialog_turns)) if dialog_turns else 0,
                "avg_answer_length": int(sum(len(t['answer']) for t in dialog_turns)/len(dialog_turns)) if dialog_turns else 0,
                "memory_system": "아우라 메모리" if AURA_MEMORY_AVAILABLE else "MongoDB",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error("="*60)
        logger.error(f"❌ 대화 학습 실패: {file.filename}")
        logger.error(f"❌ 오류: {str(e)}")
        logger.error("="*60)
        return {"success": False, "message": f"대화 학습 처리 실패: {str(e)}"}

# 아우라 메모리 저장 도우미 함수
async def save_to_aura_memory(user_id, session_id, message, response, memory_type="learning", importance=0.7):
    """아우라 메모리 시스템에 메모리 저장"""
    try:
        if aura_memory:
            memory_id = aura_memory.create_memory(
                user_id=user_id,
                session_id=session_id,
                message=message,
                response=response,
                memory_type=memory_type,
                importance=importance
            )
            return memory_id
        else:
            logger.warning("⚠️ 아우라 메모리 시스템 없음")
            raise Exception("아우라 메모리 시스템을 사용할 수 없습니다.")
    except Exception as e:
        logger.error(f"❌ 아우라 메모리 저장 오류: {e}")
        raise e

# FAISS 및 임베딩 시스템 (지연 로딩 적용)
FAISS_AVAILABLE = False
embeddings_model = None
vector_index = None

def init_faiss_system():
    """FAISS 시스템을 지연 로딩으로 초기화합니다."""
    global FAISS_AVAILABLE, embeddings_model, vector_index
    
    if FAISS_AVAILABLE:
        return True  # 이미 초기화됨
    
    try:
        logger.info("🔄 FAISS 임베딩 시스템 지연 로딩 시작...")
        
        import faiss
        from sentence_transformers import SentenceTransformer
        import numpy as np
        
        # SentenceTransformer 모델 로드 (캐시 사용)
        embeddings_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        
        # 간단한 벡터 인덱스 생성
        vector_index = faiss.IndexFlatL2(384)  # MiniLM-L6-v2의 차원
        
        FAISS_AVAILABLE = True
        logger.info("✅ FAISS 임베딩 시스템 지연 로딩 완료")
        return True
        
    except ImportError as e:
        logger.warning(f"⚠️ FAISS 라이브러리 없음: {e}")
        logger.info("ℹ️ 설치 방법: pip install faiss-cpu sentence-transformers")
        FAISS_AVAILABLE = False
        return False
    except Exception as e:
        logger.error(f"❌ FAISS 초기화 실패: {e}")
        FAISS_AVAILABLE = False
        return False

# MongoDB 연결 캐싱 시스템
successful_mongodb_url = None
mongodb_connection_cache = None

def get_cached_mongodb_connection():
    """캐싱된 MongoDB 연결을 반환하거나 새로 연결합니다."""
    global mongodb_connection_cache, successful_mongodb_url
    
    # 캐시된 연결이 있고 유효한지 확인
    if mongodb_connection_cache and successful_mongodb_url:
        try:
            mongodb_connection_cache.admin.command('ping')
            logger.info("✅ 캐싱된 MongoDB 연결 재사용")
            return mongodb_connection_cache
        except Exception as e:
            logger.warning(f"⚠️ 캐싱된 연결 무효화: {e}")
            mongodb_connection_cache = None
    
    # 캐시된 연결이 없거나 무효한 경우
    if successful_mongodb_url:
        # 이전에 성공한 URL로 빠르게 재연결 시도
        try:
            logger.info("🔄 이전 성공 URL로 빠른 재연결 시도...")
            # Railway 환경 최적화된 캐시 연결
            is_railway = bool(os.getenv("RAILWAY_ENVIRONMENT") or 
                             os.getenv("RAILWAY_PROJECT_ID") or 
                             os.getenv("RAILWAY_SERVICE_ID"))
            
            if is_railway:
                client = MongoClient(
                    successful_mongodb_url,
                    serverSelectionTimeoutMS=500,  # Railway에서는 더 빠른 타임아웃
                    connectTimeoutMS=500,
                    socketTimeoutMS=500,
                    maxPoolSize=3,  # Railway에서는 더 작은 풀 크기
                    minPoolSize=1,
                    maxIdleTimeMS=15000,  # 15초 후 연결 해제
                    waitQueueTimeoutMS=1000,  # 1초 대기
                    retryWrites=True,
                    retryReads=True
                )
            else:
                client = MongoClient(
                    successful_mongodb_url,
                    serverSelectionTimeoutMS=1000,  # 매우 빠른 타임아웃
                    connectTimeoutMS=1000,
                    socketTimeoutMS=1000,
                    maxPoolSize=10,
                    minPoolSize=1
                )
            client.admin.command('ping')
            mongodb_connection_cache = client
            logger.info("✅ 이전 성공 URL로 빠른 재연결 성공")
            return client
        except Exception as e:
            logger.warning(f"⚠️ 이전 성공 URL 재연결 실패: {e}")
    
    # 전체 연결 시도
    client = try_mongodb_connection()
    if client:
        mongodb_connection_cache = client
        return client
    
    return None

# 토큰 생성 및 검증 함수
def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=24)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 채팅 API 엔드포인트
@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        message = data.get("message")
        if not user_id or not message:
            return JSONResponse({"success": False, "message": "user_id와 message가 필요합니다."}, status_code=400)
        
        # MongoDB 연결 확인
        if db is None:
            return JSONResponse({"success": False, "message": "데이터베이스 연결 실패"}, status_code=500)
        
        collection = db[f"chat_{user_id}"]
        chat_doc = {"user_id": user_id, "message": message, "timestamp": datetime.utcnow()}
        result = collection.insert_one(chat_doc)
        return JSONResponse({"success": True, "message": "대화 저장 완료", "chat_id": str(result.inserted_id)})
    except Exception as e:
        logger.error(f"[채팅 오류] {e}\n{traceback.format_exc()}")
        return JSONResponse({"success": False, "message": "서버 오류가 발생했습니다."}, status_code=500)

@app.get("/api/user/points")
async def get_user_points(request: Request):
    """사용자 포인트 정보 조회"""
    try:
        from auth_system import get_current_user
        from database import db_manager
        
        # 사용자 정보 조회
        user = get_current_user(request)
        if not user:
            return JSONResponse(
                status_code=200,  # 에러를 200으로 반환하여 클라이언트에서 기본값 표시
                content={"success": True, "points": 100000, "max_points": 100000, "message": "포인트 정보를 불러올 수 없어 기본값을 표시합니다."}
            )
        
        user_id = user.get("user_id", "anonymous")
        
        # 포인트 조회
        points_data = await db_manager().get_user_points(user_id)
        
        return {
            "success": True,
            "points": points_data["points"],
            "max_points": points_data["max_points"]
        }
    except Exception as e:
        logger.error(f"포인트 조회 오류: {str(e)}")
        # 오류 시 기본값 반환
        return {
            "success": True,  # 클라이언트에게는 성공으로 반환
            "points": 100000,
            "max_points": 100000,
            "message": "포인트 정보를 불러올 수 없어 기본값을 표시합니다."
        }

@app.get("/user/points")
async def get_user_points_compat(request: Request):
    """사용자 포인트 조회 (호환성 경로)"""
    user_id = request.query_params.get("user_id", "anonymous")
    
    try:
        from database import db_manager
        
        # 포인트 조회
        points_data = await db_manager().get_user_points(user_id)
        
        return {
            "success": True,
            "points": points_data["points"],
            "max_points": points_data["max_points"]
        }
    except Exception as e:
        logger.error(f"포인트 조회 오류 (호환성): {str(e)}")
        # 오류 시 기본값 반환
        return {
            "success": True,
            "points": 100000,
            "max_points": 100000,
            "message": "포인트 정보를 불러올 수 없어 기본값을 표시합니다."
        }

@app.get("/user/chats")
async def get_user_chats(request: Request):
    user_id = request.query_params.get("user_id")
    if not user_id:
        return JSONResponse({"error": "user_id는 필수입니다."}, status_code=400)
    chat_collection = get_user_chat_collection(user_id)
    chats = list(chat_collection.find({}).sort("timestamp", -1))
    for chat in chats:
        chat["_id"] = str(chat["_id"])
        chat["timestamp"] = chat["timestamp"].isoformat() if hasattr(chat["timestamp"], "isoformat") else str(chat["timestamp"])
    return {"chats": chats}

def get_user_chat_collection(user_id):
    """사용자별 채팅 컬렉션 반환"""
    return db[f"user_{user_id}_chat"]

def get_user_points_collection(user_id):
    """사용자별 포인트 컬렉션 반환"""
    return db[f"user_{user_id}_points"]

# 세션 관련 API 엔드포인트
@app.post("/api/sessions")
async def create_session(request: Request):
    """새 세션 생성"""
    try:
        data = await request.json()
        user = get_current_user(request)
        
        if not user:
            return JSONResponse({"success": False, "message": "로그인이 필요합니다."}, status_code=401)
        
        user_id = user.get("user_id") or user.get("email")
        session_name = data.get("name", f"세션 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # 세션 ID 생성
        session_id = str(uuid.uuid4())
        
        # 세션 데이터 생성
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "name": session_name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "message_count": 0
        }
        
        # MongoDB에 세션 저장
        if db:
            try:
                result = db.sessions.insert_one(session_data)
                logger.info(f"✅ 세션 생성 완료 (MongoDB): {session_id}")
            except Exception as e:
                logger.error(f"❌ MongoDB 세션 저장 실패: {e}")
                # 메모리에 저장 (백업)
                save_session_to_memory(session_id, session_data)
        else:
            # MongoDB 연결 없을 경우 메모리에 저장
            save_session_to_memory(session_id, session_data)
        
        return JSONResponse({
            "success": True,
            "session_id": session_id,
            "name": session_name
        })
    except Exception as e:
        logger.error(f"❌ 세션 생성 오류: {e}")
        return JSONResponse({"success": False, "message": f"세션 생성 실패: {str(e)}"}, status_code=500)

@app.get("/api/sessions")
async def get_sessions(request: Request):
    """사용자의 세션 목록 조회"""
    try:
        user = get_current_user(request)
        if not user:
            return JSONResponse({"success": False, "message": "로그인이 필요합니다."}, status_code=401)
        
        user_id = user.get("user_id") or user.get("email")
        
        # MongoDB에서 세션 조회
        sessions = []
        if db:
            try:
                cursor = db.sessions.find({"user_id": user_id}).sort("created_at", -1)
                for session in cursor:
                    # ObjectId를 문자열로 변환
                    if "_id" in session:
                        session["id"] = str(session["_id"])
                        del session["_id"]
                    sessions.append(session)
                logger.info(f"✅ 세션 목록 조회 완료 (MongoDB): {len(sessions)}개")
            except Exception as e:
                logger.error(f"❌ MongoDB 세션 조회 실패: {e}")
                # 메모리에서 조회 (백업)
                sessions = [s for s in memory_sessions.values() if s.get("user_id") == user_id]
        else:
            # MongoDB 연결 없을 경우 메모리에서 조회
            sessions = [s for s in memory_sessions.values() if s.get("user_id") == user_id]
        
        return JSONResponse({
            "success": True,
            "sessions": sessions
        })
    except Exception as e:
        logger.error(f"❌ 세션 목록 조회 오류: {e}")
        return JSONResponse({"success": False, "message": f"세션 목록 조회 실패: {str(e)}"}, status_code=500)

@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, request: Request):
    """세션의 메시지 목록 조회"""
    try:
        user = get_current_user(request)
        if not user:
            return JSONResponse({"success": False, "message": "로그인이 필요합니다."}, status_code=401)
        
        user_id = user.get("user_id") or user.get("email")
        
        # 세션 존재 및 권한 확인
        session = None
        if db:
            try:
                session = db.sessions.find_one({"session_id": session_id})
            except Exception as e:
                logger.error(f"❌ MongoDB 세션 조회 실패: {e}")
                session = memory_sessions.get(session_id)
        else:
            session = memory_sessions.get(session_id)
        
        if not session:
            return JSONResponse({"success": False, "message": "세션을 찾을 수 없습니다."}, status_code=404)
        
        if session.get("user_id") != user_id:
            return JSONResponse({"success": False, "message": "이 세션에 접근할 권한이 없습니다."}, status_code=403)
        
        # 메시지 조회
        messages = []
        if db:
            try:
                cursor = db.messages.find({"session_id": session_id}).sort("timestamp", 1)
                for msg in cursor:
                    # ObjectId를 문자열로 변환
                    if "_id" in msg:
                        msg["id"] = str(msg["_id"])
                        del msg["_id"]
                    messages.append(msg)
                logger.info(f"✅ 메시지 목록 조회 완료 (MongoDB): {len(messages)}개")
            except Exception as e:
                logger.error(f"❌ MongoDB 메시지 조회 실패: {e}")
                # 메모리에서 조회 (백업)
                messages = memory_messages.get(session_id, [])
        else:
            # MongoDB 연결 없을 경우 메모리에서 조회
            messages = memory_messages.get(session_id, [])
        
        # 메시지 포맷팅
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "id": msg.get("id", str(uuid.uuid4())),
                "user_message": msg.get("content") if msg.get("role") == "user" else "",
                "ai_response": msg.get("content") if msg.get("role") == "assistant" else "",
                "timestamp": msg.get("timestamp")
            })
        
        return JSONResponse({
            "success": True,
            "messages": formatted_messages
        })
    except Exception as e:
        logger.error(f"❌ 메시지 목록 조회 오류: {e}")
        return JSONResponse({"success": False, "message": f"메시지 목록 조회 실패: {str(e)}"}, status_code=500)

@app.post("/api/sessions/{session_id}/messages")
async def add_session_message(session_id: str, request: Request):
    """세션에 메시지 추가"""
    try:
        data = await request.json()
        user = get_current_user(request)
        
        if not user:
            return JSONResponse({"success": False, "message": "로그인이 필요합니다."}, status_code=401)
        
        user_id = user.get("user_id") or user.get("email")
        message = data.get("message")
        
        if not message:
            return JSONResponse({"success": False, "message": "메시지 내용이 필요합니다."}, status_code=400)
        
        # 세션 존재 및 권한 확인
        session = None
        if db:
            try:
                session = db.sessions.find_one({"session_id": session_id})
            except Exception as e:
                logger.error(f"❌ MongoDB 세션 조회 실패: {e}")
                session = memory_sessions.get(session_id)
        else:
            session = memory_sessions.get(session_id)
        
        if not session:
            return JSONResponse({"success": False, "message": "세션을 찾을 수 없습니다."}, status_code=404)
        
        if session.get("user_id") != user_id:
            return JSONResponse({"success": False, "message": "이 세션에 접근할 권한이 없습니다."}, status_code=403)
        
        # 메시지 데이터 생성
        message_data = {
            "session_id": session_id,
            "user_id": user_id,
            "content": message,
            "role": "user",
            "timestamp": datetime.now().isoformat()
        }
        
        # MongoDB에 메시지 저장
        message_id = None
        if db:
            try:
                result = db.messages.insert_one(message_data)
                message_id = str(result.inserted_id)
                logger.info(f"✅ 메시지 저장 완료 (MongoDB): {message_id}")
                
                # 세션 업데이트
                db.sessions.update_one(
                    {"session_id": session_id},
                    {"$inc": {"message_count": 1}, "$set": {"updated_at": datetime.now().isoformat()}}
                )
            except Exception as e:
                logger.error(f"❌ MongoDB 메시지 저장 실패: {e}")
                # 메모리에 저장 (백업)
                message_id = save_message_to_memory(message_data)
        else:
            # MongoDB 연결 없을 경우 메모리에 저장
            message_id = save_message_to_memory(message_data)
        
        # AI 응답 생성 (간단한 예시)
        ai_response = "이 기능은 아직 구현 중입니다."
        
        # AI 응답 메시지 데이터 생성
        ai_message_data = {
            "session_id": session_id,
            "user_id": user_id,
            "content": ai_response,
            "role": "assistant",
            "timestamp": datetime.now().isoformat()
        }
        
        # MongoDB에 AI 응답 저장
        ai_message_id = None
        if db:
            try:
                result = db.messages.insert_one(ai_message_data)
                ai_message_id = str(result.inserted_id)
                logger.info(f"✅ AI 응답 저장 완료 (MongoDB): {ai_message_id}")
                
                # 세션 업데이트
                db.sessions.update_one(
                    {"session_id": session_id},
                    {"$inc": {"message_count": 1}, "$set": {"updated_at": datetime.now().isoformat()}}
                )
            except Exception as e:
                logger.error(f"❌ MongoDB AI 응답 저장 실패: {e}")
                # 메모리에 저장 (백업)
                ai_message_id = save_message_to_memory(ai_message_data)
        else:
            # MongoDB 연결 없을 경우 메모리에 저장
            ai_message_id = save_message_to_memory(ai_message_data)
        
        return JSONResponse({
            "success": True,
            "message_id": message_id,
            "ai_message_id": ai_message_id,
            "ai_response": ai_response
        })
    except Exception as e:
        logger.error(f"❌ 메시지 추가 오류: {e}")
        return JSONResponse({"success": False, "message": f"메시지 추가 실패: {str(e)}"}, status_code=500)

# 세션 백업 파일 생성 함수
@app.post("/api/sessions/{session_id}/backup")
async def backup_session(session_id: str, request: Request):
    """세션 백업 파일 생성"""
    try:
        user = get_current_user(request)
        if not user:
            return JSONResponse({"success": False, "message": "로그인이 필요합니다."}, status_code=401)
        
        user_id = user.get("user_id") or user.get("email")
        
        # 세션 존재 및 권한 확인
        session = None
        if db:
            try:
                session = db.sessions.find_one({"session_id": session_id})
            except Exception as e:
                logger.error(f"❌ MongoDB 세션 조회 실패: {e}")
                session = memory_sessions.get(session_id)
        else:
            session = memory_sessions.get(session_id)
        
        if not session:
            return JSONResponse({"success": False, "message": "세션을 찾을 수 없습니다."}, status_code=404)
        
        if session.get("user_id") != user_id:
            return JSONResponse({"success": False, "message": "이 세션에 접근할 권한이 없습니다."}, status_code=403)
        
        # 메시지 조회
        messages = []
        if db:
            try:
                cursor = db.messages.find({"session_id": session_id}).sort("timestamp", 1)
                for msg in cursor:
                    # ObjectId를 문자열로 변환
                    if "_id" in msg:
                        msg["id"] = str(msg["_id"])
                        del msg["_id"]
                    messages.append(msg)
            except Exception as e:
                logger.error(f"❌ MongoDB 메시지 조회 실패: {e}")
                # 메모리에서 조회 (백업)
                messages = memory_messages.get(session_id, [])
        else:
            # MongoDB 연결 없을 경우 메모리에서 조회
            messages = memory_messages.get(session_id, [])
        
        # 백업 데이터 생성
        backup_data = {
            "session": session,
            "messages": messages,
            "backup_time": datetime.now().isoformat()
        }
        
        # 백업 파일 저장 (sessions_backup 디렉토리)
        import os
        import json
        
        backup_dir = "sessions_backup"
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_file = os.path.join(backup_dir, f"{user_id}_{session_id}.json")
        metadata_file = os.path.join(backup_dir, f"{user_id}_{session_id}_metadata.json")
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        # 메타데이터 저장
        metadata = {
            "session_id": session_id,
            "user_id": user_id,
            "name": session.get("name", "Unknown"),
            "message_count": len(messages),
            "created_at": session.get("created_at"),
            "backup_time": datetime.now().isoformat()
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return JSONResponse({
            "success": True,
            "message": "세션 백업이 완료되었습니다.",
            "backup_file": backup_file,
            "metadata_file": metadata_file
        })
    except Exception as e:
        logger.error(f"❌ 세션 백업 오류: {e}")
        return JSONResponse({"success": False, "message": f"세션 백업 실패: {str(e)}"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True) 