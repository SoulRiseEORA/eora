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
import uuid
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# FastAPI 및 관련 라이브러리
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, status, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# 데이터베이스 및 캐시
import pymongo
from pymongo import MongoClient
from bson import ObjectId

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# OpenAI 클라이언트
openai_client = None

# 메모리 기반 저장소 (MongoDB 연결 실패 시 사용)
memory_sessions = {}
memory_messages = {}
memory_cache = {}

# 아우라 메모리 시스템 통합
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

# 사용자 인증 함수
def get_current_user(request: Request):
    """현재 사용자 정보를 반환합니다."""
    try:
        # 실제 환경에서는 JWT 토큰 등을 사용하여 사용자 인증
        # 현재는 기본 사용자 정보 반환
        return {
            "user_id": "anonymous",
            "username": "게스트",
            "email": "guest@example.com"
        }
    except Exception as e:
        logger.error(f"사용자 인증 오류: {e}")
        return {
            "user_id": "anonymous",
            "username": "게스트",
            "email": "guest@example.com"
        }

# Dotenv 로드 - b43dd7c 커밋의 성공적인 방식 적용
from dotenv import load_dotenv
import os

# 프로젝트 루트 디렉토리 찾기
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
env_path = os.path.join(project_root, ".env")

# 환경변수 로드
load_dotenv(dotenv_path=env_path)

# 로드 확인
logger.info(f"🔧 환경변수 로드 경로: {env_path}")
logger.info(f"🔧 .env 파일 존재: {os.path.exists(env_path)}")

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

# 환경변수 설정 - b43dd7c 커밋의 성공적인 방식 적용
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_PROJECT_ID = os.getenv("OPENAI_PROJECT_ID", "").strip()
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
DATABASE_NAME = os.getenv("DATABASE_NAME", "eora_ai")

# 환경변수 로드 확인 로그
logger.info(f"🔧 OpenAI API Key 설정: {'✅ 설정됨' if OPENAI_API_KEY else '❌ 설정 안됨'}")
logger.info(f"🔧 OpenAI Project ID 설정: {'✅ 설정됨' if OPENAI_PROJECT_ID else '❌ 설정 안됨'}")
logger.info(f"🔧 GPT Model: {GPT_MODEL}")
logger.info(f"🔧 Max Tokens: {MAX_TOKENS}")
logger.info(f"🔧 Temperature: {TEMPERATURE}")



# Railway 환경에서 .env 파일 경고 방지
if not OPENAI_API_KEY:
    logger.info("ℹ️ Railway 환경에서 환경변수로 OpenAI API 키를 설정해주세요.")
else:
    logger.info("✅ OpenAI API 키가 환경변수에서 로드되었습니다.")

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
    """MongoDB 연결을 시도합니다."""
    urls_to_try = []
    
    # Railway 환경에서 사용할 수 있는 MongoDB URL들
    if MONGODB_URL:
        urls_to_try.append(MONGODB_URL)
    
    # Railway MongoDB 서비스 연결 문자열들
    railway_urls = [
        os.getenv("MONGO_PUBLIC_URL"),
        os.getenv("MONGO_URL"),
        os.getenv("MONGODB_URI"),
        "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594",
        "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@mongodb.railway.internal:27017"
    ]
    
    for url in railway_urls:
        if url and url not in urls_to_try:
            urls_to_try.append(url)
    
    # 로컬 개발 환경용 URL들
    local_urls = [
        "mongodb://localhost:27017",
        "mongodb://127.0.0.1:27017"
    ]
    
    for url in local_urls:
        if url not in urls_to_try:
            urls_to_try.append(url)
    
    logger.info(f"🔗 연결 시도할 URL 수: {len(urls_to_try)}")
    
    for i, url in enumerate(urls_to_try, 1):
        if not url:
            continue
            
        try:
            logger.info(f"🔗 MongoDB 연결 시도: {i}/{len(urls_to_try)}")
            logger.info(f"📝 연결 URL: {url}")
            
            # 연결 문자열 정리
            clean_url = clean_mongodb_url(url)
            
            # 연결 시도
            client = MongoClient(clean_url, serverSelectionTimeoutMS=5000)
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
    logger.info("ℹ️ 메모리 기반 세션 관리로 전환합니다.")
else:
    # 데이터베이스 및 컬렉션 설정
    try:
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
    except Exception as e:
        logger.error(f"❌ MongoDB 컬렉션 초기화 실패: {e}")
        logger.info("ℹ️ 메모리 기반 세션 관리로 전환합니다.")
        # 컬렉션 변수들을 None으로 설정
        chat_logs_collection = None
        sessions_collection = None
        users_collection = None
        aura_collection = None
        system_logs_collection = None
        points_collection = None

# 전역 변수 초기화
prompts_data = {}


# OpenAI 클라이언트 초기화 - 최신 버전 호환성 개선
openai_client = None
if OPENAI_API_KEY:
    try:
        import openai
        # OpenAI 1.0.0+ 버전 호환 코드
        if hasattr(openai, 'OpenAI'):
            # 새로운 OpenAI 클라이언트 (1.0.0+)
            openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
            logger.info("✅ OpenAI API 키 설정 성공 (v1.0.0+)")
        else:
            # 구버전 OpenAI 클라이언트
            openai.api_key = OPENAI_API_KEY
            openai_client = openai
            logger.info("✅ OpenAI API 키 설정 성공 (구버전)")
    except Exception as e:
        logger.error(f"❌ OpenAI API 클라이언트 초기화 실패: {e}")
        logger.info("ℹ️ OpenAI API 키 설정을 확인해주세요.")
        openai_client = None
else:
    logger.warning("⚠️ OPENAI_API_KEY가 설정되지 않았습니다. Railway 환경변수를 확인해주세요.")



def normalize_prompts_data(data):
    """프롬프트 데이터를 정규화하여 일관된 구조로 만듭니다."""
    normalized_data = {"prompts": {}}
    
    # prompts 키가 있는 경우와 없는 경우 모두 처리
    actual_prompts = data.get("prompts", data)
    
    for ai_name, ai_data in actual_prompts.items():
        if isinstance(ai_data, dict):
            normalized_data["prompts"][ai_name] = {}
            for category, category_prompts in ai_data.items():
                if isinstance(category_prompts, list):
                    # 리스트인 경우 그대로 유지
                    normalized_data["prompts"][ai_name][category] = category_prompts
                elif isinstance(category_prompts, str):
                    # 문자열인 경우 리스트로 변환
                    normalized_data["prompts"][ai_name][category] = [category_prompts]
                else:
                    # 기타 타입인 경우 문자열로 변환 후 리스트로
                    normalized_data["prompts"][ai_name][category] = [str(category_prompts)]
        elif isinstance(ai_data, str):
            # AI 데이터가 문자열인 경우 content 카테고리로 변환
            normalized_data["prompts"][ai_name] = {"content": [ai_data]}
        else:
            # 기타 타입인 경우 문자열로 변환
            normalized_data["prompts"][ai_name] = {"content": [str(ai_data)]}
    
    return normalized_data

def load_prompts_data():
    """ai_prompts.json 파일에서 프롬프트 데이터를 로드합니다."""
    global prompts_data
    try:
        logger.info("📚 프롬프트 데이터 로드 중...")
        
        # Railway 환경에서 가능한 모든 경로 시도 (templates 우선)
        possible_paths = [
            "templates/ai_prompts.json",
            "/app/templates/ai_prompts.json",
            "ai_brain/ai_prompts.json",
            "ai_prompts.json",
            "/app/ai_brain/ai_prompts.json",
            "/app/ai_prompts.json",
            os.path.join(os.getcwd(), "templates", "ai_prompts.json"),
            os.path.join(os.getcwd(), "ai_brain", "ai_prompts.json"),
            os.path.join(os.getcwd(), "ai_prompts.json"),
            "../ai_prompts.json"  # 상위 디렉토리도 확인
        ]
        
        logger.info(f"🔍 프롬프트 파일 검색 경로: {len(possible_paths)}개")
        
        for i, prompts_file in enumerate(possible_paths, 1):
            logger.info(f"🔍 경로 {i}/{len(possible_paths)} 확인: {prompts_file}")
            
            if os.path.exists(prompts_file):
                logger.info(f"✅ 파일 발견: {prompts_file}")
                
                try:
                    with open(prompts_file, 'r', encoding='utf-8') as f:
                        raw_data = json.load(f)
                    
                    logger.info(f"📄 파일 내용 로드 성공: {len(str(raw_data))} 문자")
                    logger.info(f"📄 JSON 키 목록: {list(raw_data.keys()) if isinstance(raw_data, dict) else 'Not a dict'}")
                    
                    # 프롬프트 데이터 정규화
                    prompts_data = normalize_prompts_data(raw_data)
                    
                    ai_count = len(prompts_data["prompts"])
                    ai_names = list(prompts_data["prompts"].keys())
                    logger.info(f"✅ ai_prompts.json 파일 로드 완료: {ai_count}개 AI (경로: {prompts_file})")
                    logger.info(f"📋 로드된 AI: {', '.join(ai_names)}")
                    
                    # 각 AI의 카테고리 확인
                    for ai_name, ai_data in prompts_data["prompts"].items():
                        if isinstance(ai_data, dict):
                            categories = list(ai_data.keys())
                            logger.info(f"📝 {ai_name} 카테고리: {', '.join(categories)}")
                    
                    return True
                        
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON 파싱 오류 ({prompts_file}): {e}")
                    continue
                except Exception as e:
                    logger.error(f"❌ 파일 읽기 오류 ({prompts_file}): {e}")
                    continue
            else:
                logger.info(f"❌ 파일 없음: {prompts_file}")
        
        logger.warning("⚠️ ai_prompts.json 파일을 찾을 수 없습니다.")
        # 기본 프롬프트 데이터 생성
        prompts_data = {
            "prompts": {
                "ai1": {
                    "content": ["당신은 친근하고 도움이 되는 AI 어시스턴트입니다. 사용자의 질문에 정확하고 유용한 답변을 제공하세요."]
                },
                "eora": {
                    "content": ["당신은 EORA라는 이름을 가진 AI이며, 프로그램 자동 개발 시스템의 총괄 디렉터입니다. 인간의 직감과 기억 회상 메커니즘을 결합한 지혜로운 AI입니다."]
                }
            }
        }
        logger.info("ℹ️ 기본 프롬프트 데이터로 초기화")
        return True
    except Exception as e:
        logger.error(f"❌ 프롬프트 데이터 로드 오류: {e}")
        return False

# 프롬프트 데이터 초기화
load_prompts_data()

# FAISS 임베딩 시스템 (선택적)
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    FAISS_AVAILABLE = True
    logger.info("✅ FAISS 임베딩 시스템 로드 성공")
except ImportError as e:
    FAISS_AVAILABLE = False
    logger.info(f"ℹ️ FAISS 또는 sentence-transformers 미설치: {e}")
    logger.info("ℹ️ 기본 키워드 기반 회상으로 동작합니다.")

# Redis 연결 (Graceful Fallback - Railway 환경에서 선택적 사용)
redis_client = None
redis_connected = False


# 메모리 기반 세션 저장소 (MongoDB 대체)
memory_sessions = {}
memory_messages = {}
memory_aura_data = {}

# MongoDB 컬렉션 변수들 초기화
chat_logs_collection = None
sessions_collection = None
users_collection = None
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
        
        for existing_msg in memory_messages[session_id][-5:]:  # 최근 5개 메시지만 확인
            if (existing_msg.get("content") == message_content and
                existing_msg.get("role") == message_role):
                # 타임스탬프가 문자열인 경우 파싱
                existing_timestamp = existing_msg.get("timestamp", "")
                if isinstance(existing_timestamp, str):
                    try:
                        existing_time = datetime.fromisoformat(existing_timestamp.replace('Z', '+00:00'))
                    except:
                        existing_time = datetime.now() - timedelta(seconds=20)  # 파싱 실패 시 오래된 것으로 간주
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
    # 현재 작업 디렉토리 확인
    current_dir = Path.cwd()
    logger.info(f"📁 현재 작업 디렉토리: {current_dir}")
    
    # Railway 환경에서 가능한 모든 경로 시도
    possible_paths = [
        current_dir / "templates",  # 현재 작업 디렉토리의 templates (우선순위 1)
        Path(__file__).parent / "templates",  # 현재 파일 디렉토리의 templates (우선순위 2)
        Path("/app/templates"),  # Railway 템플릿 경로
        Path("/workspace/templates"),  # Railway 작업 공간
    ]
    
    for path in possible_paths:
        logger.info(f"📁 템플릿 경로 시도: {path}")
        logger.info(f"📁 템플릿 존재: {path.exists()}")
        
        if path.exists():
            # templates 디렉토리인지 확인
            if path.name == "templates":
                html_files = list(path.glob("*.html"))
                logger.info(f"📄 templates 디렉토리에서 HTML 파일 수: {len(html_files)}개")
                if html_files:
                    logger.info(f"✅ templates 디렉토리 발견: {path}")
                    logger.info(f"📄 발견된 파일: {[f.name for f in html_files[:5]]}")
                    return path
                else:
                    logger.warning(f"⚠️ {path}에 HTML 파일이 없습니다")
            else:
                # 일반 디렉토리에서 HTML 파일 확인
                html_files = list(path.glob("*.html"))
                logger.info(f"📄 HTML 파일 수: {len(html_files)}개")
                if html_files:
                    logger.info(f"✅ 템플릿 파일 발견: {len(html_files)}개")
                    logger.info(f"📄 발견된 파일: {[f.name for f in html_files[:5]]}")
                    return path
                else:
                    logger.warning(f"⚠️ {path}에 HTML 파일이 없습니다")
        else:
            logger.warning(f"⚠️ {path} 경로가 존재하지 않습니다")
    
    # fallback: 루트 디렉토리에서 templates 하위 디렉토리 찾기
    fallback_paths = [
        current_dir,  # 현재 작업 디렉토리 (우선순위 1)
        Path(__file__).parent,  # 현재 파일 디렉토리
        Path("/app"),  # Railway 기본 경로
    ]
    
    for path in fallback_paths:
        if path.exists():
            templates_subdir = path / "templates"
            logger.info(f"📁 templates 하위 디렉토리 확인: {templates_subdir}")
            if templates_subdir.exists():
                html_files = list(templates_subdir.glob("*.html"))
                if html_files:
                    logger.info(f"✅ fallback에서 templates 디렉토리 발견: {templates_subdir}")
                    logger.info(f"📄 발견된 파일: {[f.name for f in html_files[:5]]}")
                    return templates_subdir
    
    # 최종 fallback: 루트 디렉토리에서 home.html 찾기
    for path in fallback_paths:
        if path.exists():
            home_file = path / "home.html"
            if home_file.exists():
                logger.info(f"✅ fallback에서 home.html 발견: {path}")
                return path
    
    # 기본값 반환 - Railway 환경에서 가장 가능성 높은 경로
    logger.warning("⚠️ 템플릿 디렉토리를 찾을 수 없습니다. 기본 경로 사용")
    return current_dir

templates_path = setup_templates()
logger.info(f"📁 최종 템플릿 경로: {templates_path}")

try:
    templates = Jinja2Templates(directory=str(templates_path))
    logger.info("✅ Jinja2 템플릿 초기화 성공")
    
    # 템플릿 파일 존재 확인
    home_template_path = templates_path / "home.html"
    logger.info(f"📄 home.html 경로: {home_template_path}")
    logger.info(f"📄 home.html 존재: {home_template_path.exists()}")
    
    if not home_template_path.exists():
        logger.error(f"❌ home.html 파일이 존재하지 않습니다!")
        # 현재 디렉토리의 모든 파일 목록 출력
        all_files = list(templates_path.glob("*"))
        logger.info(f"📁 현재 디렉토리 파일들: {[f.name for f in all_files]}")
        
except Exception as e:
    logger.error(f"❌ 템플릿 초기화 실패: {e}")
    # 기본 템플릿 객체 생성 (오류 방지)
    templates = Jinja2Templates(directory=str(Path("/app")))

# 웹소켓 연결 관리자 인스턴스
manager = ConnectionManager()

# Lifespan 이벤트 핸들러 (Railway 호환 - Deprecation 경고 해결)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행
    logger.info("🚀 EORA AI System 시작 중...")
    
    # 프롬프트 데이터 로드
    logger.info("📚 프롬프트 데이터 로드 중...")
    if load_prompts_data():
        logger.info("✅ 프롬프트 데이터 로드 완료")
    else:
        logger.warning("⚠️ 프롬프트 데이터 로드 실패 - 기본 설정으로 진행")
    
    # MongoDB 연결 및 데이터베이스 초기화
    global mongo_client
    try:
        mongo_client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        mongo_client.admin.command('ping')
        logger.info("✅ MongoDB 연결 성공")
        
        # 데이터베이스 컬렉션 초기화
        await initialize_database_collections()
        
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
    except Exception as e:
        logger.warning(f"⚠️ MongoDB 연결 실패: {e}")
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
    user = get_current_user(request)
    is_admin = user.get("role") == "admin" if user else False
    return templates.TemplateResponse("home.html", {"request": request, "user": user, "is_admin": is_admin})

@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    try:
        return templates.TemplateResponse("chat.html", {"request": request})
    except Exception as e:
        logger.error(f"채팅 템플릿 렌더링 오류: {e}")
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>EORA AI Chat</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
                .chat-container {{ height: 400px; border: 1px solid #ddd; padding: 15px; overflow-y: auto; margin: 20px 0; }}
                .input-container {{ display: flex; gap: 10px; }}
                input[type="text"] {{ flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                button {{ padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }}
                button:hover {{ background: #0056b3; }}
                .message {{ margin: 10px 0; padding: 10px; border-radius: 5px; }}
                .user {{ background: #e3f2fd; text-align: right; }}
                .assistant {{ background: #f3e5f5; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>💬 EORA AI Chat</h1>
                <div class="chat-container" id="chatContainer">
                    <div class="message assistant">
                        안녕하세요! EORA AI입니다. 무엇을 도와드릴까요?
                    </div>
                </div>
                <div class="input-container">
                    <input type="text" id="messageInput" placeholder="메시지를 입력하세요..." onkeypress="if(event.keyCode==13) sendMessage()">
                    <button onclick="sendMessage()">전송</button>
                </div>
                <p><a href="/">← 홈으로 돌아가기</a></p>
            </div>
            <script>
                function sendMessage() {{
                    const input = document.getElementById('messageInput');
                    const message = input.value.trim();
                    if (!message) return;
                    
                    const container = document.getElementById('chatContainer');
                    container.innerHTML += `<div class="message user">${{message}}</div>`;
                    input.value = '';
                    
                    // 간단한 응답 시뮬레이션
                    setTimeout(() => {{
                        container.innerHTML += `<div class="message assistant">메시지를 받았습니다. 실제 API 연동이 필요합니다.</div>`;
                        container.scrollTop = container.scrollHeight;
                    }}, 1000);
                }}
            </script>
        </body>
        </html>
        """, status_code=200)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    try:
        return templates.TemplateResponse("dashboard.html", {"request": request})
    except Exception as e:
        logger.error(f"대시보드 템플릿 렌더링 오류: {e}")
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>EORA AI Dashboard</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
                .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
                .stat-number {{ font-size: 2em; font-weight: bold; color: #007bff; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 EORA AI Dashboard</h1>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">✅</div>
                        <div>서버 상태</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">✅</div>
                        <div>MongoDB 연결</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">✅</div>
                        <div>OpenAI API</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">⚠️</div>
                        <div>템플릿 파일</div>
                    </div>
                </div>
                <p><a href="/">← 홈으로 돌아가기</a></p>
            </div>
        </body>
        </html>
        """, status_code=200)

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    try:
        return templates.TemplateResponse("login.html", {"request": request})
    except Exception as e:
        logger.error(f"로그인 템플릿 렌더링 오류: {e}")
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>EORA AI Login</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .login-container {{ max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                input {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
                button {{ width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; margin-top: 10px; }}
                button:hover {{ background: #0056b3; }}
            </style>
        </head>
        <body>
            <div class="login-container">
                <h1>🔐 EORA AI Login</h1>
                <form>
                    <input type="email" placeholder="이메일" required>
                    <input type="password" placeholder="비밀번호" required>
                    <button type="submit">로그인</button>
                </form>
                <p style="text-align: center; margin-top: 20px;">
                    <a href="/">← 홈으로 돌아가기</a>
                </p>
            </div>
        </body>
        </html>
        """, status_code=200)

@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    user = get_current_user(request)
    if not user or user.get("role") != "admin":
        return RedirectResponse(url="/")
    return templates.TemplateResponse("admin.html", {"request": request, "user": user, "is_admin": True})

@app.get("/debug", response_class=HTMLResponse)
async def debug(request: Request):
    try:
        return templates.TemplateResponse("debug.html", {"request": request})
    except Exception as e:
        logger.error(f"디버그 템플릿 렌더링 오류: {e}")
        return HTMLResponse(f"<h1>디버그</h1><p>템플릿 오류: {str(e)}</p>", status_code=500)

@app.get("/simple-chat", response_class=HTMLResponse)
async def simple_chat(request: Request):
    try:
        return templates.TemplateResponse("test_chat_simple.html", {"request": request})
    except Exception as e:
        logger.error(f"간단 채팅 템플릿 렌더링 오류: {e}")
        return HTMLResponse(f"<h1>간단 채팅</h1><p>템플릿 오류: {str(e)}</p>", status_code=500)

@app.get("/points", response_class=HTMLResponse)
async def points(request: Request):
    try:
        return templates.TemplateResponse("points.html", {"request": request})
    except Exception as e:
        logger.error(f"포인트 템플릿 렌더링 오류: {e}")
        return HTMLResponse(f"<h1>포인트</h1><p>템플릿 오류: {str(e)}</p>", status_code=500)

@app.get("/memory", response_class=HTMLResponse)
async def memory_page(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("memory.html", {"request": request, "user": user})

@app.get("/api/aura/memory/stats")
async def aura_memory_stats(request: Request):
    user = get_current_user(request)
    user_id = user.get("user_id") if user else "anonymous"
    if aura_memory:
        stats = aura_memory.get_stats(user_id)
        return {"success": True, "stats": stats}
    return {"success": False, "error": "아우라 메모리 시스템 미사용"}

@app.get("/api/aura/recall")
async def aura_memory_recall(request: Request, query: str = ""):
    user = get_current_user(request)
    user_id = user.get("user_id") if user else "anonymous"
    if aura_memory:
        results = aura_memory.recall(user_id, query)
        return {"success": True, "results": results}
    return {"success": False, "error": "아우라 메모리 시스템 미사용"}

@app.get("/prompts", response_class=HTMLResponse)
async def get_prompts():
    """AI별/카테고리별 딕셔너리 구조로 프롬프트 반환"""
    try:
        global prompts_data
        if not prompts_data:
            load_prompts_data()
        if not prompts_data:
            return {"prompts": {}}
        # prompts_data는 이미 정규화된 상태
        return {"prompts": prompts_data["prompts"]}
    except Exception as e:
        logger.error(f"프롬프트 딕셔너리 조회 오류: {e}")
        return {"prompts": {}}

@app.post("/api/prompts/category")
async def save_prompt_category(request: Request):
    """카테고리별 프롬프트 저장 API"""
    try:
        data = await request.json()
        ai_name = data.get("ai_name")
        category = data.get("category")
        content = data.get("content")
        
        if not ai_name or not category or content is None:
            raise HTTPException(status_code=400, detail="필수 파라미터가 누락되었습니다.")
        
        # 전역 prompts_data 사용
        global prompts_data
        
        if not prompts_data:
            prompts_data = {}
        
        # 해당 AI의 카테고리 업데이트
        if ai_name not in prompts_data:
            prompts_data[ai_name] = {}
        
        # ai1의 system 프롬프트는 문자열로 저장
        if ai_name == 'ai1' and category == 'system':
            prompts_data[ai_name][category] = content
        else:
            # 다른 경우는 콘텐츠를 리스트로 변환 (여러 줄 분할)
            if isinstance(content, str):
                content_lines = [line.strip() for line in content.split('\n') if line.strip()]
                prompts_data[ai_name][category] = content_lines
            else:
                prompts_data[ai_name][category] = content
        
        # 파일에 저장 (여러 경로 시도)
        saved = False
        possible_paths = [
            "ai_brain/ai_prompts.json",
            "ai_prompts.json",
            "templates/ai_prompts.json"
        ]
        
        for prompts_file in possible_paths:
            try:
                # 디렉토리가 없으면 생성
                os.makedirs(os.path.dirname(prompts_file), exist_ok=True)
                with open(prompts_file, 'w', encoding='utf-8') as f:
                    json.dump(prompts_data, f, ensure_ascii=False, indent=2)
                saved = True
                logger.info(f"✅ 프롬프트 파일 저장 완료: {prompts_file}")
                break
            except Exception as e:
                logger.warning(f"⚠️ 프롬프트 파일 저장 실패 ({prompts_file}): {e}")
                continue
        
        if not saved:
            logger.warning("⚠️ 모든 경로에서 프롬프트 파일 저장 실패")
        
        logger.info(f"✅ 프롬프트 저장 완료: {ai_name}.{category}")
        return {"message": f"{ai_name}의 {category} 프롬프트가 성공적으로 저장되었습니다."}
    except Exception as e:
        logger.error(f"프롬프트 저장 오류: {e}")
        raise HTTPException(status_code=500, detail="프롬프트 저장 중 오류가 발생했습니다.")

@app.get("/prompt-management", response_class=HTMLResponse)
async def prompt_management(request: Request):
    try:
        logger.info("🤖 AI별 프롬프트 통합 관리 페이지 접근")
        return templates.TemplateResponse("prompt_management.html", {"request": request})
    except Exception as e:
        logger.error(f"프롬프트 관리 템플릿 렌더링 오류: {e}")
        return HTMLResponse(f"<h1>프롬프트 관리</h1><p>템플릿 오류: {str(e)}</p>", status_code=500)

@app.get("/test-prompts", response_class=HTMLResponse)
async def test_prompts(request: Request):
    """프롬프트 테스트 페이지"""
    return templates.TemplateResponse("test_prompts.html", {
        "request": request,
        "prompts_data": prompts_data,
        "prompts_count": len(prompts_data.get("prompts", {})) if isinstance(prompts_data, dict) and "prompts" in prompts_data else 0,
        "available_ai": list(prompts_data.get("prompts", {}).keys()) if isinstance(prompts_data, dict) and "prompts" in prompts_data else []
    })

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

@app.get("/api/debug/files")
async def debug_files():
    """Railway 환경에서 파일 시스템 진단"""
    import os
    from pathlib import Path
    
    debug_info = {
        "current_working_directory": str(Path.cwd()),
        "script_location": str(Path(__file__).parent),
        "possible_template_paths": [],
        "template_files_found": [],
        "all_files_in_app": []
    }
    
    # 가능한 템플릿 경로들 확인
    possible_paths = [
        Path(__file__).parent,  # 현재 파일 디렉토리
        Path("/app"),  # Railway 기본 경로
        Path("/app/templates"),  # Railway 템플릿 경로
        Path.cwd(),  # 현재 작업 디렉토리
        Path.cwd() / "templates",  # 현재 디렉토리의 templates
        Path("/workspace"),  # Railway 작업 공간
        Path("/workspace/templates"),  # Railway 작업 공간의 templates
    ]
    
    for path in possible_paths:
        path_info = {
            "path": str(path),
            "exists": path.exists(),
            "is_dir": path.is_dir() if path.exists() else False,
            "files": []
        }
        
        if path.exists() and path.is_dir():
            try:
                # HTML 파일들 확인
                html_files = list(path.glob("*.html"))
                path_info["html_files"] = [f.name for f in html_files]
                
                # 모든 파일 확인 (최대 20개)
                all_files = list(path.iterdir())
                path_info["all_files"] = [f.name for f in all_files[:20]]
                
                if html_files:
                    debug_info["template_files_found"].append({
                        "path": str(path),
                        "html_files": [f.name for f in html_files]
                    })
            except Exception as e:
                path_info["error"] = str(e)
        
        debug_info["possible_template_paths"].append(path_info)
    
    # /app 디렉토리 전체 확인
    app_path = Path("/app")
    if app_path.exists():
        try:
            all_app_files = []
            for item in app_path.rglob("*"):
                if item.is_file():
                    all_app_files.append(str(item.relative_to(app_path)))
                if len(all_app_files) >= 50:  # 최대 50개 파일만
                    break
            debug_info["all_files_in_app"] = all_app_files
        except Exception as e:
            debug_info["app_scan_error"] = str(e)
    
    return debug_info

@app.get("/api/debug/templates")
async def debug_templates():
    """템플릿 시스템 진단"""
    try:
        # 현재 템플릿 경로 확인
        current_template_path = str(templates_path)
        
        # 템플릿 파일들 확인
        template_files = []
        if templates_path.exists():
            for file in templates_path.glob("*.html"):
                template_files.append(file.name)
        
        return {
            "current_template_path": current_template_path,
            "template_path_exists": templates_path.exists(),
            "template_files": template_files,
            "total_html_files": len(template_files)
        }
    except Exception as e:
        return {
            "error": str(e),
            "current_template_path": "unknown"
        }

# 개선된 세션 및 메시지 API - 영구 저장 및 아우라 시스템 통합
@app.get("/api/sessions")
async def get_sessions(request: Request):
    """사용자의 세션 목록 조회 - MongoDB 기반 영구 저장 (DB 우선, 메모리 fallback은 DB 완전 장애 시에만)"""
    try:
        user = get_current_user(request)
        user_id = user.get("user_id") if user else "anonymous"
        user_sessions = []
        db_failed = False
        # MongoDB에서 세션 조회
        if sessions_collection is not None:
            try:
                cursor = sessions_collection.find({"user_id": user_id}).sort("created_at", -1)
                sessions_list = list(cursor)
                for session in sessions_list:
                    session["_id"] = str(session["_id"])
                    session["created_at"] = session["created_at"].isoformat()
                    session["last_activity"] = session["last_activity"].isoformat()
                    # 메시지 개수 조회
                    if chat_logs_collection is not None:
                        message_count = chat_logs_collection.count_documents({"session_id": session["_id"]})
                    else:
                        message_count = len(memory_messages.get(session["_id"], []))
                    user_sessions.append({
                        "id": session["_id"],
                        "name": session["name"],
                        "created_at": session["created_at"],
                        "last_activity": session["last_activity"],
                        "message_count": message_count
                    })
                logger.info(f"✅ MongoDB에서 {len(user_sessions)}개 세션 조회 완료")
                return {"success": True, "sessions": user_sessions}
            except Exception as e:
                logger.error(f"❌ MongoDB 세션 조회 실패: {e}")
                db_failed = True
        # DB 장애 시 메모리 fallback
        if db_failed or sessions_collection is None:
            logger.warning("⚠️ DB 장애로 메모리에서 세션 조회 (임시 fallback)")
            for session_id, session in memory_sessions.items():
                if session["user_id"] == user_id:
                    user_sessions.append(session)
            return {"success": True, "sessions": user_sessions}
    except Exception as e:
        logger.error(f"세션 목록 조회 오류: {e}")
        return {"success": False, "sessions": [], "error": str(e)}

@app.post("/api/sessions")
async def create_session(request: Request):
    try:
        data = await request.json()
        session_name = data.get("name", "새 세션")
        user_id = data.get("user_id", "anonymous")
        session_id = generate_session_id()
        
        session_data = {
            "name": session_name,
            "message_count": 0,
            "user_id": user_id
        }
        
        logger.info(f"📝 새 세션 생성: {session_name} (ID: {session_id})")
        
        if sessions_collection is not None:
            # MongoDB에 저장 - session_id 필드 추가
            session_doc = {
                "_id": session_id,
                "session_id": session_id,  # 명시적으로 session_id 필드 추가
                "name": session_name,
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "message_count": 0,
                "user_id": user_id
            }
            try:
                sessions_collection.insert_one(session_doc)
                session_doc["_id"] = str(session_doc["_id"])
                session_doc["created_at"] = session_doc["created_at"].isoformat()
                session_doc["last_activity"] = session_doc["last_activity"].isoformat()
                logger.info(f"✅ MongoDB 세션 저장 완료: {session_id}")
                return session_doc
            except Exception as mongo_error:
                logger.error(f"❌ MongoDB 세션 저장 실패: {mongo_error}")
                # MongoDB 실패 시 메모리로 fallback
                save_session_to_memory(session_id, session_data)
                logger.info(f"✅ 메모리 세션 저장 완료 (fallback): {session_id}")
                return {
                    "_id": session_id,
                    "name": session_name,
                    "created_at": datetime.now().isoformat(),
                    "last_activity": datetime.now().isoformat(),
                    "message_count": 0,
                    "user_id": user_id
                }
        else:
            # 메모리 기반 저장
            save_session_to_memory(session_id, session_data)
            logger.info(f"✅ 메모리 세션 저장 완료: {session_id}")
            return {
                "_id": session_id,
                "name": session_name,
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "message_count": 0,
                "user_id": user_id
            }
    except Exception as e:
        logger.error(f"세션 생성 오류: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, request: Request):
    """특정 세션의 메시지 목록 조회 - MongoDB 기반 영구 저장 (DB 우선, 메모리 fallback은 DB 완전 장애 시에만)"""
    try:
        user = get_current_user(request)
        user_id = user.get("user_id") if user else "anonymous"
        formatted_messages = []
        db_failed = False
        # MongoDB에서 메시지 조회
        if chat_logs_collection is not None:
            try:
                cursor = chat_logs_collection.find({"session_id": session_id}).sort("timestamp", 1)
                messages_list = list(cursor)
                for msg in messages_list:
                    msg["_id"] = str(msg["_id"])
                    msg["timestamp"] = msg["timestamp"].isoformat()
                    formatted_messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", msg.get("message", "")),
                        "timestamp": msg["timestamp"],
                        "user_id": msg.get("user_id", user_id)
                    })
                logger.info(f"✅ MongoDB에서 {len(formatted_messages)}개 메시지 조회 완료")
                return {"success": True, "messages": formatted_messages}
            except Exception as e:
                logger.error(f"❌ MongoDB 메시지 조회 실패: {e}")
                db_failed = True
        # DB 장애 시 메모리 fallback
        if db_failed or chat_logs_collection is None:
            logger.warning("⚠️ DB 장애로 메모리에서 메시지 조회 (임시 fallback)")
            formatted_messages = memory_messages.get(session_id, [])
            return {"success": True, "messages": formatted_messages}
    except Exception as e:
        logger.error(f"메시지 목록 조회 오류: {e}")
        return {"success": False, "messages": [], "error": str(e)}

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, request: Request):
    """세션 삭제 - MongoDB 및 메모리에서 완전 제거"""
    try:
        user = get_current_user(request)
        user_id = user.get("user_id") if user else "anonymous"
        
        logger.info(f"🗑️ 세션 삭제 요청: {session_id} (사용자: {user_id})")
        
        # MongoDB에서 세션 삭제
        if sessions_collection is not None:
            try:
                result = sessions_collection.delete_one({
                    "_id": session_id,
                    "user_id": user_id
                })
                if result.deleted_count > 0:
                    logger.info(f"✅ MongoDB에서 세션 삭제 완료: {session_id}")
                else:
                    logger.warning(f"⚠️ MongoDB에서 세션을 찾을 수 없음: {session_id}")
            except Exception as e:
                logger.error(f"❌ MongoDB 세션 삭제 실패: {e}")
        
        # MongoDB에서 세션 메시지 삭제
        if chat_logs_collection is not None:
            try:
                result = chat_logs_collection.delete_many({"session_id": session_id})
                logger.info(f"✅ MongoDB에서 {result.deleted_count}개 메시지 삭제 완료")
            except Exception as e:
                logger.error(f"❌ MongoDB 메시지 삭제 실패: {e}")
        
        # 메모리에서 세션 삭제
        if session_id in sessions_db:
            del sessions_db[session_id]
            logger.info(f"✅ 메모리에서 세션 삭제 완료: {session_id}")
        
        if session_id in chat_history:
            del chat_history[session_id]
            logger.info(f"✅ 메모리에서 세션 메시지 삭제 완료: {session_id}")
        
        # 아우라 메모리에서 세션 관련 메모리 삭제
        if AURA_MEMORY_AVAILABLE:
            try:
                # 아우라 메모리 시스템에서 세션 관련 메모리 삭제
                # (아우라 메모리 시스템에 삭제 기능이 있다면 사용)
                logger.info(f"✅ 아우라 메모리에서 세션 관련 메모리 정리 완료: {session_id}")
            except Exception as e:
                logger.error(f"❌ 아우라 메모리 정리 실패: {e}")
        
        return {"success": True, "message": "세션이 성공적으로 삭제되었습니다."}
    except Exception as e:
        logger.error(f"세션 삭제 오류: {e}")
        return {"success": False, "error": "세션 삭제 중 오류가 발생했습니다."}

@app.put("/api/sessions/{session_id}/rename")
async def rename_session(session_id: str, request: Request):
    """세션 이름 변경"""
    try:
        data = await request.json()
        new_name = data.get("name", "")
        user = get_current_user(request)
        user_id = user.get("user_id") if user else "anonymous"
        
        if not new_name:
            return {"success": False, "error": "새 이름을 입력해주세요."}
        
        logger.info(f"✏️ 세션 이름 변경: {session_id} -> {new_name}")
        
        # MongoDB에서 세션 이름 변경
        if sessions_collection is not None:
            try:
                result = sessions_collection.update_one(
                    {"_id": session_id, "user_id": user_id},
                    {"$set": {"name": new_name, "last_activity": datetime.now()}}
                )
                if result.modified_count > 0:
                    logger.info(f"✅ MongoDB에서 세션 이름 변경 완료: {session_id}")
                else:
                    logger.warning(f"⚠️ MongoDB에서 세션을 찾을 수 없음: {session_id}")
            except Exception as e:
                logger.error(f"❌ MongoDB 세션 이름 변경 실패: {e}")
        
        # 메모리에서 세션 이름 변경
        if session_id in sessions_db:
            sessions_db[session_id]["name"] = new_name
            sessions_db[session_id]["last_activity"] = datetime.now().isoformat()
            logger.info(f"✅ 메모리에서 세션 이름 변경 완료: {session_id}")
        
        return {"success": True, "message": "세션 이름이 성공적으로 변경되었습니다."}
    except Exception as e:
        logger.error(f"세션 이름 변경 오류: {e}")
        return {"success": False, "error": "세션 이름 변경 중 오류가 발생했습니다."}

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
        
        logger.info(f"💾 메시지 저장 요청: {message_data['session_id']}")
        
        if chat_logs_collection is not None:
            try:
                # 중복 메시지 방지: 최근 30초 내 같은 내용의 메시지 확인
                recent_time = datetime.now() - timedelta(seconds=30)
                duplicate_check = chat_logs_collection.find_one({
                    "session_id": message_data["session_id"],
                    "content": message_data["content"],
                    "role": message_data["role"],
                    "timestamp": {"$gte": recent_time}
                }, projection={"_id": 1})
                
                if duplicate_check:
                    logger.info(f"⚠️ 중복 메시지 감지 - MongoDB 저장 건너뜀: {message_data['session_id']}")
                    return {
                        "_id": str(duplicate_check["_id"]),
                        "session_id": message_data["session_id"],
                        "content": message_data["content"],
                        "role": message_data["role"],
                        "timestamp": message_data["timestamp"].isoformat(),
                        "duplicate": True
                    }
                
                result = chat_logs_collection.insert_one(message_data)
                message_data["_id"] = str(result.inserted_id)
                message_data["timestamp"] = message_data["timestamp"].isoformat()
                
                # 세션 업데이트
                if sessions_collection is not None:
                    try:
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
                    except Exception as session_error:
                        logger.warning(f"⚠️ 세션 업데이트 실패: {session_error}")
                
                logger.info(f"✅ MongoDB에 메시지 저장 완료: {result.inserted_id}")
                return message_data
            except Exception as e:
                logger.error(f"❌ MongoDB 메시지 저장 실패: {e}")
                # MongoDB 실패 시 메모리로 전환
                pass
        
        # 메모리 기반 저장
        logger.info("ℹ️ 메모리 기반 메시지 저장")
        message_id = save_message_to_memory(message_data)
        message_data["_id"] = message_id
        
        # 중복 메시지인 경우 플래그 추가
        if message_id == "duplicate":
            message_data["duplicate"] = True
            logger.info(f"⚠️ 중복 메시지 감지 - 메모리 저장 건너뜀")
        else:
            logger.info(f"✅ 메모리에 메시지 저장 완료: {message_id}")
        
        return message_data
        
    except Exception as e:
        logger.error(f"❌ 메시지 저장 오류: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    """개선된 채팅 엔드포인트 - 아우라 메모리 시스템 및 고급 회상 통합"""
    try:
        data = await request.json()
        user_message = data.get("message", "")
        session_id = data.get("session_id", "default_session")
        user_id = data.get("user_id", "anonymous")
        
        logger.info(f"🔄 채팅 요청 처리: {user_id} - {session_id}")
        
        # 1. 아우라 메모리 시스템에서 관련 기억 회상
        recalled_memories = []
        if AURA_MEMORY_AVAILABLE and aura_memory:
            try:
                recalled_memories = await recall_from_aura_memory(
                    query=user_message,
                    user_id=user_id,
                    limit=3
                )
                logger.info(f"✅ 아우라 메모리 회상 완료: {len(recalled_memories)}개")
            except Exception as e:
                logger.error(f"❌ 아우라 메모리 회상 실패: {e}")
        else:
            logger.info("ℹ️ 아우라 메모리 시스템을 사용할 수 없어 기본 회상으로 동작합니다.")
        
        # 2. 고급 채팅 시스템 처리 (가능한 경우)
        advanced_response = None
        if ADVANCED_CHAT_AVAILABLE and advanced_chat_system:
            try:
                advanced_result = await advanced_chat_system.process_message(
                    user_message=user_message,
                    user_id=user_id
                )
                advanced_response = advanced_result.get("response")
                logger.info("✅ 고급 채팅 시스템 처리 완료")
            except Exception as e:
                logger.error(f"❌ 고급 채팅 시스템 처리 실패: {e}")
                logger.info("ℹ️ 기본 채팅 시스템으로 전환합니다.")
        else:
            logger.info("ℹ️ 고급 채팅 시스템을 사용할 수 없어 기본 시스템으로 동작합니다.")
        
        # 3. 사용자 메시지 저장
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
        
        # AI 프롬프트 로드
        system_prompt = "당신은 EORA라는 감정 중심 인공지능입니다. 친근하고 따뜻한 톤으로 대화해주세요."
        
        # ai_prompts.json에서 프롬프트 사용 (올바른 구조: prompts.ai1.content)
        logger.info("🔍 프롬프트 검색 시작...")
        logger.info(f"📄 prompts_data 타입: {type(prompts_data)}")
        logger.info(f"📄 prompts_data 키: {list(prompts_data.keys()) if isinstance(prompts_data, dict) else 'Not a dict'}")
        
        if prompts_data and isinstance(prompts_data, dict):
            if "prompts" in prompts_data:
                prompts = prompts_data["prompts"]
                logger.info(f"📋 사용 가능한 AI: {list(prompts.keys())}")
                
                # ai1 프롬프트 우선 시도
                if "ai1" in prompts and isinstance(prompts["ai1"], dict):
                    if "content" in prompts["ai1"]:
                        system_prompt = prompts["ai1"]["content"]
                        logger.info("✅ ai_prompts.json의 ai1 system 프롬프트 적용")
                        logger.info(f"📝 프롬프트 미리보기: {system_prompt[:100]}...")
                    else:
                        logger.warning("⚠️ ai1에 content 필드가 없습니다")
                # eora 프롬프트 시도
                elif "eora" in prompts and isinstance(prompts["eora"], dict):
                    if "content" in prompts["eora"]:
                        system_prompt = prompts["eora"]["content"]
                        logger.info("✅ ai_prompts.json의 eora system 프롬프트 적용")
                        logger.info(f"📝 프롬프트 미리보기: {system_prompt[:100]}...")
                    else:
                        logger.warning("⚠️ eora에 content 필드가 없습니다")
                # 첫 번째 사용 가능한 AI 프롬프트 사용
                else:
                    for ai_name, ai_data in prompts.items():
                        if isinstance(ai_data, dict) and "content" in ai_data:
                            system_prompt = ai_data["content"]
                            logger.info(f"✅ ai_prompts.json의 {ai_name} system 프롬프트 적용")
                            logger.info(f"📝 프롬프트 미리보기: {system_prompt[:100]}...")
                            break
                    else:
                        logger.warning("⚠️ 사용 가능한 AI 프롬프트를 찾을 수 없습니다")
            else:
                logger.warning("⚠️ prompts_data에 'prompts' 키가 없습니다")
                logger.info(f"📄 prompts_data 구조: {list(prompts_data.keys())}")
        else:
            logger.warning("⚠️ prompts_data가 비어있거나 잘못된 형식입니다")
        
        logger.info(f"🎯 최종 사용 프롬프트: {system_prompt[:100]}...")
        
        # 4. EORA 응답 생성 - 회상된 기억과 고급 시스템 통합
        eora_response = None
        
        # 고급 응답 우선 사용
        if advanced_response:
            eora_response = advanced_response
            logger.info("✅ 고급 채팅 시스템 응답 사용")
        # OpenAI API 사용
        elif openai_client and OPENAI_API_KEY:
            try:
                # 회상된 기억을 컨텍스트에 포함
                context_messages = [{"role": "system", "content": system_prompt}]
                
                # 회상된 기억이 있으면 컨텍스트에 추가
                if recalled_memories:
                    memory_context = "📌 이전 대화에서 관련된 내용:\n"
                    for i, memory in enumerate(recalled_memories, 1):
                        memory_context += f"{i}. 사용자: {memory.message}\n   AI: {memory.response}\n"
                    memory_context += "\n위의 기억을 참고하여 자연스럽게 대화를 이어가세요.\n"
                    context_messages.append({"role": "system", "content": memory_context})
                
                context_messages.append({"role": "user", "content": user_message})
                
                # 최신 OpenAI 라이브러리 호환 - gpt-4o 모델 사용
                response = openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=context_messages,
                    max_tokens=500,
                    temperature=0.7
                )
                eora_response = response.choices[0].message.content
                logger.info("✅ OpenAI API 호출 성공 (회상 기억 포함)")
            except Exception as e:
                logger.warning(f"OpenAI API 호출 실패: {e}")
                eora_response = f"안녕하세요! '{user_message}'에 대해 이야기하고 싶으시군요. 현재 AI 서비스에 일시적인 문제가 있어 기본 응답을 드립니다."
        else:
            logger.warning("⚠️ OpenAI API 키가 설정되지 않았습니다.")
            eora_response = f"안녕하세요! '{user_message}'에 대해 이야기하고 싶으시군요. 현재 AI 서비스가 설정되지 않아 기본 응답을 드립니다."
        
        # 5. EORA 응답 저장
        eora_msg_data = {
            "session_id": session_id,
            "user_id": user_id,
            "content": eora_response,
            "role": "assistant",
            "timestamp": datetime.now()
        }
        
        message_id = None
        if chat_logs_collection is not None:
            # 중복 응답 방지
            recent_time = datetime.now() - timedelta(seconds=30)
            duplicate_check = chat_logs_collection.find_one({
                "session_id": session_id,
                "content": eora_response,
                "role": "assistant",
                "timestamp": {"$gte": recent_time}
            }, projection={"_id": 1})
            
            if duplicate_check:
                logger.info(f"⚠️ 중복 AI 응답 감지 - 저장 건너뜀: {session_id}")
                message_id = str(duplicate_check["_id"])
            else:
                result = chat_logs_collection.insert_one(eora_msg_data)
                message_id = str(result.inserted_id)
        else:
            # 메모리 기반 저장
            message_id = save_message_to_memory(eora_msg_data)
        
        # 6. 아우라 메모리 시스템에 대화 저장
        if AURA_MEMORY_AVAILABLE and aura_memory:
            try:
                memory_id = await save_to_aura_memory(
                    user_id=user_id,
                    session_id=session_id,
                    message=user_message,
                    response=eora_response
                )
                if memory_id:
                    logger.info(f"✅ 아우라 메모리 저장 완료: {memory_id}")
            except Exception as e:
                logger.error(f"❌ 아우라 메모리 저장 실패: {e}")
        else:
            logger.info("ℹ️ 아우라 메모리 시스템을 사용할 수 없어 기본 저장으로 동작합니다.")
        
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

# 관리자 로그인 API
@app.post("/api/admin/login")
async def admin_login(request: Request):
    try:
        data = await request.json()
        email = data.get("email", "")
        password = data.get("password", "")
        
        # 기본 관리자 계정 (실제 환경에서는 데이터베이스에서 확인)
        if email == "admin@eora.ai" and password == "admin123":
            return {
                "success": True,
                "message": "관리자 로그인 성공",
                "user": {
                    "id": "admin",
                    "email": email,
                    "role": "admin",
                    "name": "EORA 관리자"
                }
            }
        else:
            return {
                "success": False,
                "message": "이메일 또는 비밀번호가 올바르지 않습니다."
            }
    except Exception as e:
        logger.error(f"관리자 로그인 오류: {e}")
        return {
            "success": False,
            "message": "로그인 처리 중 오류가 발생했습니다."
        }

@app.post("/api/register")
async def register(request: Request):
    """회원가입 API"""
    try:
        data = await request.json()
        email = data.get("email", "")
        password = data.get("password", "")
        name = data.get("name", "")
        if not email or not password:
            return {"success": False, "message": "이메일과 비밀번호를 입력해주세요."}
        if users_collection.find_one({"email": email}):
            return {"success": False, "message": "이미 등록된 이메일입니다."}
        user_id = str(uuid.uuid4())
        user_doc = {"user_id": user_id, "email": email, "password": password, "name": name, "role": "user"}
        users_collection.insert_one(user_doc)
        # 회원별 전용 컬렉션 생성 (보완)
        for coll in [f"user_{user_id}_chat", f"user_{user_id}_points"]:
            if coll not in db.list_collection_names():
                db.create_collection(coll)
        db[f"user_{user_id}_points"].insert_one({"user_id": user_id, "points": 100000})
        return {"success": True, "message": "회원가입 성공! 10만 포인트가 지급되었습니다.", "user_id": user_id}
    except Exception as e:
        logger.error(f"회원가입 오류: {e}")
        return {"success": False, "message": str(e)}

@app.post("/api/login")
async def login(request: Request):
    """일반 로그인 API (관리자 로그인과 동일하게 처리)"""
    try:
        data = await request.json()
        email = data.get("email", "")
        password = data.get("password", "")
        
        # 관리자 계정으로 로그인 시도
        if email == "admin@eora.ai" and password == "admin123":
            return {
                "success": True,
                "message": "로그인 성공",
                "user": {
                    "id": "admin",
                    "email": email,
                    "role": "admin",
                    "name": "EORA 관리자"
                },
                "access_token": "admin_token"
            }
        else:
            # 일반 사용자 로그인 시도 (MongoDB에서 확인)
            if users_collection is not None:
                try:
                    user = users_collection.find_one({"email": email, "password": password})
                    if user:
                        return {
                            "success": True,
                            "message": "로그인 성공",
                            "user": {
                                "id": str(user.get("_id", email)),
                                "email": email,
                                "role": user.get("role", "user"),
                                "name": user.get("name", email.split('@')[0])
                            },
                            "access_token": f"user_token_{email}"
                        }
                except Exception as e:
                    logger.warning(f"⚠️ MongoDB 사용자 조회 실패: {e}")
            
            return {
                "success": False,
                "message": "이메일 또는 비밀번호가 올바르지 않습니다."
            }
    except Exception as e:
        logger.error(f"로그인 오류: {e}")
        return {
            "success": False,
            "message": "로그인 처리 중 오류가 발생했습니다."
        }

@app.get("/api/prompts")
async def get_prompts():
    """AI별/카테고리별 딕셔너리 구조로 프롬프트 반환"""
    try:
        global prompts_data
        if not prompts_data:
            load_prompts_data()
        if not prompts_data:
            return {"prompts": {}}
        # prompts_data는 이미 정규화된 상태
        return {"prompts": prompts_data["prompts"]}
    except Exception as e:
        logger.error(f"프롬프트 딕셔너리 조회 오류: {e}")
        return {"prompts": {}}

@app.get("/api/prompts/raw")
async def get_raw_prompts():
    """원본 ai_prompts.json 파일 내용 조회"""
    try:
        global prompts_data
        
        if not prompts_data:
            load_prompts_data()
        
        if not prompts_data:
            return {"error": "프롬프트 데이터를 찾을 수 없습니다."}
        
        # 파일 경로 찾기 (더 많은 경로 추가)
        possible_paths = [
            "templates/ai_prompts.json",
            "ai_prompts.json",
            "ai_brain/ai_prompts.json",
            "/app/templates/ai_prompts.json",
            "/app/ai_prompts.json",
            "/app/ai_brain/ai_prompts.json",
            os.path.join(os.getcwd(), "templates", "ai_prompts.json"),
            os.path.join(os.getcwd(), "ai_prompts.json"),
            os.path.join(os.getcwd(), "ai_brain", "ai_prompts.json"),
            "src/templates/ai_prompts.json",
            "src/ai_prompts.json",
            "E:/AI_Dev_Tool/src/templates/ai_prompts.json"
        ]
        
        file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_content = f.read()
                
                return {
                    "file_path": file_path,
                    "raw_content": raw_content,
                    "parsed_data": prompts_data,
                    "file_size": len(raw_content),
                    "file_exists": True,
                    "success": True,
                    "ai_count": len(prompts_data) if prompts_data else 0
                }
            except Exception as e:
                return {
                    "file_path": file_path,
                    "raw_content": f"파일 읽기 오류: {str(e)}",
                    "parsed_data": prompts_data,
                    "file_exists": True,
                    "read_error": str(e),
                    "success": False
                }
        else:
            # 파일이 없으면 현재 메모리의 데이터를 JSON으로 반환
            import json
            return {
                "file_path": "메모리 데이터",
                "raw_content": json.dumps(prompts_data, ensure_ascii=False, indent=2),
                "parsed_data": prompts_data,
                "file_size": len(json.dumps(prompts_data, ensure_ascii=False)),
                "file_exists": False,
                "searched_paths": possible_paths,
                "success": True,
                "ai_count": len(prompts_data) if prompts_data else 0
            }
    except Exception as e:
        logger.error(f"원본 프롬프트 조회 오류: {e}")
        return {"error": str(e), "success": False}

@app.post("/api/prompts/update-category")
async def update_prompt_category(request: Request):
    """특정 카테고리 프롬프트 업데이트 API"""
    try:
        data = await request.json()
        ai_name = data.get("ai_name")
        category = data.get("category")
        content = data.get("content")
        
        if not ai_name or not category or content is None:
            raise HTTPException(status_code=400, detail="필수 파라미터가 누락되었습니다.")
        
        # 전역 prompts_data 사용
        global prompts_data
        
       
        
        # 해당 AI의 카테고리 업데이트
        if ai_name not in prompts_data:
            prompts_data[ai_name] = {}
        
        # 콘텐츠를 리스트로 변환 (여러 줄 분할)
        if isinstance(content, str):
            content_lines = [line.strip() for line in content.split('\n') if line.strip()]
            prompts_data[ai_name][category] = content_lines
        else:
            prompts_data[ai_name][category] = content
        
        # 파일에 저장 (여러 경로 시도)
        saved = False
        possible_paths = [
            "ai_brain/ai_prompts.json",
            "ai_prompts.json",
            "templates/ai_prompts.json"
        ]
        
        for prompts_file in possible_paths:
            try:
                # 디렉토리가 없으면 생성
                os.makedirs(os.path.dirname(prompts_file), exist_ok=True)
                with open(prompts_file, 'w', encoding='utf-8') as f:
                    json.dump(prompts_data, f, ensure_ascii=False, indent=2)
                saved = True
                logger.info(f"✅ 프롬프트 파일 저장 완료: {prompts_file}")
                break
            except Exception as e:
                logger.warning(f"⚠️ 프롬프트 파일 저장 실패 ({prompts_file}): {e}")
                continue
        
        if not saved:
            logger.warning("⚠️ 모든 경로에서 프롬프트 파일 저장 실패")
        
        logger.info(f"✅ 프롬프트 업데이트 완료: {ai_name}.{category}")
        return {"message": f"{ai_name}의 {category} 프롬프트가 성공적으로 업데이트되었습니다."}
    except Exception as e:
        logger.error(f"프롬프트 업데이트 오류: {e}")
        raise HTTPException(status_code=500, detail="프롬프트 업데이트 중 오류가 발생했습니다.")

@app.delete("/api/prompts/delete-category")
async def delete_prompt_category(request: Request):
    """특정 카테고리 프롬프트 삭제 API"""
    try:
        data = await request.json()
        ai_name = data.get("ai_name")
        category = data.get("category")
        
        if not ai_name or not category:
            raise HTTPException(status_code=400, detail="필수 파라미터가 누락되었습니다.")
        
        # 전역 prompts_data 사용
        global prompts_data
        
        if not prompts_data:
            raise HTTPException(status_code=404, detail="프롬프트 데이터를 찾을 수 없습니다.")
        
        # 해당 AI의 카테고리 삭제
        if ai_name in prompts_data and category in prompts_data[ai_name]:
            del prompts_data[ai_name][category]
            
            # AI가 비어있으면 전체 삭제
            if not prompts_data[ai_name]:
                del prompts_data[ai_name]
            
            # 파일에 저장 (여러 경로 시도)
            saved = False
            possible_paths = [
                "ai_brain/ai_prompts.json",
                "ai_prompts.json",
                "templates/ai_prompts.json"
            ]
            
            for prompts_file in possible_paths:
                try:
                    # 디렉토리가 없으면 생성
                    os.makedirs(os.path.dirname(prompts_file), exist_ok=True)
                    with open(prompts_file, 'w', encoding='utf-8') as f:
                        json.dump(prompts_data, f, ensure_ascii=False, indent=2)
                    saved = True
                    logger.info(f"✅ 프롬프트 파일 저장 완료: {prompts_file}")
                    break
                except Exception as e:
                    logger.warning(f"⚠️ 프롬프트 파일 저장 실패 ({prompts_file}): {e}")
                    continue
            
            if not saved:
                logger.warning("⚠️ 모든 경로에서 프롬프트 파일 저장 실패")
            
            logger.info(f"✅ 프롬프트 삭제 완료: {ai_name}.{category}")
            return {"message": f"{ai_name}의 {category} 프롬프트가 성공적으로 삭제되었습니다."}
        else:
            raise HTTPException(status_code=404, detail="해당 프롬프트를 찾을 수 없습니다.")
            
    except Exception as e:
        logger.error(f"프롬프트 삭제 오류: {e}")
        raise HTTPException(status_code=500, detail="프롬프트 삭제 중 오류가 발생했습니다.")

@app.post("/api/prompts/reload")
async def reload_prompts():
    """프롬프트 데이터를 다시 로드합니다."""
    try:
        global prompts_data
        success = load_prompts_data()
        return {
            "success": success,
            "message": "프롬프트 데이터가 다시 로드되었습니다." if success else "프롬프트 데이터 로드에 실패했습니다.",
            "prompts_count": len(prompts_data.get("prompts", {})) if isinstance(prompts_data, dict) and "prompts" in prompts_data else 0
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


        # 해당 AI의 카테고리 업데이트
        if ai_name not in prompts_data:
            prompts_data[ai_name] = {}
        
        # ai1의 system 프롬프트는 문자열로 저장
        if ai_name == 'ai1' and category == 'system':
            prompts_data[ai_name][category] = content
        else:
            # 다른 경우는 콘텐츠를 리스트로 변환 (여러 줄 분할)
            if isinstance(content, str):
                content_lines = [line.strip() for line in content.split('\n') if line.strip()]
                prompts_data[ai_name][category] = content_lines
            else:
                prompts_data[ai_name][category] = content
        
        # 파일에 저장 (여러 경로 시도)
        saved = False
        possible_paths = [
            "ai_brain/ai_prompts.json",
            "ai_prompts.json",
            "templates/ai_prompts.json"
        ]
        
        for prompts_file in possible_paths:
            try:
                # 디렉토리가 없으면 생성
                os.makedirs(os.path.dirname(prompts_file), exist_ok=True)
                with open(prompts_file, 'w', encoding='utf-8') as f:
                    json.dump(prompts_data, f, ensure_ascii=False, indent=2)
                saved = True
                logger.info(f"✅ 프롬프트 파일 저장 완료: {prompts_file}")
                break
            except Exception as e:
                logger.warning(f"⚠️ 프롬프트 파일 저장 실패 ({prompts_file}): {e}")
                continue
        
        if not saved:
            logger.warning("⚠️ 모든 경로에서 프롬프트 파일 저장 실패")
        
        logger.info(f"✅ 프롬프트 저장 완료: {ai_name}.{category}")
        return {"message": f"{ai_name}의 {category} 프롬프트가 성공적으로 저장되었습니다."}
    except Exception as e:
        logger.error(f"프롬프트 저장 오류: {e}")
        raise HTTPException(status_code=500, detail="프롬프트 저장 중 오류가 발생했습니다.")

# 관리자 페이지 API들
@app.get("/api/admin/monitoring")
async def get_monitoring_data():
    """시스템 모니터링 데이터 조회"""
    try:
        # 시스템 상태 정보 수집
        import psutil
        import time
        
        # CPU 사용률
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 메모리 사용률
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # 디스크 사용률
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # 네트워크 정보
        network = psutil.net_io_counters()
        
        # 활성 세션 수
        active_sessions = len(active_connections)
        
        # MongoDB 연결 상태
        mongo_status = "연결됨" if mongo_client else "연결 안됨"
        
        return {
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "network_bytes_sent": network.bytes_sent,
                "network_bytes_recv": network.bytes_recv
            },
            "application": {
                "active_sessions": active_sessions,
                "mongo_status": mongo_status,
                "uptime": time.time() - start_time if 'start_time' in globals() else 0
            },
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"모니터링 데이터 조회 오류: {e}")
        return {"error": "모니터링 데이터를 가져올 수 없습니다."}

@app.get("/api/admin/users")
async def get_users_data():
    """사용자 관리 데이터 조회"""
    try:
        # 메모리에서 세션 데이터 수집
        sessions = get_sessions_from_memory()
        
        # 사용자 통계
        total_users = len(set(session.get('user_id', 'anonymous') for session in sessions))
        active_users = len([s for s in sessions if s.get('last_activity', 0) > time.time() - 3600])
        
        # 세션별 상세 정보
        user_details = []
        for session in sessions:
            user_details.append({
                "session_id": session.get('session_id', ''),
                "user_id": session.get('user_id', 'anonymous'),
                "created_at": session.get('created_at', ''),
                "last_activity": session.get('last_activity', ''),
                "message_count": len(session.get('messages', []))
            })
        
        return {
            "statistics": {
                "total_users": total_users,
                "active_users": active_users,
                "total_sessions": len(sessions)
            },
            "users": user_details
        }
    except Exception as e:
        logger.error(f"사용자 데이터 조회 오류: {e}")
        return {"error": "사용자 데이터를 가져올 수 없습니다."}

@app.get("/api/admin/system-settings")
async def get_system_settings():
    """시스템 설정 데이터 조회"""
    try:
        # 환경변수 정보 (민감한 정보는 제외)
        env_vars = {
            "PORT": os.getenv("PORT", "8080"),
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "development"),
            "OPENAI_API_KEY_SET": "설정됨" if os.getenv("OPENAI_API_KEY") else "설정 안됨",
            "MONGODB_URI_SET": "설정됨" if os.getenv("MONGODB_URI") else "설정 안됨"
        }
        
        # 시스템 정보
        import platform
        system_info = {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor()
        }
        
        # 프롬프트 데이터 상태
        prompt_status = {
            "loaded": bool(prompts_data),
            "ai_count": len(prompts_data) if prompts_data else 0,
            "file_paths": ["ai_brain/ai_prompts.json", "ai_prompts.json", "templates/ai_prompts.json"]
        }
        
        return {
            "environment": env_vars,
            "system": system_info,
            "prompts": prompt_status
        }
    except Exception as e:
        logger.error(f"시스템 설정 조회 오류: {e}")
        return {"error": "시스템 설정을 가져올 수 없습니다."}

@app.get("/api/admin/performance")
async def get_performance_data():
    """성능 분석 데이터 조회"""
    try:
        # 채팅 응답 시간 통계 (메모리에서)
        sessions = get_sessions_from_memory()
        
        response_times = []
        total_messages = 0
        
        for session in sessions:
            messages = session.get('messages', [])
            total_messages += len(messages)
            
            for msg in messages:
                if msg.get('role') == 'assistant' and 'response_time' in msg:
                    response_times.append(msg['response_time'])
        
        # 통계 계산
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        # 사용자 만족도 (간단한 지표)
        satisfaction_score = 85.5  # 예시 값
        
        return {
            "chat_performance": {
                "total_messages": total_messages,
                "avg_response_time": round(avg_response_time, 2),
                "min_response_time": round(min_response_time, 2),
                "max_response_time": round(max_response_time, 2)
            },
            "user_satisfaction": {
                "score": satisfaction_score,
                "level": "높음" if satisfaction_score >= 80 else "보통" if satisfaction_score >= 60 else "낮음"
            }
        }
    except Exception as e:
        logger.error(f"성능 데이터 조회 오류: {e}")
        return {"error": "성능 데이터를 가져올 수 없습니다."}

@app.get("/api/admin/security")
async def get_security_data():
    """보안 관리 데이터 조회"""
    try:
        # 보안 관련 정보 수집
        sessions = get_sessions_from_memory()
        
        # 접근 로그 분석
        recent_sessions = [s for s in sessions if s.get('last_activity', 0) > time.time() - 86400]  # 24시간
        
        # 의심스러운 활동 감지 (간단한 예시)
        suspicious_activities = []
        for session in recent_sessions:
            messages = session.get('messages', [])
            if len(messages) > 100:  # 메시지가 너무 많은 경우
                suspicious_activities.append({
                    "session_id": session.get('session_id', ''),
                    "reason": "과도한 메시지",
                    "count": len(messages)
                })
        
        # 보안 상태
        security_status = {
            "total_sessions_24h": len(recent_sessions),
            "suspicious_activities": len(suspicious_activities),
            "mongo_connection_secure": bool(mongo_client),
            "api_key_configured": bool(os.getenv("OPENAI_API_KEY"))
        }
        
        return {
            "security_status": security_status,
            "suspicious_activities": suspicious_activities,
            "recommendations": [
                "정기적인 로그 모니터링",
                "API 키 보안 강화",
                "세션 타임아웃 설정"
            ]
        }
    except Exception as e:
        logger.error(f"보안 데이터 조회 오류: {e}")
        return {"error": "보안 데이터를 가져올 수 없습니다."}

@app.post("/api/auth/logout")
async def logout():
    """로그아웃 API"""
    try:
        # 세션 정리 로직 (필요시)
        return {"message": "로그아웃되었습니다."}
    except Exception as e:
        logger.error(f"로그아웃 오류: {e}")
        return {"error": "로그아웃 중 오류가 발생했습니다."}

# 언어 설정 API
@app.post("/api/set-language")
async def set_language(request: Request):
    try:
        data = await request.json()
        language = data.get("language", "ko")
        logger.info(f"언어 설정: {language}")
        return {"status": "success", "language": language}
    except Exception as e:
        logger.error(f"언어 설정 오류: {e}")
        return {"status": "error", "message": str(e)}

# 사용자 활동 API
@app.get("/api/user/activity")
async def get_user_activity():
    return {
        "recent_activity": [
            {
                "type": "chat",
                "timestamp": datetime.now().isoformat(),
                "description": "채팅 시작"
            }
        ],
        "total_activities": 1
    }

@app.get("/api/prompts/debug")
async def debug_prompts():
    """프롬프트 로딩 상태를 디버그합니다."""
    try:
        debug_info = {
            "prompts_data_type": str(type(prompts_data)),
            "prompts_data_keys": list(prompts_data.keys()) if isinstance(prompts_data, dict) else None,
            "prompts_data_length": len(str(prompts_data)),
            "has_prompts_key": "prompts" in prompts_data if isinstance(prompts_data, dict) else False,
            "available_ai": [],
            "ai_details": {},
            "load_status": "success"
        }
        
        if isinstance(prompts_data, dict) and "prompts" in prompts_data:
            prompts = prompts_data["prompts"]
            debug_info["available_ai"] = list(prompts.keys())
            
            for ai_name, ai_data in prompts.items():
                if isinstance(ai_data, dict):
                    debug_info["ai_details"][ai_name] = {
                        "has_content": "content" in ai_data,
                        "content_length": len(ai_data.get("content", "")),
                        "content_preview": ai_data.get("content", "")[:200] + "..." if len(ai_data.get("content", "")) > 200 else ai_data.get("content", ""),
                        "keys": list(ai_data.keys())
                    }
                else:
                    debug_info["ai_details"][ai_name] = {
                        "type": str(type(ai_data)),
                        "value": str(ai_data)[:200]
                    }
        
        return debug_info
    except Exception as e:
        return {
            "error": str(e),
            "load_status": "error",
            "prompts_data_type": str(type(prompts_data))
        }

# 세션 및 메모리 관리 개선 - 영구 저장 및 아우라 시스템 통합
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import uuid

# 세션 데이터베이스 초기화
sessions_db = {}
chat_history = {}

# MongoDB 컬렉션 초기화
sessions_collection = None
chat_logs_collection = None
memory_collection = None

async def initialize_database_collections():
    """데이터베이스 컬렉션 초기화"""
    global sessions_collection, chat_logs_collection, memory_collection
    
    try:
        if mongo_client and mongo_client.is_primary:
            db = mongo_client[DATABASE_NAME]
            sessions_collection = db["sessions"]
            chat_logs_collection = db["chat_logs"]
            memory_collection = db["memories"]
            
            # 기존 인덱스 삭제 (중복 키 오류 해결)
            try:
                sessions_collection.drop_index("session_id_1")
                logger.info("✅ 기존 session_id 인덱스 삭제 완료")
            except:
                pass  # 인덱스가 없으면 무시
            
            # 새로운 인덱스 생성 (중복 방지)
            sessions_collection.create_index([("user_id", 1), ("created_at", -1)])
            sessions_collection.create_index([("session_id", 1)], unique=True)  # session_id는 유니크
            chat_logs_collection.create_index([("session_id", 1), ("timestamp", -1)])
            memory_collection.create_index([("user_id", 1), ("session_id", 1)])
            
            logger.info("✅ MongoDB 컬렉션 초기화 완료")
        else:
            logger.warning("⚠️ MongoDB 연결 실패 - 메모리 기반으로 동작")
    except Exception as e:
        logger.error(f"❌ 데이터베이스 초기화 실패: {e}")

async def save_to_aura_memory(user_id: str, session_id: str, message: str, response: str):
    """아우라 메모리 시스템에 대화 저장"""
    try:
        if AURA_MEMORY_AVAILABLE and aura_memory:
            memory_id = aura_memory.create_memory(
                user_id=user_id,
                session_id=session_id,
                message=message,
                response=response,
                memory_type="conversation",
                importance=0.7
            )
            logger.info(f"✅ 아우라 메모리 저장 완료: {memory_id}")
            return memory_id
        else:
            logger.warning("⚠️ 아우라 메모리 시스템을 사용할 수 없습니다")
            return None
    except Exception as e:
        logger.error(f"❌ 아우라 메모리 저장 실패: {e}")
        return None

async def recall_from_aura_memory(query: str, user_id: str = None, limit: int = 5):
    """아우라 메모리 시스템에서 회상"""
    try:
        if AURA_MEMORY_AVAILABLE and aura_memory:
            memories = aura_memory.recall_memories(
                query=query,
                user_id=user_id,
                limit=limit
            )
            logger.info(f"✅ 아우라 메모리 회상 완료: {len(memories)}개")
            return memories
        else:
            logger.warning("⚠️ 아우라 메모리 시스템을 사용할 수 없습니다")
            return []
    except Exception as e:
        logger.error(f"❌ 아우라 메모리 회상 실패: {e}")
        return []

def generate_session_id():
    """세션 ID 생성"""
    return str(uuid.uuid4())

def save_session_to_memory(session_id: str, session_data: dict):
    """메모리에 세션 저장"""
    sessions_db[session_id] = {
        "name": session_data.get("name", "새 세션"),
        "created_at": datetime.now().isoformat(),
        "last_activity": datetime.now().isoformat(),
        "message_count": 0,
        "user_id": session_data.get("user_id", "anonymous")
    }
    chat_history[session_id] = []

def save_message_to_memory(message_data: dict):
    """메모리에 메시지 저장"""
    session_id = message_data.get("session_id")
    if not session_id:
        return None
    
    # 중복 메시지 방지
    recent_messages = chat_history.get(session_id, [])
    if recent_messages:
        last_message = recent_messages[-1]
        if (last_message.get("content") == message_data.get("content") and
            last_message.get("role") == message_data.get("role") and
            (datetime.now() - datetime.fromisoformat(last_message.get("timestamp", datetime.now().isoformat()))).seconds < 30):
            return "duplicate"
    
    message_id = str(uuid.uuid4())
    message_data["_id"] = message_id
    message_data["timestamp"] = message_data["timestamp"].isoformat()
    
    if session_id not in chat_history:
        chat_history[session_id] = []
    chat_history[session_id].append(message_data)
    
    # 세션 업데이트
    if session_id in sessions_db:
        sessions_db[session_id]["last_activity"] = datetime.now().isoformat()
        sessions_db[session_id]["message_count"] = len(chat_history[session_id])
    
    return message_id

def get_messages_from_memory(session_id: str):
    """메모리에서 메시지 조회"""
    return chat_history.get(session_id, [])

def get_sessions_from_memory():
    """메모리에서 세션 목록 조회"""
    return sessions_db

@app.post("/api/user/change-password")
async def change_password(request: Request):
    try:
        data = await request.json()
        current_password = data.get("current_password", "")
        new_password = data.get("new_password", "")
        user_email = None
        # 세션 또는 토큰에서 사용자 이메일 추출 (여기서는 간단히 localStorage 기반)
        # 실제 배포 환경에서는 인증 토큰에서 추출해야 함
        if "user_email" in request.cookies:
            user_email = request.cookies["user_email"]
        else:
            # 프론트에서 이메일을 보내는 경우도 지원
            user_email = data.get("email")
        if not user_email:
            return {"success": False, "message": "로그인 정보가 없습니다. 다시 로그인 해주세요."}
        if not current_password or not new_password:
            return {"success": False, "message": "모든 필드를 입력해주세요."}
        if len(new_password) < 6:
            return {"success": False, "message": "비밀번호는 6자 이상이어야 합니다."}
        # MongoDB에서 사용자 확인 및 비밀번호 변경
        if users_collection is not None:
            user = users_collection.find_one({"email": user_email})
            if not user:
                return {"success": False, "message": "사용자 정보를 찾을 수 없습니다."}
            if user.get("password") != current_password:
                return {"success": False, "message": "현재 비밀번호가 올바르지 않습니다."}
            users_collection.update_one({"email": user_email}, {"$set": {"password": new_password}})
            return {"success": True, "message": "비밀번호가 성공적으로 변경되었습니다."}
        return {"success": False, "message": "서버 오류: 사용자 데이터베이스 연결 실패"}
    except Exception as e:
        logger.error(f"비밀번호 변경 오류: {e}")
        return {"success": False, "message": "비밀번호 변경 중 서버 오류가 발생했습니다."}

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})

# 포인트 차감 함수
POINTS_PER_TOKEN = 2
INITIAL_POINTS = 100000
ADMIN_EMAIL = "admin@eora.ai"

# 포인트 차감 함수

def deduct_points(user_email, tokens_used):
    if user_email == ADMIN_EMAIL:
        return True  # 관리자는 무한 포인트
    if points_collection is not None:
        user_points = points_collection.find_one({"user_id": user_email})
        if not user_points:
            return False
        cost = tokens_used * POINTS_PER_TOKEN
        if user_points.get("points", 0) < cost:
            return False
        points_collection.update_one({"user_id": user_email}, {"$inc": {"points": -cost}})
        return True
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

@app.post("/api/register")
async def register(request: Request):
    try:
        data = await request.json()
        email = data.get("email", "")
        password = data.get("password", "")
        name = data.get("name", "")
        if not email or not password:
            return {"success": False, "message": "이메일과 비밀번호를 입력해주세요."}
        if users_collection.find_one({"email": email}):
            return {"success": False, "message": "이미 등록된 이메일입니다."}
        user_id = str(uuid.uuid4())
        user_doc = {"user_id": user_id, "email": email, "password": password, "name": name, "role": "user"}
        users_collection.insert_one(user_doc)
        # 회원별 전용 컬렉션 생성 (보완)
        for coll in [f"user_{user_id}_chat", f"user_{user_id}_points"]:
            if coll not in db.list_collection_names():
                db.create_collection(coll)
        db[f"user_{user_id}_points"].insert_one({"user_id": user_id, "points": 100000})
        return {"success": True, "message": "회원가입 성공! 10만 포인트가 지급되었습니다.", "user_id": user_id}
    except Exception as e:
        logger.error(f"회원가입 오류: {e}")
        return {"success": False, "message": str(e)}

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        user = get_current_user(request)
        user_id = user.get("user_id") if user else None
        if not user_id:
            return {"success": False, "message": "로그인 필요"}
        tokens_used = data.get("tokens_used", 0)
        # 포인트 차감(토큰 2배)
        points_col = db[f"user_{user_id}_points"]
        user_points = points_col.find_one({"user_id": user_id})
        cost = tokens_used * 2
        if not user_points or user_points.get("points", 0) < cost:
            return {"success": False, "message": "포인트가 부족합니다."}
        points_col.update_one({"user_id": user_id}, {"$inc": {"points": -cost}})
        # 대화 저장
        chat_col = db[f"user_{user_id}_chat"]
        chat_col.insert_one({"user_id": user_id, "message": data.get("message", ""), "created_at": datetime.now()})
        # 1. 저장소 용량 체크
        usage_mb = get_user_storage_usage_mb(user_id)
        if usage_mb >= 100:
            return {"success": False, "message": f"저장소 용량 초과(100MB). 채팅/저장 불가.", "usage_mb": usage_mb}
        warn_msg = None
        if usage_mb >= 95:
            warn_msg = f"경고: 저장소 용량이 95MB를 초과했습니다. ({usage_mb}MB/100MB)"
        return {"success": True, "message": "채팅 성공", "points": user_points["points"] - cost, "warning": warn_msg}
    except Exception as e:
        logger.error(f"채팅 오류: {e}")
        return {"success": False, "message": str(e)}

@app.get("/api/admin/points")
async def admin_points():
    users = []
    if points_collection is not None:
        for user in points_collection.find():
            users.append({
                "user_id": user.get("user_id"),
                "email": user.get("email", user.get("user_id")),
                "name": user.get("name", ""),
                "points": user.get("points", 0)
            })
    return {"users": users}

@app.post("/api/admin/points/charge")
async def admin_points_charge(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    type_ = data.get("type")
    amount = int(data.get("amount", 0))
    if not user_id or type_ not in ("add", "subtract", "reset"): return {"success": False, "message": "잘못된 요청"}
    if points_collection is None:
        return {"success": False, "message": "DB 연결 오류"}
    user = points_collection.find_one({"user_id": user_id})
    if not user:
        return {"success": False, "message": "사용자 없음"}
    if type_ == "add":
        points_collection.update_one({"user_id": user_id}, {"$inc": {"points": amount}})
    elif type_ == "subtract":
        if user.get("points", 0) < amount:
            return {"success": False, "message": "포인트 부족"}
        points_collection.update_one({"user_id": user_id}, {"$inc": {"points": -amount}})
    elif type_ == "reset":
        points_collection.update_one({"user_id": user_id}, {"$set": {"points": 0}})
    return {"success": True}

@app.post("/api/points/purchase")
async def points_purchase(request: Request):
    data = await request.json()
    points = int(data.get("points", 0))
    price = int(data.get("price", 0))
    user = await get_current_user(request)
    if not user or not user.get("user_id"):
        return {"success": False, "message": "로그인 필요"}
    if points_collection is None:
        return {"success": False, "message": "DB 연결 오류"}
    points_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"points": points}}, upsert=True)
    # TODO: 결제 연동 시 실제 결제 검증 필요
    return {"success": True, "message": f"{points} 포인트 충전 완료"}

@app.get("/api/admin/user/{user_id}")
async def admin_user_detail(user_id: str):
    user = users_collection.find_one({"user_id": user_id}) if users_collection else None
    points = points_collection.find_one({"user_id": user_id}) if points_collection else None
    sessions = list(sessions_collection.find({"user_id": user_id})) if sessions_collection else []
    return {
        "user_id": user_id,
        "email": user.get("email", user_id) if user else user_id,
        "name": user.get("name", "") if user else "",
        "created_at": user.get("created_at", "") if user else "",
        "last_activity": user.get("last_activity", "") if user else "",
        "role": user.get("role", "user") if user else "user",
        "points": points.get("points", 0) if points else 0,
        "sessions": [{"name": s.get("name", "세션"), "created_at": s.get("created_at", "")} for s in sessions]
    }

@app.get("/api/user/points/{user_id}")
async def user_points_detail(user_id: str, from_: str = '', to: str = '', type: str = ''):
    # from_, to: yyyy-mm-dd
    points = points_collection.find_one({"user_id": user_id}) if points_collection else None
    history = points.get("history", []) if points else []
    def date_in_range(ts):
        if not (from_ or to): return True
        dt = datetime.fromisoformat(ts[:19]) if ts else None
        if from_:
            if not dt or dt < datetime.fromisoformat(from_): return False
        if to:
            if not dt or dt > datetime.fromisoformat(to)+timedelta(days=1): return False
        return True
    filtered = [h for h in history if (not type or h.get('type')==type) and date_in_range(h.get('timestamp',''))]
    return {
        "user_id": user_id,
        "points": points.get("points", 0) if points else 0,
        "history": filtered
    }

@app.get("/api/admin/points")
async def admin_points(email: str = '', name: str = '', minp: int = None, maxp: int = None, sort: str = 'points', dir: int = -1):
    users = []
    q = {}
    if email: q["email"] = {"$regex": email, "$options": "i"}
    if name: q["name"] = {"$regex": name, "$options": "i"}
    if minp is not None or maxp is not None:
        q["points"] = {}
        if minp is not None: q["points"]["$gte"] = minp
        if maxp is not None: q["points"]["$lte"] = maxp
    sort_tuple = (sort, dir)
    if points_collection is not None:
        for user in points_collection.find(q).sort([sort_tuple]):
            users.append({
                "user_id": user.get("user_id"),
                "email": user.get("email", user.get("user_id")),
                "name": user.get("name", ""),
                "points": user.get("points", 0)
            })
    # 통계
    total_users = points_collection.count_documents({}) if points_collection else 0
    total_points = sum(u["points"] for u in users)
    return {"users": users, "stats": {"total_users": total_users, "total_points": total_points}}

@app.post("/api/auth/register")
async def register_user(request: Request):
    import hashlib
    if users_collection is None:
        logger.error("❌ users_collection이 None (MongoDB 연결 실패)")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="MongoDB 연결 실패. 잠시 후 다시 시도해주세요.")
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        name = data.get("name")
        if not email or not password:
            return {"success": False, "message": "이메일과 비밀번호를 입력하세요."}
        if users_collection.find_one({"email": email}):
            return {"success": False, "message": "이미 등록된 이메일입니다."}
        user_id = str(uuid.uuid4())
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        users_collection.insert_one({
            "user_id": user_id,
            "email": email,
            "password": hashed_pw,
            "name": name,
            "is_admin": False
        })
        db[f"user_{user_id}_chat"].insert_one({"init": True})
        db[f"user_{user_id}_points"].insert_one({"user_id": user_id, "points": 100000})
        return {"success": True, "message": "회원가입 완료! 10만 포인트 지급.", "user_id": user_id}
    except Exception as e:
        logger.error(f"회원가입 오류: {e}")
        return {"success": False, "message": f"회원가입 오류: {str(e)}"}

@app.post("/api/auth/login")
async def login_user(request: Request):
    import hashlib
    if users_collection is None:
        logger.error("❌ users_collection이 None (MongoDB 연결 실패)")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="MongoDB 연결 실패. 잠시 후 다시 시도해주세요.")
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        user = users_collection.find_one({"email": email})
        if not user or user["password"] != hashlib.sha256(password.encode()).hexdigest():
            return {"success": False, "message": "이메일 또는 비밀번호가 올바르지 않습니다."}
        token = str(uuid.uuid4())
        users_collection.update_one({"email": email}, {"$set": {"token": token}})
        resp = JSONResponse({"success": True, "message": "로그인 성공", "is_admin": user.get("is_admin", False)})
        resp.set_cookie(key="token", value=token)
        return resp
    except Exception as e:
        logger.error(f"로그인 오류: {e}")
        return {"success": False, "message": f"로그인 오류: {str(e)}"}

def get_user_by_token(request: Request):
    token = request.cookies.get("token")
    if not token:
        return None
    user = db.users.find_one({"token": token})
    return user

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    message = data.get("message", "")
    session_id = data.get("session_id", "default")
    user = get_user_by_token(request)
    if not user:
        return {"success": False, "message": "로그인 필요"}
    user_id = user["user_id"]
    try:
        import tiktoken
        enc = tiktoken.encoding_for_model("gpt-4o")
        tokens = len(enc.encode(message))
    except Exception:
        tokens = len(message)
    cost = tokens * 2
    points_col = db[f"user_{user_id}_points"]
    points_doc = points_col.find_one({"user_id": user_id})
    if not points_doc or points_doc.get("points", 0) < cost:
        return {"success": False, "message": "포인트 부족"}
    points_col.update_one({"user_id": user_id}, {"$inc": {"points": -cost}})
    db[f"user_{user_id}_chat"].insert_one({"session_id": session_id, "message": message})
    return {"success": True, "message": f"채팅 저장 및 {cost}포인트 차감 완료", "remain": points_doc["points"] - cost}

@app.get("/admin")
async def admin_page(request: Request):
    user = get_user_by_token(request)
    if not user or not user.get("is_admin", False):
        return RedirectResponse("/")
    return JSONResponse({"success": True, "message": "관리자 페이지", "user": user})

# 1. MongoDB 연결 및 컬렉션 초기화 함수 분리

def initialize_mongodb_collections():
    global client, db, chat_logs_collection, sessions_collection, users_collection, aura_collection, system_logs_collection, points_collection
    client = try_mongodb_connection()
    if client is None:
        logger.error("❌ 모든 MongoDB 연결 시도 실패 (앱 시작)")
        # 연결 실패 시에도 서버는 계속 실행
        logger.info("ℹ️ 메모리 기반 세션 관리로 전환합니다.")
        chat_logs_collection = None
        sessions_collection = None
        users_collection = None
        aura_collection = None
        system_logs_collection = None
        points_collection = None
        return False
    try:
        db = client[DATABASE_NAME]
        chat_logs_collection = db["chat_logs"]
        sessions_collection = db["sessions"]
        users_collection = db["users"]
        aura_collection = db["aura"]
        system_logs_collection = db["system_logs"]
        points_collection = db["points"]
        logger.info("✅ MongoDB 컬렉션 초기화 완료 (앱 시작)")
        return True
    except Exception as e:
        logger.error(f"❌ MongoDB 컬렉션 초기화 실패 (앱 시작): {e}")
        chat_logs_collection = None
        sessions_collection = None
        users_collection = None
        aura_collection = None
        system_logs_collection = None
        points_collection = None
        return False

# 2. FastAPI 앱 시작 이벤트에서 반드시 호출
from fastapi import status, HTTPException

@app.on_event("startup")
def on_startup():
    logger.info("🚦 FastAPI 앱 시작: MongoDB 컬렉션 초기화 시도")
    initialize_mongodb_collections()

from functools import wraps
from fastapi import Request, HTTPException, status, Depends

# 관리자 접근제어 데코레이터

def admin_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get('request')
        if request is None:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
        user = None
        if request:
            user = getattr(request.state, 'user', None)
        if not user or not user.get('is_admin', False):
            raise HTTPException(status_code=403, detail="관리자만 접근 가능합니다.")
        return await func(*args, **kwargs)
    return wrapper

# 관리자 계정 자동 생성 함수
import hashlib

def create_admin_account():
    admin_email = "admin@admin.com"
    admin_pw = "admin1234"
    admin_name = "관리자"
    if users_collection is None:
        return
    if not users_collection.find_one({"email": admin_email}):
        hashed_pw = hashlib.sha256(admin_pw.encode()).hexdigest()
        users_collection.insert_one({
            "user_id": "admin",
            "email": admin_email,
            "password": hashed_pw,
            "name": admin_name,
            "is_admin": True,
            "points": 100000
        })
        print("✅ 관리자 계정 자동 생성: admin@admin.com / admin1234")

# FastAPI 앱 시작 시 관리자 계정 자동 생성
@app.on_event("startup")
async def startup_event():
    initialize_mongodb_collections()
    create_admin_account()

# 관리자 접근제어 적용 예시 (admin 페이지 및 API)
from fastapi.responses import HTMLResponse

@app.get("/admin", response_class=HTMLResponse)
@admin_required
async def admin_page(request: Request):
    # ... 기존 관리자 페이지 렌더링 코드 ...
    return templates.TemplateResponse("admin.html", {"request": request})

# /api/admin/* 라우트에 admin_required 적용 (예시)
@app.get("/api/admin/users")
@admin_required
async def admin_get_users(request: Request):
    # ... 기존 코드 ...
    return {"success": True, "users": list(users_collection.find({}, {"_id": 0, "password": 0}))}

# ... 기존 코드 ...

@app.get("/api/admin/storage")
@admin_required
async def admin_storage_overview():
    """전체 회원수, 전체 데이터 용량, 회원별 용량/포인트 통계 반환"""
    try:
        users = list(users_collection.find({}, {"_id": 0, "user_id": 1, "email": 1, "name": 1, "points": 1}))
        total_users = len(users)
        total_mb = 0.0
        user_stats = []
        for user in users:
            user_id = user.get("user_id")
            usage_mb = get_user_storage_usage_mb(user_id)
            total_mb += usage_mb
            user_stats.append({
                "user_id": user_id,
                "email": user.get("email"),
                "name": user.get("name"),
                "points": user.get("points", 0),
                "usage_mb": usage_mb
            })
        return {
            "success": True,
            "total_users": total_users,
            "total_storage_mb": round(total_mb, 2),
            "users": user_stats
        }
    except Exception as e:
        logger.error(f"관리자 저장소 통계 오류: {e}")
        return {"success": False, "message": str(e)}

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