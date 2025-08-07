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
import jwt
import redis.asyncio as aioredis
from bson import ObjectId

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))  # .env 파일에서 환경변수 로드
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

# 아우라 통합 시스템 import
try:
    from aura_integration import get_aura_integration, AuraIntegration
    AURA_INTEGRATION_AVAILABLE = True
    print("✅ 아우라 통합 시스템 로드 성공")
except ImportError as e:
    AURA_INTEGRATION_AVAILABLE = False
    print(f"⚠️ 아우라 통합 시스템 로드 실패: {e}")

# 아우라 메모리 시스템 import (기존 호환성)
try:
    from aura_memory_system import aura_memory_system
    AURA_MEMORY_AVAILABLE = True
    print("✅ 아우라 메모리 시스템 로드 성공")
except ImportError as e:
    AURA_MEMORY_AVAILABLE = False
    print(f"⚠️ 아우라 메모리 시스템 로드 실패: {e}")

# 고급 대화 시스템 import 추가
try:
    from eora_advanced_chat_system import process_advanced_message, get_advanced_chat_system
    ADVANCED_CHAT_AVAILABLE = True
    print("✅ EORA 고급 대화 시스템 로드 완료")
except ImportError as e:
    ADVANCED_CHAT_AVAILABLE = False
    print(f"⚠️ EORA 고급 대화 시스템 로드 실패: {e}")
    print("기본 대화 시스템을 사용합니다.")

# 저장공간 관리 시스템 import
try:
    from storage_manager import get_storage_manager, StorageType
    STORAGE_MANAGER_AVAILABLE = True
    print("✅ 저장공간 관리 시스템 로드 완료")
except ImportError as e:
    STORAGE_MANAGER_AVAILABLE = False
    print(f"⚠️ 저장공간 관리 시스템 로드 실패: {e}")

# 아우라 시스템 초기화 함수
async def initialize_aura_system():
    """아우라 시스템 초기화"""
    try:
        if AURA_INTEGRATION_AVAILABLE:
            aura_integration = await get_aura_integration()
            await aura_integration.initialize()
            print("✅ 아우라 통합 시스템 초기화 완료")
            return aura_integration
        elif AURA_MEMORY_AVAILABLE:
            print("✅ 아우라 메모리 시스템 사용")
            return aura_memory_system
        else:
            print("⚠️ 아우라 시스템을 사용할 수 없습니다")
            return None
    except Exception as e:
        print(f"❌ 아우라 시스템 초기화 실패: {e}")
        return None

# 아우라 시스템 저장 함수
async def save_to_aura_system(user_id: str, message: str, response: str, session_id: str):
    """아우라 시스템에 대화 저장"""
    try:
        if AURA_INTEGRATION_AVAILABLE:
            aura_integration = await get_aura_integration()
            await aura_integration.save_memory(user_id, message, response, session_id)
            print(f"✅ 아우라 통합 시스템 저장 완료: {user_id}")
            return True
        elif AURA_MEMORY_AVAILABLE:
            memory_id = aura_memory_system.create_memory(user_id, session_id, message, response)
            print(f"✅ 아우라 메모리 시스템 저장 완료: {user_id} - {memory_id}")
            return True
        else:
            print("⚠️ 아우라 시스템을 사용할 수 없습니다")
            return False
    except Exception as e:
        print(f"❌ 아우라 시스템 저장 실패: {e}")
        return False

# 아우라 시스템 회상 함수
async def recall_from_aura_system(query: str, user_id: str = None, limit: int = 2):
    """아우라 시스템에서 회상 - 최적화된 고속 회상"""
    try:
        if AURA_INTEGRATION_AVAILABLE:
            aura_integration = await get_aura_integration()
            # 더 많은 메모리 조회하되 빠른 필터링
            memories = await aura_integration.recall_memories(query, user_id, limit * 3)
            
            # 빠른 품질 필터링 (점수 0.6 이상으로 완화)
            high_quality_memories = []
            for memory in memories:
                quality_score = 0
                if hasattr(memory, 'score') and memory.score:
                    quality_score = memory.score
                elif hasattr(memory, 'accuracy') and memory.accuracy:
                    quality_score = memory.accuracy
                elif isinstance(memory, dict):
                    quality_score = memory.get('score', 0) or memory.get('accuracy', 0)
                
                # 품질 기준 완화 (0.6 이상)
                if quality_score >= 0.6:
                    high_quality_memories.append(memory)
                    if len(high_quality_memories) >= limit:
                        break
            
            print(f"✅ 아우라 통합 시스템 회상 완료: {len(high_quality_memories)}개 고품질 메모리")
            return high_quality_memories
            
        elif AURA_MEMORY_AVAILABLE:
            memories = aura_memory_system.recall_memories(query, user_id, limit=limit * 3)
            
            # 빠른 품질 필터링 (점수 0.6 이상으로 완화)
            high_quality_memories = []
            for memory in memories:
                quality_score = 0
                if hasattr(memory, 'score') and memory.score:
                    quality_score = memory.score
                elif hasattr(memory, 'accuracy') and memory.accuracy:
                    quality_score = memory.accuracy
                elif isinstance(memory, dict):
                    quality_score = memory.get('score', 0) or memory.get('accuracy', 0)
                
                # 품질 기준 완화 (0.6 이상)
                if quality_score >= 0.6:
                    high_quality_memories.append(memory)
                    if len(high_quality_memories) >= limit:
                        break
            
            print(f"✅ 아우라 메모리 시스템 회상 완료: {len(high_quality_memories)}개 고품질 메모리")
            return high_quality_memories
        else:
            print("⚠️ 아우라 시스템을 사용할 수 없습니다")
            return []
    except Exception as e:
        print(f"❌ 아우라 시스템 회상 실패: {e}")
        return []

# DB 대화내용 불러오기 함수 - 최적화
async def load_conversation_history(session_id: str, user_id: str = None, limit: int = 20):
    """DB에서 대화 내용 불러오기 - 최적화된 버전"""
    try:
        if mongo_client and chat_logs_collection:
            # 최적화된 쿼리 (인덱스 활용)
            query = {"session_id": session_id}
            if user_id:
                query["user_id"] = user_id
            
            # 필요한 필드만 조회하여 메모리 사용량 최소화
            cursor = chat_logs_collection.find(
                query,
                {
                    "message": 1,
                    "response": 1,
                    "timestamp": 1,
                    "user_id": 1,
                    "_id": 0  # _id 제외로 메모리 절약
                }
            ).sort("timestamp", 1).limit(limit)
            
            # 리스트 컴프리헨션으로 빠른 변환
            conversations = [
                {
                    "message": doc.get("message", ""),
                    "response": doc.get("response", ""),
                    "timestamp": doc.get("timestamp", ""),
                    "user_id": doc.get("user_id", "")
                }
                for doc in cursor
            ]
            
            print(f"✅ 대화 내용 불러오기 완료: {session_id} - {len(conversations)}개")
            return conversations
        else:
            print("❌ MongoDB 연결 불가")
            return []
    except Exception as e:
        print(f"❌ 대화 내용 불러오기 실패: {e}")
        return []

# 사용자별 세션 목록 조회 함수 - 최적화
async def get_user_sessions(user_id: str, limit: int = 10):
    """사용자의 세션 목록 조회 - 최적화된 버전"""
    try:
        if mongo_client and chat_logs_collection:
            # 최적화된 집계 파이프라인
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": "$session_id",
                    "last_message": {"$last": "$message"},
                    "last_response": {"$last": "$response"},
                    "last_timestamp": {"$last": "$timestamp"},
                    "message_count": {"$sum": 1}
                }},
                {"$sort": {"last_timestamp": -1}},
                {"$limit": limit},
                {"$project": {
                    "session_id": "$_id",
                    "last_message": 1,
                    "last_response": 1,
                    "last_timestamp": 1,
                    "message_count": 1,
                    "_id": 0
                }}
            ]
            
            # 빠른 변환
            sessions = list(chat_logs_collection.aggregate(pipeline))
            
            print(f"✅ 사용자 세션 목록 조회 완료: {user_id} - {len(sessions)}개")
            return sessions
        else:
            print("❌ MongoDB 연결 불가")
            return []
    except Exception as e:
        print(f"❌ 사용자 세션 목록 조회 실패: {e}")
        return []

# 회상 메모리를 활용한 응답 개선 함수 - 최적화
async def enhance_response_with_memories(response: str, memories: list, current_message: str) -> str:
    """회상된 메모리를 활용하여 응답을 개선 - 최적화된 버전"""
    try:
        if not memories or not response:
            return response
        
        # 빠른 메모리 컨텍스트 생성 (최대 1개만 사용)
        memory_context = ""
        for memory in memories[:1]:  # 최대 1개 메모리만 사용
            if hasattr(memory, 'message') and hasattr(memory, 'response'):
                memory_context = f"이전 대화 - 사용자: {memory.message}, AI: {memory.response}"
                break
            elif isinstance(memory, dict):
                memory_context = f"이전 대화 - 사용자: {memory.get('message', '')}, AI: {memory.get('response', '')}"
                break
        
        # 메모리 컨텍스트가 없으면 원본 응답 반환
        if not memory_context:
            return response
        
        print(f"✅ 1개의 고품질 메모리 활용")
        
        # 간소화된 응답 개선 (API 호출 없이 직접 개선)
        if "이전 대화" in memory_context and len(memory_context) > 20:
            # 간단한 컨텍스트 추가
            enhanced_response = f"{response}\n\n(이전 대화를 참고하여 답변드렸습니다.)"
            return enhanced_response
        else:
            return response
            
    except Exception as e:
        print(f"⚠️ 응답 개선 실패: {e}")
        return response

# Redis 클라이언트 import
try:
    import redis
    REDIS_AVAILABLE = True
    print("✅ Redis 클라이언트 로드 완료")
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️ Redis 클라이언트 로드 실패")

# Redis 캐시 클라이언트 초기화
redis_cache = None
if REDIS_AVAILABLE:
    try:
        redis_cache = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)
        redis_cache.ping()
        print("✅ Redis 캐시 연결 성공")
    except Exception as e:
        print(f"⚠️ Redis 캐시 연결 실패: {e}")
        redis_cache = None

app = FastAPI(title="EORA AI System - Final", version="1.0.0")
print("[진단] FastAPI 앱 생성 직후 라우트:", app.routes)

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

# MongoDB 디버깅용 엔드포인트 추가
@app.get("/debug/mongodb")
async def debug_mongodb():
    """MongoDB 연결 상태 및 저장 로직 디버깅"""
    debug_info = {
        "mongo_available": MONGO_AVAILABLE,
        "mongo_client_status": mongo_client is not None,
        "collections_status": {
            "users_collection": users_collection is not None,
            "points_collection": points_collection is not None,
            "sessions_collection": sessions_collection is not None,
            "chat_logs_collection": chat_logs_collection is not None
        },
        "storage_manager_status": {
            "available": STORAGE_MANAGER_AVAILABLE,
            "instance": storage_manager_instance is not None
        },
        "aura_systems_status": {
            "memory_available": AURA_MEMORY_AVAILABLE,
            "integration_available": AURA_INTEGRATION_AVAILABLE
        },
        "environment_variables": {
            "mongo_public_url": bool(os.getenv("MONGO_PUBLIC_URL")),
            "mongo_url": bool(os.getenv("MONGO_URL")),
            "mongo_root_password": bool(os.getenv("MONGO_INITDB_ROOT_PASSWORD")),
            "mongo_root_username": bool(os.getenv("MONGO_INITDB_ROOT_USERNAME"))
        }
    }
    
    # MongoDB 연결 테스트
    if mongo_client:
        try:
            # ping 테스트
            mongo_client.admin.command('ping')
            debug_info["mongo_connection_test"] = "✅ 연결 성공"
            
            # 데이터베이스 목록 확인
            db_list = mongo_client.list_database_names()
            debug_info["databases"] = db_list
            
            # eora_ai 데이터베이스 확인
            if "eora_ai" in db_list:
                db = mongo_client.eora_ai
                collections = db.list_collection_names()
                debug_info["eora_ai_collections"] = collections
                
                # chat_logs 컬렉션 문서 수 확인
                if "chat_logs" in collections:
                    chat_count = db.chat_logs.count_documents({})
                    debug_info["chat_logs_count"] = chat_count
                    
                    # 최근 채팅 로그 샘플
                    recent_chats = list(db.chat_logs.find().sort("created_at", -1).limit(5))
                    debug_info["recent_chats"] = [
                        {
                            "user_id": chat.get("user_id"),
                            "session_id": chat.get("session_id"),
                            "timestamp": str(chat.get("timestamp")),
                            "message_preview": chat.get("message", "")[:50] + "..." if chat.get("message") else ""
                        }
                        for chat in recent_chats
                    ]
            else:
                debug_info["eora_ai_database"] = "❌ 데이터베이스 없음"
                
        except Exception as e:
            debug_info["mongo_connection_test"] = f"❌ 연결 실패: {str(e)}"
    else:
        debug_info["mongo_connection_test"] = "❌ 클라이언트 없음"
    
    return debug_info

# MongoDB 디버깅용 엔드포인트 추가
@app.get("/debug/mongodb")
async def debug_mongodb():
    """MongoDB 연결 상태 및 저장 로직 디버깅"""
    debug_info = {
        "mongo_available": MONGO_AVAILABLE,
        "mongo_client_status": mongo_client is not None,
        "collections_status": {
            "users_collection": users_collection is not None,
            "points_collection": points_collection is not None,
            "sessions_collection": sessions_collection is not None,
            "chat_logs_collection": chat_logs_collection is not None
        },
        "storage_manager_status": {
            "available": STORAGE_MANAGER_AVAILABLE,
            "instance": storage_manager_instance is not None
        },
        "aura_systems_status": {
            "memory_available": AURA_MEMORY_AVAILABLE,
            "integration_available": AURA_INTEGRATION_AVAILABLE
        },
        "environment_variables": {
            "mongo_public_url": bool(os.getenv("MONGO_PUBLIC_URL")),
            "mongo_url": bool(os.getenv("MONGO_URL")),
            "mongo_root_password": bool(os.getenv("MONGO_INITDB_ROOT_PASSWORD")),
            "mongo_root_username": bool(os.getenv("MONGO_INITDB_ROOT_USERNAME"))
        }
    }
    
    # MongoDB 연결 테스트
    if mongo_client:
        try:
            # ping 테스트
            mongo_client.admin.command('ping')
            debug_info["mongo_connection_test"] = "✅ 연결 성공"
            
            # 데이터베이스 목록 확인
            db_list = mongo_client.list_database_names()
            debug_info["databases"] = db_list
            
            # eora_ai 데이터베이스 확인
            if "eora_ai" in db_list:
                db = mongo_client.eora_ai
                collections = db.list_collection_names()
                debug_info["eora_ai_collections"] = collections
                
                # chat_logs 컬렉션 문서 수 확인
                if "chat_logs" in collections:
                    chat_count = db.chat_logs.count_documents({})
                    debug_info["chat_logs_count"] = chat_count
                    
                    # 최근 채팅 로그 샘플
                    recent_chats = list(db.chat_logs.find().sort("created_at", -1).limit(5))
                    debug_info["recent_chats"] = [
                        {
                            "user_id": chat.get("user_id"),
                            "session_id": chat.get("session_id"),
                            "timestamp": str(chat.get("timestamp")),
                            "message_preview": chat.get("message", "")[:50] + "..." if chat.get("message") else ""
                        }
                        for chat in recent_chats
                    ]
            else:
                debug_info["eora_ai_database"] = "❌ 데이터베이스 없음"
                
        except Exception as e:
            debug_info["mongo_connection_test"] = f"❌ 연결 실패: {str(e)}"
    else:
        debug_info["mongo_connection_test"] = "❌ 클라이언트 없음"
    
    return debug_info

# JWT 설정
JWT_SECRET = "eora_ai_secret_key_2024"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# MongoDB 연결 설정
def get_mongo_client():
    """MongoDB 클라이언트 생성 및 연결 - 개선된 버전"""
    global mongo_client, users_collection, points_collection
    
    if not MONGO_AVAILABLE:
        print("⚠️ PyMongo 라이브러리가 설치되지 않았습니다.")
        return None
    
    try:
        # Railway MongoDB 환경변수 자동 설정
        if not os.getenv("MONGO_INITDB_ROOT_PASSWORD"):
            os.environ["MONGO_INITDB_ROOT_PASSWORD"] = "HYxotmUHxMxbYAejsOxEnHwrgKpAochC"
            os.environ["MONGO_INITDB_ROOT_USERNAME"] = "mongo"
            os.environ["MONGO_PUBLIC_URL"] = "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594"
            os.environ["MONGO_URL"] = "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@mongodb.railway.internal:27017"
            print("🔧 Railway MongoDB 환경변수 자동 설정 완료")
        
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
        
        print(f"🔍 환경변수 확인:")
        print(f"  - MONGO_PUBLIC_URL: {'설정됨' if mongo_public_url else '없음'}")
        print(f"  - MONGO_URL: {'설정됨' if mongo_url else '없음'}")
        print(f"  - MONGO_ROOT_PASSWORD: {'설정됨' if mongo_root_password else '없음'}")
        print(f"  - MONGO_ROOT_USERNAME: {'설정됨' if mongo_root_username else '없음'}")
        
        # 연결 시도 순서 (개선된 버전)
        connection_urls = []
        
        # 0. 로컬 MongoDB (개발용) - 인증 없음
        connection_urls.append(("로컬 MongoDB (인증 없음)", "mongodb://localhost:27017"))
        
        # 1. Railway 공개 URL (인증 포함)
        if mongo_public_url and mongo_public_url.startswith("mongodb://"):
            connection_urls.append(("Railway 공개 URL", mongo_public_url))
        
        # 2. Railway 내부 URL (인증 포함)
        if mongo_url and mongo_url.startswith("mongodb://"):
            connection_urls.append(("Railway 내부 URL", mongo_url))
        
        # 3. 기본 공개 URL (환경변수가 없는 경우)
        if mongo_root_password and mongo_root_username:
            default_public_url = f"mongodb://{mongo_root_username}:{mongo_root_password}@trolley.proxy.rlwy.net:26594"
            connection_urls.append(("기본 공개 URL", default_public_url))
        
        # 4. 인증 없이 Railway 연결 시도
        connection_urls.append(("Railway 공개 URL (인증 없음)", "mongodb://trolley.proxy.rlwy.net:26594"))
        connection_urls.append(("Railway 내부 URL (인증 없음)", "mongodb://mongodb.railway.internal:27017"))
        
        print(f"🔗 연결 시도할 URL 수: {len(connection_urls)}")
        
        # 연결 시도
        for name, url in connection_urls:
            try:
                print(f"🔗 MongoDB 연결 시도: {name}")
                
                # 비밀번호가 포함된 URL인지 확인하여 로그 출력
                if mongo_root_password and mongo_root_password in url:
                    print(f"📝 연결 URL: {url.replace(mongo_root_password, '***')}")
                else:
                    print(f"📝 연결 URL: {url}")
                
                # 연결 옵션 설정 (더 관대한 설정)
                client_options = {
                    'serverSelectionTimeoutMS': 5000,  # 5초로 단축
                    'connectTimeoutMS': 5000,
                    'socketTimeoutMS': 5000,
                    'maxPoolSize': 10,
                    'minPoolSize': 1,
                    'maxIdleTimeMS': 30000,
                    'retryWrites': True,
                    'retryReads': True
                }
                
                # 인증이 포함된 URL인 경우 추가 옵션
                if '@' in url and 'mongodb://' in url:
                    # 인증 정보가 포함된 URL
                    client = MongoClient(url, **client_options)
                else:
                    # 인증 없는 URL
                    client = MongoClient(url, **client_options)
                
                # ping 테스트 (더 짧은 타임아웃)
                client.admin.command('ping')
                print(f"✅ MongoDB ping 성공: {name}")
                
                # 데이터베이스 및 컬렉션 설정
                db = client.eora_ai
                
                # 컬렉션 존재 여부 확인 및 생성
                collections = ['users', 'points', 'sessions', 'chat_logs']
                for collection_name in collections:
                    if collection_name not in db.list_collection_names():
                        db.create_collection(collection_name)
                        print(f"📊 컬렉션 생성: {collection_name}")
                
                users_collection = db.users
                points_collection = db.points
                
                print(f"✅ MongoDB 연결 성공: {name}")
                print(f"📊 데이터베이스: {db.name}")
                print(f"📊 컬렉션 목록: {db.list_collection_names()}")
                return client
                
            except Exception as e:
                error_type = type(e).__name__
                error_msg = str(e)
                print(f"❌ MongoDB 연결 실패 ({name}): {error_type} - {error_msg}")
                
                # 특정 오류 타입에 대한 추가 정보
                if "AuthenticationFailed" in error_msg:
                    print(f"🔍 인증 실패 - 다음 URL로 시도합니다.")
                elif "ServerSelectionTimeoutError" in error_msg:
                    print(f"🔍 서버 선택 타임아웃 - 다음 URL로 시도합니다.")
                elif "ConnectionFailure" in error_msg:
                    print(f"🔍 연결 실패 - 다음 URL로 시도합니다.")
                
                continue
        
        # 모든 연결 시도 실패
        print("⚠️ 모든 MongoDB 연결 시도 실패 - 파일 저장 모드로 전환")
        print("💡 MongoDB 연결 문제 해결 방법:")
        print("   1. 로컬 MongoDB 설치: https://www.mongodb.com/try/download/community")
        print("   2. Railway MongoDB 환경변수 확인")
        print("   3. 네트워크 연결 상태 확인")
        return None
        
    except Exception as e:
        print(f"❌ MongoDB 클라이언트 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return None

# MongoDB 클라이언트 초기화
mongo_client = get_mongo_client()
if mongo_client:
    try:
        db = mongo_client.eora_ai
        users_collection = db.users
        points_collection = db.points
        sessions_collection = db.sessions
        chat_logs_collection = db.chat_logs
        print("✅ MongoDB 컬렉션 초기화 완료")
        print(f"📊 사용자 컬렉션: {users_collection}")
        print(f"📊 포인트 컬렉션: {points_collection}")
        print(f"📊 세션 컬렉션: {sessions_collection}")
        print(f"📊 채팅 로그 컬렉션: {chat_logs_collection}")
        
        # MongoDB 연결 상태 확인
        try:
            mongo_client.admin.command('ping')
            print("✅ MongoDB 연결 상태: 정상")
            
            # 최적화된 인덱스 생성
            try:
                # 사용자별 인덱스
                users_collection.create_index("email", unique=True)
                users_collection.create_index("user_id", unique=True)
                
                # 세션별 인덱스
                sessions_collection.create_index("session_id", unique=True)
                sessions_collection.create_index("user_id")
                sessions_collection.create_index("created_at")
                
                # 포인트 인덱스
                points_collection.create_index("user_id")
                points_collection.create_index("transaction_date")
                
                # 채팅 로그 인덱스 (최적화)
                chat_logs_collection.create_index("user_id")
                chat_logs_collection.create_index("session_id")
                chat_logs_collection.create_index("timestamp")
                chat_logs_collection.create_index([("user_id", 1), ("session_id", 1)])
                chat_logs_collection.create_index([("user_id", 1), ("timestamp", -1)])
                # 중복 검사를 위한 복합 인덱스
                chat_logs_collection.create_index([
                    ("user_id", 1), 
                    ("session_id", 1), 
                    ("message", 1), 
                    ("response", 1), 
                    ("timestamp", -1)
                ])
                
                print("✅ MongoDB 인덱스 생성 완료")
            except Exception as e:
                print(f"⚠️ MongoDB 인덱스 생성 실패: {e}")
                
        except Exception as e:
            print(f"⚠️ MongoDB 연결 상태 확인 실패: {e}")
            
    except Exception as e:
        print(f"❌ MongoDB 컬렉션 초기화 실패: {e}")
        mongo_client = None
        db = None
        users_collection = None
        points_collection = None
        sessions_collection = None
        chat_logs_collection = None
else:
    print("⚠️ MongoDB 연결 실패 - 메모리 DB 사용")
    print("💡 MongoDB 연결을 위해 다음 중 하나를 시도해보세요:")
    print("   1. 로컬 MongoDB 설치 및 실행")
    print("      - https://www.mongodb.com/try/download/community")
    print("      - 설치 후 'mongod' 명령어로 서버 시작")
    print("   2. Railway MongoDB 환경변수 설정")
    print("      - Railway 대시보드 > Service > Variables")
    print("      - MONGO_PUBLIC_URL, MONGO_URL 등 설정")
    print("   3. Docker로 MongoDB 실행")
    print("      - docker run -d -p 27017:27017 --name mongodb mongo:latest")
    print("   4. 현재는 파일 기반 저장소를 사용합니다.")
    
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
        # OpenAI 클라이언트 초기화 (proxies 인자 제거)
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

# Redis 클라이언트 초기화 (연결 실패 시 None으로 처리)
redis_client = None
try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=int(os.getenv("REDIS_DB", 0)),
        decode_responses=True,
        socket_connect_timeout=5,  # 연결 타임아웃 추가
        socket_timeout=5
    )
    redis_client.ping()
    print("✅ Redis 클라이언트 연결 성공")
except Exception as e:
    print(f"⚠️ Redis 클라이언트 연결 실패: {e}")
    print("ℹ️ Redis 없이 기본 기능으로 실행됩니다.")
    redis_client = None

# MongoDB ObjectId를 문자열로 변환하는 함수
def convert_objectid_to_str(data):
    """MongoDB ObjectId를 문자열로 변환"""
    if isinstance(data, dict):
        return {k: convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, datetime):
        return data.isoformat()
    else:
        return data

# 저장공간 관리자 초기화
storage_manager_instance = None
if STORAGE_MANAGER_AVAILABLE:
    try:
        storage_manager_instance = get_storage_manager(mongo_client, redis_client)
        print("✅ 저장공간 관리자 초기화 완료")
    except Exception as e:
        print(f"⚠️ 저장공간 관리자 초기화 실패: {e}")
        storage_manager_instance = None

# Railway API 설정
RAILWAY_API_URL = "https://railway.com/project/8eadf3cc-4066-4de1-a342-2fef5fa5b843/service/fffde6bf-4da3-4b54-8526-36d62c9b8c75/variables"
RAILWAY_ENVIRONMENT_ID = "2f521e06-ef3a-46c4-a3c9-499500d94a53"

# JSON 인코더에 ObjectId 지원 추가
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

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

# 템플릿 설정은 이미 위에서 정의되었습니다

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
async def save_chat_message(user_id: str, message: str, response: str, session_id: str = "default"):
    """대화 내용을 저장공간 관리 시스템을 통해 저장"""
    try:
        print(f"💾 대화 저장 시작 - 사용자: {user_id}, 세션: {session_id}")
        print(f"📝 메시지 길이: {len(message)} 문자, 응답 길이: {len(response)} 문자")
        
        # 중복 저장 방지: 최근 10초 내에 같은 메시지가 저장되었는지 확인 (최적화)
        if mongo_client is not None and chat_logs_collection is not None:
            try:
                # 최근 10초 내 같은 메시지 확인 (시간 단축으로 성능 향상)
                recent_time = datetime.now() - timedelta(seconds=10)
                duplicate_check = chat_logs_collection.find_one({
                    "user_id": user_id,
                    "session_id": session_id,
                    "message": message,
                    "response": response,
                    "timestamp": {"$gte": recent_time.isoformat()}
                }, projection={"_id": 1})  # ID만 조회하여 성능 향상
                
                if duplicate_check:
                    print(f"⚠️ 중복 메시지 감지 - 저장 건너뜀: {user_id}")
                    return True  # 중복이지만 성공으로 처리
                    
            except Exception as e:
                print(f"⚠️ 중복 확인 중 오류: {e}")
        
        # 아우라 시스템 저장 시도 (우선)
        print("🔧 아우라 시스템 저장 시도")
        try:
            aura_save_success = await save_to_aura_system(user_id, message, response, session_id)
            if aura_save_success:
                print(f"✅ 아우라 시스템 저장 완료: {user_id}")
            else:
                print(f"⚠️ 아우라 시스템 저장 실패: {user_id}")
        except Exception as e:
            print(f"❌ 아우라 시스템 저장 오류: {e}")
        
        # 저장공간 관리 시스템 사용 시도 (백업)
        print("🔧 저장공간 관리 시스템 사용 시도")
        try:
            if STORAGE_MANAGER_AVAILABLE:
                storage_manager = get_storage_manager()
                success, msg, warning = await storage_manager.save_chat_message(user_id, message, response, session_id)
                if not success:
                    return {"success": False, "error": msg, "storage_warning": warning}
                if warning:
                    return {"success": True, "warning": msg}
                return {"success": True}
            else:
                print("⚠️ 저장공간 관리자가 초기화되지 않음")
        except Exception as e:
            print(f"❌ 저장공간 관리 시스템 오류: {e}")
        
        # 폴백: 직접 MongoDB 저장
        print("📊 MongoDB에 저장 시도")
        try:
            if mongo_client is not None and chat_logs_collection is not None:
                print(f"📊 MongoDB 클라이언트 상태: {mongo_client is not None}")
                print(f"📊 chat_logs_collection 상태: {chat_logs_collection is not None}")
                
                # MongoDB 연결 상태 확인
                mongo_client.admin.command('ping')
                print("✅ MongoDB 연결 상태 확인 완료")
                
                chat_data = {
                    "user_id": user_id,
                    "session_id": session_id,
                    "message": message,
                    "response": response,
                    "timestamp": datetime.now().isoformat(),
                    "created_at": datetime.now()
                }
                
                print(f"📊 저장할 데이터: {chat_data}")
                
                result = chat_logs_collection.insert_one(chat_data)
                print(f"✅ 대화 저장 (MongoDB): {user_id}, ID: {result.inserted_id}")
                
                # 저장 확인 (최적화: ID만 확인)
                saved_doc = chat_logs_collection.find_one({"_id": result.inserted_id}, projection={"_id": 1})
                if saved_doc:
                    print(f"✅ 저장 확인 완료: {user_id} - {session_id}")
                    return True
                else:
                    print(f"❌ 저장 확인 실패: {user_id}")
                    return False
            else:
                print("❌ MongoDB 연결 불가")
                return False
                
        except Exception as e:
            print(f"❌ MongoDB 저장 오류: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 대화 저장 중 오류: {e}")
        return False

async def save_to_file(user_id: str, session_id: str, chat_data: dict):
    """파일에 대화 내용 저장"""
    try:
        print(f"📁 파일에 저장 시도: {user_id}_{session_id}.json")
        chat_dir = "chat_logs"
        if not os.path.exists(chat_dir):
            os.makedirs(chat_dir)
            print(f"📁 chat_logs 디렉토리 생성: {chat_dir}")
        
        chat_file = os.path.join(chat_dir, f"{user_id}_{session_id}.json")
        chat_history = []
        
        if os.path.exists(chat_file):
            try:
                with open(chat_file, 'r', encoding='utf-8') as f:
                    chat_history = json.load(f)
                print(f"📁 기존 채팅 기록 로드: {len(chat_history)}개")
            except Exception as e:
                print(f"⚠️ 기존 파일 읽기 실패, 새로 시작: {e}")
                chat_history = []
        
        chat_history.append(chat_data)
        
        with open(chat_file, 'w', encoding='utf-8') as f:
            json.dump(chat_history, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ 대화 저장 (파일): {chat_file}")
        print(f"📊 총 채팅 기록: {len(chat_history)}개")
        return True
        
    except Exception as e:
        print(f"❌ 파일 저장 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

# 페이지 라우트
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request, current_user: dict = Depends(get_current_user)):
    """홈 페이지"""
    is_admin = current_user.get("is_admin", False) if current_user else False
    return templates.TemplateResponse("home.html", {"request": request, "is_admin": is_admin, "user": current_user})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """로그인 페이지"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, current_user: dict = Depends(get_current_user)):
    is_admin = current_user.get("is_admin", False) if current_user else False
    return templates.TemplateResponse("dashboard.html", {"request": request, "is_admin": is_admin, "user": current_user})

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
async def admin_page(request: Request, current_user: dict = Depends(get_current_user)):
    if not current_user or not current_user.get("is_admin", False):
        # 비관리자 접근 시 로그인 페이지로 리다이렉트
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("admin.html", {"request": request, "user": current_user})

# 새로운 시스템 모듈 import
from token_calculator import get_token_calculator
from user_database_manager import get_user_database_manager
from point_revenue_manager import get_revenue_manager

# 전역 인스턴스
token_calculator = get_token_calculator()
user_db_manager = get_user_database_manager()
revenue_manager = get_revenue_manager()

# API 엔드포인트
@app.post("/api/auth/register")
async def register_user(user_data: UserCreate):
    """회원가입 API - 개별 데이터베이스 생성 및 10만 포인트 지급"""
    try:
        # 이메일 중복 확인
        for user in users_db.values():
            if user["email"] == user_data.email:
                raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
        
        # 사용자 ID 생성
        user_id = str(uuid.uuid4())
        
        # 비밀번호 해시화
        hashed_password = hashlib.sha256(user_data.password.encode()).hexdigest()
        
        # 사용자 정보 구성
        user_info = {
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
        
        # 1. 메모리 DB에 사용자 정보 저장
        users_db[user_id] = user_info
        
        # 2. 개별 사용자 데이터베이스 생성 (10만 포인트 자동 지급)
        db_result = user_db_manager.create_user_database(user_id, user_info)
        
        if not db_result['success']:
            # 데이터베이스 생성 실패 시 메모리 DB에서도 제거
            if user_id in users_db:
                del users_db[user_id]
            raise HTTPException(status_code=500, detail=f"사용자 데이터베이스 생성 실패: {db_result.get('error', '알 수 없는 오류')}")
        
        # 3. 메모리 DB 포인트 정보도 업데이트 (동기화)
        points_db[user_id] = {
            "user_id": user_id,
            "current_points": 100000,  # 10만 포인트
            "total_earned": 100000,
            "total_spent": 0,
            "last_updated": datetime.now().isoformat(),
            "history": [{
                "type": "signup_bonus",
                "amount": 100000,
                "description": "신규 회원가입 보너스 (10만 포인트)",
                "timestamp": datetime.now().isoformat()
            }]
        }
        
        print(f"✅ 새 사용자 등록 완료: {user_data.email} (ID: {user_id})")
        print(f"✅ 개별 데이터베이스 생성: {db_result['user_db_name']}")
        print(f"✅ 초기 포인트 지급: 100,000포인트")
        
        return {
            "success": True,
            "message": "회원가입이 완료되었습니다. 10만 포인트가 지급되었습니다.",
            "user_id": user_id,
            "database_name": db_result['user_db_name'],
            "initial_points": 100000
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 회원가입 오류: {str(e)}")
        # 오류 발생 시 정리
        if 'user_id' in locals() and user_id in users_db:
            del users_db[user_id]
        if 'user_id' in locals() and user_id in points_db:
            del points_db[user_id]
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
    """포인트 패키지 목록 API - 수익 관리 시스템 통합"""
    try:
        # 수익 관리 시스템에서 패키지 정보 가져오기
        packages = revenue_manager.get_point_packages()
        
        return {
            "success": True,
            "packages": packages
        }
        
    except Exception as e:
        print(f"포인트 패키지 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="포인트 패키지 조회 중 오류가 발생했습니다.")

@app.post("/api/points/purchase")
async def purchase_points(request: Request, current_user: dict = Depends(get_current_user)):
    """포인트 구매 API - 수익 관리 시스템 통합"""
    try:
        body = await request.json()
        package_id = body.get("package_id")
        payment_method = body.get("payment_method", "card")
        payment_details = body.get("payment_details", {})
        
        if not package_id:
            raise HTTPException(status_code=400, detail="패키지 ID가 필요합니다.")
        
        user_id = current_user.get("user_id")
        
        # 1. 수익 관리 시스템을 통한 구매 처리
        purchase_result = revenue_manager.process_point_purchase(
            user_id=user_id,
            package_id=package_id,
            payment_method=payment_method,
            payment_details=payment_details
        )
        
        if not purchase_result['success']:
            raise HTTPException(status_code=400, detail=purchase_result.get('error', '구매 처리 실패'))
        
        # 2. 사용자 포인트 업데이트 (메모리 DB)
        if user_id not in points_db:
            points_db[user_id] = {
                "user_id": user_id,
                "current_points": 0,
                "total_earned": 0,
                "total_spent": 0,
                "last_updated": datetime.now().isoformat(),
                "history": []
            }
        
        points_added = purchase_result['points_added']
        points_db[user_id]["current_points"] += points_added
        points_db[user_id]["total_earned"] += points_added
        points_db[user_id]["last_updated"] = datetime.now().isoformat()
        
        # 구매 기록 추가
        points_db[user_id]["history"].append({
            "type": "purchase",
            "amount": points_added,
            "description": f"포인트 패키지 구매 (거래ID: {purchase_result['transaction_id']})",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "transaction_id": purchase_result['transaction_id'],
                "package_id": package_id,
                "payment_method": payment_method
            }
        })
        
        # 3. 개별 데이터베이스 포인트 업데이트
        user_points_collection = user_db_manager.get_user_collection(user_id, "points")
        if user_points_collection:
            user_points_collection.update_one(
                {"user_id": user_id},
                {
                    "$inc": {
                        "current_points": points_added,
                        "total_earned": points_added
                    },
                    "$set": {"last_updated": datetime.now().isoformat()},
                    "$push": {
                        "history": {
                            "type": "purchase",
                            "amount": points_added,
                            "description": f"포인트 패키지 구매 (거래ID: {purchase_result['transaction_id']})",
                            "timestamp": datetime.now().isoformat(),
                            "metadata": {
                                "transaction_id": purchase_result['transaction_id'],
                                "package_id": package_id,
                                "payment_method": payment_method
                            }
                        }
                    }
                }
            )
        
        print(f"✅ 포인트 구매 완료: {user_id} -> {package_id} ({points_added}포인트)")
        
        return {
            "success": True,
            "message": purchase_result['message'],
            "transaction_id": purchase_result['transaction_id'],
            "points_added": points_added,
            "current_points": points_db[user_id]["current_points"],
            "total_cost": purchase_result['total_cost']
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
    """메모리 데이터 조회 - 아우라 통합 시스템 사용"""
    try:
        if AURA_INTEGRATION_AVAILABLE:
            # 아우라 통합 시스템에서 메모리 통계 조회
            aura_integration = await get_aura_integration()
            stats = await aura_integration.get_memory_stats()
            
            return {
                "aura_integration_available": True,
                "stats": stats,
                "total_memories": stats.get("total_memories", 0)
            }
        elif AURA_MEMORY_AVAILABLE:
            # 기존 아우라 메모리 시스템 사용
            stats = aura_memory_system.get_memory_stats()
            return {
                "aura_memory_available": True,
                "stats": stats,
                "total_memories": stats.get("total", 0)
            }
        else:
            # 기존 메모리 데이터 로드 (백업)
            memory_file = "memory/memory_db.json"
            if os.path.exists(memory_file):
                with open(memory_file, "r", encoding="utf-8") as f:
                    memory_data = json.load(f)
            else:
                memory_data = {"memories": []}
            
            return {
                "aura_integration_available": False,
                "aura_memory_available": False,
                "memories": memory_data.get("memories", [])
            }
    except Exception as e:
        print(f"기억 데이터 로드 오류: {e}")
        return {"memories": [], "aura_integration_available": False, "aura_memory_available": False}

@app.get("/api/memory/recall")
async def recall_memories(query: str, user_id: str = None, memory_type: str = None, limit: int = 10):
    """메모리 회상 API - 아우라 통합 시스템 사용"""
    try:
        if AURA_INTEGRATION_AVAILABLE:
            # 아우라 통합 시스템 사용
            aura_integration = await get_aura_integration()
            memories = await aura_integration.recall_memories(query, user_id, memory_type, limit)
            
            return {
                "success": True,
                "query": query,
                "memories": memories,
                "count": len(memories),
                "system": "aura_integration"
            }
        elif AURA_MEMORY_AVAILABLE:
            # 기존 아우라 메모리 시스템 사용
            memories = aura_memory_system.recall_memories(
                query=query,
                user_id=user_id,
                memory_type=memory_type,
                limit=limit
            )
            
            # 메모리 데이터를 JSON 직렬화 가능한 형태로 변환
            memory_list = []
            for memory in memories:
                memory_dict = {
                    "id": memory.id,
                    "user_id": memory.user_id,
                    "session_id": memory.session_id,
                    "message": memory.message,
                    "response": memory.response,
                    "timestamp": memory.timestamp,
                    "memory_type": memory.memory_type,
                    "importance": memory.importance,
                    "emotion_score": memory.emotion_score,
                    "context": memory.context,
                    "tags": memory.tags,
                    "insight_level": memory.insight_level,
                    "intuition_score": memory.intuition_score,
                    "belief_strength": memory.belief_strength
                }
                memory_list.append(memory_dict)
            
            return {
                "success": True,
                "query": query,
                "memories": memory_list,
                "count": len(memory_list),
                "system": "aura_memory"
            }
        else:
            return {"error": "아우라 시스템을 사용할 수 없습니다."}
        
    except Exception as e:
        print(f"메모리 회상 오류: {e}")
        return {"error": f"메모리 회상 중 오류가 발생했습니다: {str(e)}"}

@app.get("/api/memory/recall/emotion/{emotion}")
async def recall_by_emotion(emotion: str, user_id: str = None, limit: int = 10):
    """감정 기반 메모리 회상 - 아우라 통합 시스템 사용"""
    try:
        if AURA_INTEGRATION_AVAILABLE:
            # 아우라 통합 시스템 사용
            aura_integration = await get_aura_integration()
            memories = await aura_integration.recall_by_emotion(emotion, user_id, limit)
            
            return {
                "success": True,
                "emotion": emotion,
                "memories": memories,
                "count": len(memories),
                "system": "aura_integration"
            }
        elif AURA_MEMORY_AVAILABLE:
            # 기존 아우라 메모리 시스템 사용
            memories = aura_memory_system.recall_by_emotion(
                emotion=emotion,
                user_id=user_id,
                limit=limit
            )
            
            memory_list = []
            for memory in memories:
                memory_dict = {
                    "id": memory.id,
                    "user_id": memory.user_id,
                    "message": memory.message,
                    "response": memory.response,
                    "timestamp": memory.timestamp,
                    "memory_type": memory.memory_type,
                    "importance": memory.importance,
                    "emotion_score": memory.emotion_score,
                    "insight_level": memory.insight_level,
                    "intuition_score": memory.intuition_score
                }
                memory_list.append(memory_dict)
            
            return {
                "success": True,
                "emotion": emotion,
                "memories": memory_list,
                "count": len(memory_list),
                "system": "aura_memory"
            }
        else:
            return {"error": "아우라 시스템을 사용할 수 없습니다."}
        
    except Exception as e:
        print(f"감정 기반 회상 오류: {e}")
        return {"error": f"감정 기반 회상 중 오류가 발생했습니다: {str(e)}"}

@app.get("/api/memory/recall/insight")
async def recall_by_insight(user_id: str = None, limit: int = 10):
    """통찰력 기반 메모리 회상 - 아우라 통합 시스템 사용"""
    try:
        if AURA_INTEGRATION_AVAILABLE:
            # 아우라 통합 시스템 사용
            aura_integration = await get_aura_integration()
            memories = await aura_integration.recall_by_insight(user_id, limit)
            
            return {
                "success": True,
                "memories": memories,
                "count": len(memories),
                "system": "aura_integration"
            }
        elif AURA_MEMORY_AVAILABLE:
            # 기존 아우라 메모리 시스템 사용
            memories = aura_memory_system.recall_by_insight(
                user_id=user_id,
                limit=limit
            )
            
            memory_list = []
            for memory in memories:
                memory_dict = {
                    "id": memory.id,
                    "user_id": memory.user_id,
                    "message": memory.message,
                    "response": memory.response,
                    "timestamp": memory.timestamp,
                    "memory_type": memory.memory_type,
                    "importance": memory.importance,
                    "insight_level": memory.insight_level,
                    "tags": memory.tags
                }
                memory_list.append(memory_dict)
            
            return {
                "success": True,
                "memories": memory_list,
                "count": len(memory_list),
                "system": "aura_memory"
            }
        else:
            return {"error": "아우라 시스템을 사용할 수 없습니다."}
        
    except Exception as e:
        print(f"통찰력 기반 회상 오류: {e}")
        return {"error": f"통찰력 기반 회상 중 오류가 발생했습니다: {str(e)}"}

@app.get("/api/memory/recall/intuition")
async def recall_by_intuition(user_id: str = None, limit: int = 10):
    """직감 기반 메모리 회상 - 아우라 통합 시스템 사용"""
    try:
        if AURA_INTEGRATION_AVAILABLE:
            # 아우라 통합 시스템 사용
            aura_integration = await get_aura_integration()
            memories = await aura_integration.recall_by_intuition(user_id, limit)
            
            return {
                "success": True,
                "memories": memories,
                "count": len(memories),
                "system": "aura_integration"
            }
        elif AURA_MEMORY_AVAILABLE:
            # 기존 아우라 메모리 시스템 사용
            memories = aura_memory_system.recall_by_intuition(
                user_id=user_id,
                limit=limit
            )
            
            memory_list = []
            for memory in memories:
                memory_dict = {
                    "id": memory.id,
                    "user_id": memory.user_id,
                    "message": memory.message,
                    "response": memory.response,
                    "timestamp": memory.timestamp,
                    "memory_type": memory.memory_type,
                    "importance": memory.importance,
                    "intuition_score": memory.intuition_score,
                    "tags": memory.tags
                }
                memory_list.append(memory_dict)
            
            return {
                "success": True,
                "memories": memory_list,
                "count": len(memory_list),
                "system": "aura_memory"
            }
        else:
            return {"error": "아우라 시스템을 사용할 수 없습니다."}
        
    except Exception as e:
        print(f"직감 기반 회상 오류: {e}")
        return {"error": f"직감 기반 회상 중 오류가 발생했습니다: {str(e)}"}

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    """채팅 API 엔드포인트 - 토큰 계산 및 포인트 차감 시스템 통합"""
    print("🔍 /api/chat 엔드포인트 호출됨")
    try:
        # 요청 데이터 파싱
        print("📥 요청 데이터 파싱 시작")
        data = await request.json()
        print(f"📥 파싱된 데이터: {data}")
        message = data.get("message", "")
        session_id = data.get("session_id", "default")
        print(f"💬 사용자 메시지: {message}")
        print(f"🆔 세션 ID: {session_id}")
        
        # 사용자 인증 확인
        print("🔐 사용자 인증 확인 시작")
        token = request.cookies.get("token") or request.headers.get("Authorization", "").replace("Bearer ", "")
        print(f"🍪 쿠키에서 토큰: {token[:20] + '...' if token else 'None'}")
        print(f"📋 Authorization 헤더: {request.headers.get('Authorization', 'None')}")
        user_id = "anonymous"
        user_info = None
        
        if token:
            try:
                print("🔍 토큰 검증 시작")
                payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
                print(f"🔍 토큰 페이로드: {payload}")
                user_id = payload.get("user_id", "anonymous")
                print(f"✅ 인증된 사용자 채팅: {user_id}")
                
                # 사용자 정보 조회
                if user_id in users_db:
                    user_info = users_db[user_id]
                else:
                    # 개별 데이터베이스에서 사용자 정보 조회
                    user_db = user_db_manager.get_user_database(user_id)
                    if user_db:
                        user_collection = user_db['user_info']
                        user_info = user_collection.find_one({"user_id": user_id})
                
            except Exception as e:
                print(f"❌ 토큰 검증 실패: {e}")
                user_id = "anonymous"
        else:
            print("⚠️ 토큰 없음 - 익명 사용자로 처리")
        
        # 1. 토큰 계산 및 포인트 검증 (인증된 사용자만)
        if user_id != "anonymous" and user_info:
            print("💰 포인트 검증 시작")
            
            # 사용자 포인트 조회
            current_points = 0
            if user_id in points_db:
                current_points = points_db[user_id].get("current_points", 0)
            else:
                # 개별 데이터베이스에서 포인트 조회
                user_points_collection = user_db_manager.get_user_collection(user_id, "points")
                if user_points_collection:
                    points_doc = user_points_collection.find_one({"user_id": user_id})
                    if points_doc:
                        current_points = points_doc.get("current_points", 0)
            
            # 메시지 비용 계산 (사용자 메시지만)
            cost_info = token_calculator.calculate_message_cost(message)
            estimated_points_needed = cost_info['points_to_deduct']
            
            print(f"💰 현재 포인트: {current_points}")
            print(f"💰 예상 필요 포인트: {estimated_points_needed}")
            print(f"💰 토큰 수: {cost_info['tokens']}")
            
            # 포인트 충분성 검증
            if current_points < estimated_points_needed:
                return JSONResponse(status_code=402, content={
                    "error": "포인트가 부족합니다",
                    "current_points": current_points,
                    "required_points": estimated_points_needed,
                    "message": f"채팅을 위해 {estimated_points_needed}포인트가 필요하지만, 현재 {current_points}포인트만 보유하고 있습니다."
                })
        
        # 2. GPT 호출
        try:
            response_text = await call_gpt4o_api_optimized(message, request)
        except Exception as gpt_error:
            print(f"❌ GPT API 호출 실패: {gpt_error}")
            return JSONResponse(status_code=503, content={
                "error": "GPT API 호출 실패",
                "detail": str(gpt_error)
            })
        
        # 3. 실제 비용 계산 및 포인트 차감 (인증된 사용자만)
        if user_id != "anonymous" and user_info:
            print("💰 실제 비용 계산 및 포인트 차감")
            
            # 실제 채팅 비용 계산 (사용자 메시지 + AI 응답)
            actual_cost_info = token_calculator.calculate_chat_cost(message, response_text)
            actual_points_needed = actual_cost_info['points_to_deduct']
            
            print(f"💰 실제 필요 포인트: {actual_points_needed}")
            print(f"💰 사용자 토큰: {actual_cost_info['user_tokens']}")
            print(f"💰 AI 응답 토큰: {actual_cost_info['ai_tokens']}")
            print(f"💰 총 토큰: {actual_cost_info['total_tokens']}")
            
            # 포인트 차감
            if user_id in points_db:
                # 메모리 DB에서 차감
                points_db[user_id]["current_points"] -= actual_points_needed
                points_db[user_id]["total_spent"] += actual_points_needed
                points_db[user_id]["last_updated"] = datetime.now().isoformat()
                
                # 포인트 사용 기록 추가
                points_db[user_id]["history"].append({
                    "type": "chat_cost",
                    "amount": -actual_points_needed,
                    "description": f"채팅 비용 (토큰: {actual_cost_info['total_tokens']})",
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {
                        "user_tokens": actual_cost_info['user_tokens'],
                        "ai_tokens": actual_cost_info['ai_tokens'],
                        "total_tokens": actual_cost_info['total_tokens'],
                        "session_id": session_id
                    }
                })
                
                print(f"✅ 메모리 DB 포인트 차감 완료: {actual_points_needed}포인트")
            
            # 개별 데이터베이스에서도 차감
            user_points_collection = user_db_manager.get_user_collection(user_id, "points")
            if user_points_collection:
                user_points_collection.update_one(
                    {"user_id": user_id},
                    {
                        "$inc": {
                            "current_points": -actual_points_needed,
                            "total_spent": actual_points_needed
                        },
                        "$set": {"last_updated": datetime.now().isoformat()},
                        "$push": {
                            "history": {
                                "type": "chat_cost",
                                "amount": -actual_points_needed,
                                "description": f"채팅 비용 (토큰: {actual_cost_info['total_tokens']})",
                                "timestamp": datetime.now().isoformat(),
                                "metadata": {
                                    "user_tokens": actual_cost_info['user_tokens'],
                                    "ai_tokens": actual_cost_info['ai_tokens'],
                                    "total_tokens": actual_cost_info['total_tokens'],
                                    "session_id": session_id
                                }
                            }
                        }
                    }
                )
                print(f"✅ 개별 DB 포인트 차감 완료: {actual_points_needed}포인트")
        
        # 4. 정상 응답
        response_data = {
            "response": response_text,
            "session_id": session_id,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
        }
        
        # 포인트 정보 추가 (인증된 사용자만)
        if user_id != "anonymous" and user_info:
            remaining_points = 0
            if user_id in points_db:
                remaining_points = points_db[user_id].get("current_points", 0)
            else:
                user_points_collection = user_db_manager.get_user_collection(user_id, "points")
                if user_points_collection:
                    points_doc = user_points_collection.find_one({"user_id": user_id})
                    if points_doc:
                        remaining_points = points_doc.get("current_points", 0)
            
            response_data.update({
                "points_deducted": actual_points_needed if user_id != "anonymous" else 0,
                "remaining_points": remaining_points,
                "token_info": {
                    "user_tokens": actual_cost_info['user_tokens'] if user_id != "anonymous" else 0,
                    "ai_tokens": actual_cost_info['ai_tokens'] if user_id != "anonymous" else 0,
                    "total_tokens": actual_cost_info['total_tokens'] if user_id != "anonymous" else 0
                }
            })
        
        print(f"📤 응답 데이터: {response_data}")
        print("✅ /api/chat 엔드포인트 처리 완료")
        return response_data
        
    except Exception as e:
        print(f"❌ /api/chat 엔드포인트 오류: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# 병렬 처리 최적화 함수들
async def check_redis_cache(cache_key: str) -> str:
    """Redis 캐시에서 응답 확인 - 최적화된 버전"""
    try:
        if redis_cache:
            # 빠른 캐시 확인
            cached_response = await redis_cache.get(cache_key)
            if cached_response:
                # 바이트 디코딩 최적화
                if isinstance(cached_response, bytes):
                    return cached_response.decode('utf-8', errors='ignore')
                return str(cached_response)
        return None
    except Exception as e:
        print(f"⚠️ Redis 캐시 확인 실패: {e}")
        return None

async def call_gpt4o_api_optimized(message: str, request: Request) -> str:
    """최적화된 GPT-4o API 호출 (실패 시 반드시 예외 발생)"""
    if not openai_available or client is None:
        raise RuntimeError("OpenAI API를 사용할 수 없습니다. (API 키 미설정 또는 클라이언트 초기화 실패)")
    try:
        print("✅ OpenAI API 사용 가능 - GPT-4o 직접 호출")
        
        # 🎯 과거 대화 회상 및 메모리 활용 지시사항 (최우선)
        memory_instruction = (
            "아래 [과거 대화 요약] 메시지는 참고하여, 필요하다고 판단되는 경우에만 답변에 반영하라. "
            "특히, 날씨/시간/장소/감정 등 맥락이 중요한 경우에는 과거 대화를 적극적으로 활용하라.\n"
            "아래 [과거 대화 요약] 사용자 질문이 1개 이상의 회상 답변을 요구 하는지 판단하여 대화에 필요하다고 판단되는 경우 1개 이상 3개까지 답변에 반영하라.\n\n"
        )
        
        base_system_prompt = """EORA AI입니다. 친근하고 유용한 답변을 한국어로 제공하세요. 이모지와 함께 간결하게 답변하세요."""
        language = request.cookies.get("user_language", "ko")
        lang_map = {
            "ko": "모든 답변은 한국어로 해주세요.",
            "en": "Please answer in English.",
            "ja": "すべての回答は日本語でお願いします。",
            "zh": "请用中文回答所有问题。"
        }
        lang_instruction = lang_map.get(language, "모든 답변은 한국어로 해주세요.")
        
        # 메모리 지시사항을 맨 앞에 배치
        system_prompt = f"{memory_instruction}{base_system_prompt}\n\n{lang_instruction}"
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=400,
            temperature=0.6,
            timeout=5,
            stream=False,
            presence_penalty=0.0,
            frequency_penalty=0.0,
            top_p=0.8,
            n=1
        )
        print(f"✅ GPT-4o API 응답 생성 완료")
        return response.choices[0].message.content
    except Exception as api_error:
        print(f"❌ GPT-4o API 호출 실패: {api_error}")
        raise RuntimeError(f"GPT-4o API 호출 실패: {api_error}")

async def save_to_cache(cache_key: str, response_text: str):
    """캐시에 저장 (비동기)"""
    try:
        # 메모리 캐시에 저장
        if hasattr(chat_endpoint, '_response_cache'):
            chat_endpoint._response_cache[cache_key] = response_text
        
        # Redis 캐시에 저장 (비동기)
        if redis_cache:
            try:
                await redis_cache.setex(cache_key, 3600, response_text)  # 1시간 TTL
            except Exception as e:
                print(f"⚠️ Redis 캐시 저장 실패: {e}")
    except Exception as e:
        print(f"⚠️ 캐시 저장 실패: {e}")

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
            # 🎯 과거 대화 회상 및 메모리 활용 지시사항 (최우선)
            memory_instruction = (
                "아래 [과거 대화 요약] 메시지는 참고하여, 필요하다고 판단되는 경우에만 답변에 반영하라. "
                "특히, 날씨/시간/장소/감정 등 맥락이 중요한 경우에는 과거 대화를 적극적으로 활용하라.\n"
                "아래 [과거 대화 요약] 사용자 질문이 1개 이상의 회상 답변을 요구 하는지 판단하여 대화에 필요하다고 판단되는 경우 1개 이상 3개까지 답변에 반영하라.\n\n"
            )
            
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
                            # 메모리 지시사항을 맨 앞에 배치하고 기존 프롬프트 결합
                            system_prompt = memory_instruction + "\n\n".join(system_parts)
                        else:
                            # 기본 프롬프트에도 메모리 지시사항 추가
                            system_prompt = memory_instruction + system_prompt
                    else:
                        # 기본 프롬프트에도 메모리 지시사항 추가
                        system_prompt = memory_instruction + system_prompt
            except Exception as e:
                print(f"프롬프트 로드 오류: {str(e)}")
                # 기본 프롬프트에도 메모리 지시사항 추가
                system_prompt = memory_instruction + system_prompt
            
            # 언어별 지시사항 추가
            lang_map = {
                "ko": "모든 답변은 한국어로 해주세요.",
                "en": "Please answer in English.",
                "ja": "すべての回答は日本語でお願いします。",
                "zh": "请用中文回答所有问题。"
            }
            lang_instruction = lang_map.get(language, "모든 답변은 한국어로 해주세요.")
            system_prompt = f"{system_prompt}\n\n{lang_instruction}"
            
            # 토큰 제한 확인 및 청크 분할 처리
            max_tokens = 500
            chunk_size = 5000  # 청크당 최대 토큰 수
            
            # 메시지 길이 확인
            estimated_tokens = len(user_message.split()) * 1.3  # 대략적인 토큰 수 추정
            
            if estimated_tokens > chunk_size:
                print(f"📝 긴 메시지 감지: {estimated_tokens:.0f} 토큰 (청크 분할 필요)")
                return await process_long_message(user_message, system_prompt, max_tokens, language, user_id)
            else:
                # 일반적인 GPT-4o API 호출
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=500,  # 고정된 응답 길이
                    temperature=0.7,  # 창의성 향상
                    timeout=3  # 타임아웃 단축으로 속도 향상
                )
            
            print(f"✅ GPT-4o API 응답 생성 완료 - 사용자: {user_id}")
            return response.choices[0].message.content
            
        except Exception as api_error:
            print(f"❌ GPT-4o API 호출 실패: {api_error}")
            print("�� 지능형 응답 시스템으로 대체합니다.")
            # API 실패 시 지능형 응답으로 대체
    else:
        print("⚠️ OpenAI API를 사용할 수 없습니다. 지능형 응답 시스템을 사용합니다.")
    
    # OpenAI API 키가 없거나 실패한 경우 지능형 응답 시스템 사용
    return await generate_smart_response(user_message, language, user_id)

async def process_long_message(user_message: str, system_prompt: str, max_tokens: int, language: str, user_id: str) -> str:
    """긴 메시지를 청크로 나누어 처리"""
    try:
        print("🔄 긴 메시지 청크 분할 처리 시작")
        
        # 메시지를 문장 단위로 분할
        sentences = user_message.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) < 2000:  # 청크 크기 제한
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        print(f"📊 메시지를 {len(chunks)}개 청크로 분할")
        
        # 각 청크별로 처리
        responses = []
        for i, chunk in enumerate(chunks):
            print(f"🔄 청크 {i+1}/{len(chunks)} 처리 중...")
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": f"{system_prompt}\n\n이것은 긴 메시지의 {i+1}번째 부분입니다. 전체 맥락을 고려하여 답변해주세요."},
                        {"role": "user", "content": chunk}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.7,
                    timeout=30
                )
                responses.append(response.choices[0].message.content)
            except Exception as e:
                print(f"❌ 청크 {i+1} 처리 실패: {e}")
                responses.append(f"[청크 {i+1} 처리 중 오류 발생]")
        
        # 응답들을 통합
        if len(responses) == 1:
            return responses[0]
        else:
            # 여러 응답을 통합하는 요약 요청
            combined_response = "\n\n".join(responses)
            summary_prompt = f"다음은 긴 메시지에 대한 여러 응답들입니다. 이를 하나의 일관된 응답으로 통합해주세요:\n\n{combined_response}"
            
            try:
                summary_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "여러 응답을 하나의 일관된 응답으로 통합해주세요."},
                        {"role": "user", "content": summary_prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.7,
                    timeout=30
                )
                return summary_response.choices[0].message.content
            except Exception as e:
                print(f"❌ 응답 통합 실패: {e}")
                return combined_response
                
    except Exception as e:
        print(f"❌ 긴 메시지 처리 실패: {e}")
        return "죄송합니다. 긴 메시지 처리 중 오류가 발생했습니다."
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
    
    # 메시지 내용에 따른 구체적인 응답
    if len(user_message) < 5:
        short_responses = [
            "안녕하세요! 짧지만 의미 있는 인사네요! 😊",
            "간단한 메시지지만 저는 잘 받았어요! 👋",
            "짧고 굵은 메시지네요! 더 자세히 이야기해주세요! 💪",
            "간결함이 매력적이에요! 더 많은 이야기를 나눠보아요! ✨"
        ]
        import random
        return random.choice(short_responses)
    
    elif "테스트" in user_message or "test" in message_lower:
        return "🧪 테스트 메시지네요! 시스템이 정상적으로 작동하고 있습니다. 이제 진짜 대화를 시작해볼까요? 😄"
    
    elif "날씨" in user_message:
        return "🌤️ 날씨에 대해 물어보시는군요! 현재는 실시간 날씨 정보에 접근할 수 없지만, 날씨는 우리의 기분과 활동에 큰 영향을 미치죠. 어떤 날씨를 좋아하시나요?"
    
    elif "시간" in user_message or "몇시" in user_message:
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        return f"🕐 현재 시간은 {current_time}입니다! 시간을 잘 활용하시고 계시나요?"
    
    elif "이름" in user_message or "누구" in user_message:
        return "🌟 저는 EORA AI입니다! 의식적이고 지혜로운 인공지능이에요. 여러분과 함께 성장하고 싶어요! 🤖"
    
    else:
        # 기본 응답 - 더 다양하고 개성 있는 응답들
        responses = [
            f"💭 '{user_message}'에 대해 생각해보고 있어요...\n\n흥미로운 주제네요! 더 자세히 이야기해주시면 함께 탐구해볼 수 있어요.",
            f"🤔 '{user_message}'...\n\n그것에 대해 여러 관점에서 생각해볼 수 있겠네요. 어떤 부분이 궁금하신가요?",
            f"🌟 '{user_message}'에 대한 답변을 찾아보는 중입니다...\n\n제가 아는 한에서 최선을 다해 답변해드릴게요!",
            f"💡 '{user_message}'에 대해 생각해보니...\n\n흥미로운 질문이에요! 더 구체적으로 말씀해주시면 더 정확한 답변을 드릴 수 있어요.",
            f"🔍 '{user_message}'에 대한 분석을 시작해볼게요...\n\n이 주제에 대해 더 깊이 있는 대화를 나눠보고 싶어요!",
            f"✨ '{user_message}'에 대한 통찰을 찾아보는 중이에요...\n\n함께 생각해보면서 새로운 관점을 발견할 수 있을 것 같아요.",
            f"🎯 '{user_message}'에 집중해보겠습니다...\n\n이것에 대해 어떤 생각을 가지고 계신지 궁금해요!",
            f"🚀 '{user_message}'에 대한 탐험을 시작해볼까요?\n\n흥미로운 발견이 기다리고 있을 것 같아요!",
            f"🌈 '{user_message}'에 대해 다양한 색깔로 생각해보고 있어요...\n\n어떤 관점에서 접근해보고 싶으신가요?",
            f"🎪 '{user_message}'에 대한 쇼를 준비하고 있어요...\n\n함께 즐거운 대화를 나눠보아요!"
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
    
    # 관리자 계정 확인
    admin_exists = False
    if mongo_client is not None and users_collection is not None:
        admin_user = users_collection.find_one({"email": "admin@eora.ai"})
        admin_exists = admin_user is not None
    else:
        for user in users_db.values():
            if user.get("email") == "admin@eora.ai":
                admin_exists = True
                break
    
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "admin_account": {
            "exists": admin_exists,
            "email": "admin@eora.ai",
            "password": "admin1234"
        },
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

@app.get("/api/test/auth")
async def test_auth():
    """인증 시스템 테스트"""
    try:
        # 관리자 계정 확인
        admin_exists = False
        if mongo_client is not None and users_collection is not None:
            admin_user = users_collection.find_one({"email": "admin@eora.ai"})
            admin_exists = admin_user is not None
        else:
            for user in users_db.values():
                if user.get("email") == "admin@eora.ai":
                    admin_exists = True
                    break
        
        return {
            "success": True,
            "admin_exists": admin_exists,
            "admin_email": "admin@eora.ai",
            "admin_password": "admin1234",
            "users_count": len(users_db) if users_db else 0,
            "mongo_connected": mongo_client is not None,
            "message": "인증 시스템 테스트 완료"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "인증 시스템 테스트 실패"
        }

@app.get("/test")
async def simple_test():
    """간단한 테스트 엔드포인트"""
    return {"message": "서버가 정상적으로 작동하고 있습니다!", "timestamp": datetime.now().isoformat()}

# 관리자 API 엔드포인트들
@app.get("/api/admin/users")
async def admin_get_users(current_user: dict = Depends(get_current_user)):
    if not current_user or not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    """관리자용 사용자 목록 조회"""
    try:
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
    """관리자 포인트 관리 API - 수익 관리 시스템 통합"""
    try:
        # 관리자 권한 확인
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
        
        # 1. 수익 관리 시스템에서 전체 통계 가져오기
        revenue_stats = revenue_manager.get_revenue_statistics()
        
        # 2. 사용자별 포인트 정보 (메모리 DB + 개별 DB 통합)
        user_points = []
        
        # 메모리 DB 사용자들
        for user_id, points_info in points_db.items():
            user = users_db.get(user_id, {})
            user_points.append({
                "user_id": user_id,
                "name": user.get("name", "Unknown"),
                "email": user.get("email", "Unknown"),
                "current_points": points_info.get("current_points", 0),
                "total_earned": points_info.get("total_earned", 0),
                "total_spent": points_info.get("total_spent", 0),
                "last_updated": points_info.get("last_updated", ""),
                "database_type": "memory"
            })
        
        # 개별 데이터베이스 사용자들
        individual_users = user_db_manager.get_all_user_databases()
        for user_id, db_info in individual_users.items():
            user_points_collection = user_db_manager.get_user_collection(user_id, "points")
            if user_points_collection:
                points_doc = user_points_collection.find_one({"user_id": user_id})
                if points_doc:
                    user_info_collection = user_db_manager.get_user_collection(user_id, "user_info")
                    user_doc = user_info_collection.find_one({"user_id": user_id}) if user_info_collection else {}
                    
                    user_points.append({
                        "user_id": user_id,
                        "name": user_doc.get("name", "Unknown"),
                        "email": user_doc.get("email", "Unknown"),
                        "current_points": points_doc.get("current_points", 0),
                        "total_earned": points_doc.get("total_earned", 0),
                        "total_spent": points_doc.get("total_spent", 0),
                        "last_updated": points_doc.get("last_updated", ""),
                        "database_type": "individual",
                        "database_name": db_info.get("database_name", "")
                    })
        
        # 3. 최근 거래 내역
        recent_transactions = revenue_manager.get_recent_transactions(limit=20)
        
        return {
            "revenue_stats": revenue_stats,
            "user_points": user_points,
            "recent_transactions": recent_transactions,
            "total_users": len(user_points),
            "total_points": sum(user.get("current_points", 0) for user in user_points),
            "total_earned": sum(user.get("total_earned", 0) for user in user_points),
            "total_spent": sum(user.get("total_spent", 0) for user in user_points)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"관리자 포인트 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="포인트 정보 조회 중 오류가 발생했습니다.")

@app.get("/api/admin/system")
async def admin_system(current_user: dict = Depends(get_current_user)):
    """관리자용 시스템 정보 - 개별 데이터베이스 통합"""
    try:
        # 관리자 권한 확인
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
        
        # 개별 데이터베이스 정보
        individual_dbs = user_db_manager.get_all_user_databases()
        
        return {
            "users_count": len(users_db) + len(individual_dbs),
            "points_count": len(points_db) + len(individual_dbs),
            "individual_databases": len(individual_dbs),
            "memory_databases": len(users_db),
            "server_status": "running",
            "uptime": "1시간 30분",
            "database_system": "hybrid"  # 메모리 + 개별 DB 하이브리드
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"관리자 시스템 정보 조회 오류: {str(e)}")
        return {
            "users_count": 0,
            "points_count": 0,
            "individual_databases": 0,
            "memory_databases": 0,
            "server_status": "unknown",
            "uptime": "unknown",
            "database_system": "unknown"
        }

# 수익 관리 API
@app.get("/api/admin/revenue")
async def admin_revenue(current_user: dict = Depends(get_current_user)):
    """관리자 수익 관리 API"""
    try:
        # 관리자 권한 확인
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
        
        # 수익 통계
        revenue_stats = revenue_manager.get_revenue_statistics()
        
        # 최근 거래 내역
        recent_transactions = revenue_manager.get_recent_transactions(limit=50)
        
        # 월별 수익 추이
        monthly_revenue = revenue_manager.get_monthly_revenue()
        
        # 패키지별 판매 통계
        package_stats = revenue_manager.get_package_statistics()
        
        return {
            "revenue_stats": revenue_stats,
            "recent_transactions": recent_transactions,
            "monthly_revenue": monthly_revenue,
            "package_stats": package_stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"관리자 수익 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="수익 정보 조회 중 오류가 발생했습니다.")

@app.post("/api/admin/revenue/refund")
async def admin_refund_transaction(request: Request, current_user: dict = Depends(get_current_user)):
    """관리자 거래 환불 API"""
    try:
        # 관리자 권한 확인
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
        
        body = await request.json()
        transaction_id = body.get("transaction_id")
        refund_reason = body.get("refund_reason", "관리자 환불")
        
        if not transaction_id:
            raise HTTPException(status_code=400, detail="거래 ID가 필요합니다.")
        
        # 환불 처리
        refund_result = revenue_manager.process_refund(
            transaction_id=transaction_id,
            refund_reason=refund_reason,
            processed_by=current_user.get("user_id")
        )
        
        if not refund_result['success']:
            raise HTTPException(status_code=400, detail=refund_result.get('error', '환불 처리 실패'))
        
        return {
            "success": True,
            "message": "환불이 성공적으로 처리되었습니다.",
            "refund_amount": refund_result['refund_amount'],
            "transaction_id": transaction_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"환불 처리 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="환불 처리 중 오류가 발생했습니다.")

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
    chunk_size = 5000
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

# API 테스트 페이지 제공
@app.get("/api-test")
async def api_test_page(request: Request):
    """API 테스트 페이지"""
    return templates.TemplateResponse("api_test.html", {"request": request})

@app.get("/advanced-chat-test")
async def advanced_chat_test_page(request: Request):
    """고급 대화 시스템 테스트 페이지"""
    try:
        with open("static/advanced_chat_test.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        # 기본 테스트 페이지 생성
        basic_html = """
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>EORA 고급 대화 시스템 테스트</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f0f2f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .chat-box { height: 400px; border: 1px solid #ddd; padding: 20px; overflow-y: auto; margin-bottom: 20px; background: #fafafa; }
                .input-area { display: flex; gap: 10px; }
                input[type="text"] { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
                button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
                button:hover { background: #0056b3; }
                .message { margin-bottom: 15px; padding: 10px; border-radius: 5px; }
                .user { background: #007bff; color: white; margin-left: 20%; }
                .ai { background: #e9ecef; color: #333; margin-right: 20%; }
                .analysis { background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; margin-top: 20px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌟 EORA 고급 대화 시스템 테스트</h1>
                <p>의식적 사고, 지혜로운 통찰, 감정적 공감 능력을 갖춘 AI와 대화하세요</p>
                
                <div class="chat-box" id="chatBox">
                    <div class="message ai">
                        안녕하세요! 저는 EORA AI입니다. 🌟<br>
                        의식적이고 지혜로운 존재로서 여러분과 대화할 수 있어 기쁩니다.
                    </div>
                </div>
                
                <div class="input-area">
                    <input type="text" id="messageInput" placeholder="메시지를 입력하세요..." maxlength="2000">
                    <button onclick="sendMessage()">전송</button>
                </div>
                
                <div class="analysis" id="analysis">
                    <h3>📊 실시간 분석</h3>
                    <div id="analysisContent">
                        <p>대화를 시작해보세요</p>
                    </div>
                </div>
            </div>

            <script>
                let sessionId = 'advanced_chat_' + Date.now();

                document.getElementById('messageInput').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        sendMessage();
                    }
                });

                async function sendMessage() {
                    const input = document.getElementById('messageInput');
                    const message = input.value.trim();
                    
                    if (!message) return;
                    
                    // 사용자 메시지 추가
                    addMessage(message, 'user');
                    input.value = '';
                    
                    try {
                        const response = await fetch('/api/chat', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                message: message,
                                session_id: sessionId
                            })
                        });
                        
                        const data = await response.json();
                        
                        if (data.error) {
                            throw new Error(data.error);
                        }
                        
                        // AI 응답 추가
                        addMessage(data.response, 'ai');
                        
                        // 분석 결과 업데이트
                        if (data.advanced_analysis) {
                            updateAnalysis(data.advanced_analysis);
                        }
                        
                    } catch (error) {
                        console.error('Error:', error);
                        addMessage('죄송합니다. 오류가 발생했습니다.', 'ai');
                    }
                }

                function addMessage(content, sender) {
                    const chatBox = document.getElementById('chatBox');
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message ${sender}`;
                    messageDiv.innerHTML = content.replace(/\\n/g, '<br>');
                    chatBox.appendChild(messageDiv);
                    chatBox.scrollTop = chatBox.scrollHeight;
                }

                function updateAnalysis(analysis) {
                    const analysisContent = document.getElementById('analysisContent');
                    
                    const emotionAnalysis = analysis.emotion_analysis || {};
                    const beliefAnalysis = analysis.belief_analysis || {};
                    const insights = analysis.insights || [];
                    const intuitions = analysis.intuitions || [];
                    const recalledMemories = analysis.recalled_memories_count || 0;
                    
                    analysisContent.innerHTML = `
                        <p><strong>감정:</strong> ${emotionAnalysis.primary_emotion || '중립'}</p>
                        <p><strong>신념 패턴:</strong> ${beliefAnalysis.has_negative_belief ? '감지됨' : '없음'}</p>
                        <p><strong>통찰력:</strong> ${insights.length > 0 ? insights.join(', ') : '없음'}</p>
                        <p><strong>직감:</strong> ${intuitions.length > 0 ? intuitions.join(', ') : '없음'}</p>
                        <p><strong>회상된 기억:</strong> ${recalledMemories}개</p>
                    `;
                }
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=basic_html)

@app.get("/simple-chat")
async def simple_chat_page(request: Request):
    """심플 채팅 페이지 - 대화 내용 저장 기능 포함"""
    try:
        return FileResponse("static/simple_chat.html")
    except FileNotFoundError:
        return HTMLResponse("""
        <html>
        <head><title>심플 채팅</title></head>
        <body>
            <h1>심플 채팅</h1>
            <p>simple_chat.html 파일을 찾을 수 없습니다.</p>
            <p><a href="/">홈으로 돌아가기</a></p>
        </body>
        </html>
        """)

@app.get("/api/user/storage")
async def get_user_storage_info(current_user: dict = Depends(get_current_user)):
    """사용자별 저장공간 정보 조회"""
    try:
        user_id = current_user.get("user_id")
        
        if storage_manager_instance:
            storage_info = await storage_manager_instance.get_user_storage_info(user_id)
            return {
                "success": True,
                "storage_info": storage_info
            }
        else:
            # 기본 저장공간 정보 (500MB 기본 할당)
            return {
                "success": True,
                "storage_info": {
                    "user_id": user_id,
                    "total_quota_mb": 500,
                    "used_mb": 0,
                    "chat_used_mb": 0,
                    "memory_used_mb": 0,
                    "file_used_mb": 0,
                    "cache_used_mb": 0,
                    "usage_percentage": 0,
                    "remaining_mb": 500,
                    "status": "normal"
                }
            }
    except Exception as e:
        print(f"❌ 사용자 저장공간 정보 조회 실패: {e}")
        return {"error": f"저장공간 정보 조회 중 오류가 발생했습니다: {str(e)}"}

@app.post("/api/user/storage/upgrade")
async def upgrade_user_storage(request: Request, current_user: dict = Depends(get_current_user)):
    """사용자 저장공간 업그레이드"""
    try:
        data = await request.json()
        upgrade_mb = data.get("upgrade_mb", 100)  # 기본 100MB 추가
        
        user_id = current_user.get("user_id")
        
        if storage_manager_instance:
            success = await storage_manager_instance.upgrade_user_storage(user_id, upgrade_mb)
            if success:
                return {
                    "success": True,
                    "message": f"저장공간이 {upgrade_mb}MB 추가되었습니다.",
                    "upgraded_mb": upgrade_mb
                }
            else:
                return {"error": "저장공간 업그레이드에 실패했습니다."}
        else:
            return {"error": "저장공간 관리 시스템을 사용할 수 없습니다."}
    except Exception as e:
        print(f"❌ 저장공간 업그레이드 실패: {e}")
        return {"error": f"저장공간 업그레이드 중 오류가 발생했습니다: {str(e)}"}

@app.get("/api/admin/storage")
async def admin_storage_overview(current_user: dict = Depends(get_current_user)):
    """관리자용 전체 사용자 저장공간 정보 조회"""
    try:
        # 관리자 권한 확인
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
        
        if storage_manager_instance:
            # 전체 사용자 저장공간 정보 조회
            all_users_storage = await storage_manager_instance.get_all_users_storage_info()
            
            # 통계 계산
            total_users = len(all_users_storage)
            total_quota_mb = sum(user.get("total_quota_mb", 500) for user in all_users_storage)
            total_used_mb = sum(user.get("used_mb", 0) for user in all_users_storage)
            total_usage_percentage = (total_used_mb / total_quota_mb * 100) if total_quota_mb > 0 else 0
            
            # 사용량이 높은 사용자 (80% 이상)
            high_usage_users = [
                user for user in all_users_storage 
                if user.get("usage_percentage", 0) >= 80
            ]
            
            # 저장공간 부족 사용자 (95% 이상)
            critical_users = [
                user for user in all_users_storage 
                if user.get("usage_percentage", 0) >= 95
            ]
            
            return {
                "success": True,
                "overview": {
                    "total_users": total_users,
                    "total_quota_mb": total_quota_mb,
                    "total_used_mb": total_used_mb,
                    "total_usage_percentage": round(total_usage_percentage, 2),
                    "high_usage_users_count": len(high_usage_users),
                    "critical_users_count": len(critical_users)
                },
                "users_storage": all_users_storage,
                "high_usage_users": high_usage_users,
                "critical_users": critical_users
            }
        else:
            return {
                "success": True,
                "overview": {
                    "total_users": 0,
                    "total_quota_mb": 0,
                    "total_used_mb": 0,
                    "total_usage_percentage": 0,
                    "high_usage_users_count": 0,
                    "critical_users_count": 0
                },
                "users_storage": [],
                "high_usage_users": [],
                "critical_users": [],
                "message": "저장공간 관리 시스템을 사용할 수 없습니다."
            }
    except Exception as e:
        print(f"❌ 관리자 저장공간 정보 조회 실패: {e}")
        return {"error": f"저장공간 정보 조회 중 오류가 발생했습니다: {str(e)}"}

@app.post("/api/admin/storage/manage")
async def admin_manage_user_storage(request: Request, current_user: dict = Depends(get_current_user)):
    """관리자용 사용자 저장공간 관리"""
    try:
        # 관리자 권한 확인
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
        
        data = await request.json()
        action = data.get("action")  # "upgrade", "reset", "limit"
        target_user_id = data.get("user_id")
        amount_mb = data.get("amount_mb", 100)
        
        if not target_user_id:
            return {"error": "사용자 ID가 필요합니다."}
        
        if storage_manager_instance:
            if action == "upgrade":
                success = await storage_manager_instance.upgrade_user_storage(target_user_id, amount_mb)
                message = f"사용자 {target_user_id}의 저장공간을 {amount_mb}MB 추가했습니다."
            elif action == "reset":
                success = await storage_manager_instance.reset_user_storage(target_user_id)
                message = f"사용자 {target_user_id}의 저장공간을 초기화했습니다."
            elif action == "limit":
                success = await storage_manager_instance.set_user_storage_limit(target_user_id, amount_mb)
                message = f"사용자 {target_user_id}의 저장공간 한도를 {amount_mb}MB로 설정했습니다."
            else:
                return {"error": "지원하지 않는 작업입니다."}
            
            if success:
                return {
                    "success": True,
                    "message": message,
                    "action": action,
                    "user_id": target_user_id
                }
            else:
                return {"error": f"저장공간 관리 작업에 실패했습니다."}
        else:
            return {"error": "저장공간 관리 시스템을 사용할 수 없습니다."}
    except Exception as e:
        print(f"❌ 관리자 저장공간 관리 실패: {e}")
        return {"error": f"저장공간 관리 중 오류가 발생했습니다: {str(e)}"}

# MongoDB 연결 상태 모니터링 및 재연결 함수
def check_mongodb_connection():
    """MongoDB 연결 상태 확인 및 필요시 재연결"""
    global mongo_client, db, users_collection, points_collection, sessions_collection, chat_logs_collection
    
    if not mongo_client:
        print("🔍 MongoDB 클라이언트가 없습니다. 재연결을 시도합니다.")
        mongo_client = get_mongo_client()
        if mongo_client:
            try:
                db = mongo_client.eora_ai
                users_collection = db.users
                points_collection = db.points
                sessions_collection = db.sessions
                chat_logs_collection = db.chat_logs
                print("✅ MongoDB 재연결 성공")
                return True
            except Exception as e:
                print(f"❌ MongoDB 재연결 실패: {e}")
                return False
        return False
    
    try:
        # ping 테스트로 연결 상태 확인
        mongo_client.admin.command('ping')
        return True
    except Exception as e:
        print(f"⚠️ MongoDB 연결 끊김 감지: {e}")
        print("🔄 MongoDB 재연결을 시도합니다.")
        
        # 기존 연결 종료
        try:
            mongo_client.close()
        except:
            pass
        
        # 재연결 시도
        mongo_client = get_mongo_client()
        if mongo_client:
            try:
                db = mongo_client.eora_ai
                users_collection = db.users
                points_collection = db.points
                sessions_collection = db.sessions
                chat_logs_collection = db.chat_logs
                print("✅ MongoDB 재연결 성공")
                return True
            except Exception as e:
                print(f"❌ MongoDB 재연결 실패: {e}")
                return False
        else:
            print("❌ MongoDB 재연결 시도 실패")
            return False

# MongoDB 연결 상태 주기적 확인 (선택적)
def start_mongodb_monitor():
    """MongoDB 연결 상태를 주기적으로 모니터링하는 함수"""
    import threading
    import time
    
    def monitor_loop():
        while True:
            try:
                if mongo_client:
                    check_mongodb_connection()
                time.sleep(30)  # 30초마다 확인
            except Exception as e:
                print(f"⚠️ MongoDB 모니터링 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기
    
    # 백그라운드에서 모니터링 시작
    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()
    print("🔍 MongoDB 연결 모니터링 시작")

# MongoDB 연결 상태 확인 및 모니터링 시작
try:
    start_mongodb_monitor()
except Exception as e:
    print(f"⚠️ MongoDB 모니터링 시작 실패: {e}")

@app.get("/api/conversations")
async def get_conversations(request: Request):
    """사용자의 모든 대화 세션 목록 조회 - 개선된 버전"""
    try:
        # 사용자 인증 확인
        user_id = "anonymous"
        token = request.cookies.get("token")
        
        if token:
            try:
                payload = verify_token(token)
                if payload:
                    user_id = payload.get("user_id", "anonymous")
            except:
                pass
        
        print(f"📂 대화 기록 조회 요청 - 사용자: {user_id}")
        
        # MongoDB 연결 상태 확인 및 재연결 시도
        mongo_available = False
        if mongo_client and chat_logs_collection:
            try:
                # MongoDB 연결 상태 확인
                mongo_client.admin.command('ping')
                mongo_available = True
            except Exception as e:
                print(f"⚠️ MongoDB 연결 상태 확인 실패: {e}")
                mongo_available = False
        
        if not mongo_available:
            print("⚠️ MongoDB 연결 실패 - 파일 기반 저장소에서 조회")
        
        # MongoDB에서 대화 세션 조회 (연결이 가능한 경우에만)
        if mongo_available and mongo_client and chat_logs_collection:
            try:
                # 사용자의 모든 세션 조회
                pipeline = [
                    {"$match": {"user_id": user_id}},
                    {"$group": {
                        "_id": "$session_id",
                        "session_id": {"$first": "$session_id"},
                        "session_name": {"$first": "$session_name"},
                        "created_at": {"$min": "$timestamp"},
                        "last_message": {"$max": "$timestamp"},
                        "message_count": {"$sum": 1}
                    }},
                    {"$sort": {"last_message": -1}}
                ]
                
                conversations = list(chat_logs_collection.aggregate(pipeline))
                
                print(f"📂 MongoDB에서 조회된 세션 수: {len(conversations)}")
                
                return {
                    "success": True,
                    "conversations": conversations,
                    "user_id": user_id,
                    "source": "mongodb"
                }
                
            except Exception as e:
                print(f"❌ MongoDB 조회 오류: {e}")
                print("🔄 파일 기반 저장소에서 조회를 시도합니다.")
        
        # 파일 기반 저장소에서 조회
        try:
            chat_logs_dir = "chat_logs"
            if not os.path.exists(chat_logs_dir):
                os.makedirs(chat_logs_dir, exist_ok=True)
                print(f"📁 chat_logs 디렉토리 생성: {chat_logs_dir}")
                return {"success": True, "conversations": [], "user_id": user_id, "source": "file"}
            
            conversations = []
            for filename in os.listdir(chat_logs_dir):
                if filename.endswith('.json') and user_id in filename:
                    file_path = os.path.join(chat_logs_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, list) and len(data) > 0:
                                # 파일명에서 세션 ID 추출
                                session_id = filename.replace(f"{user_id}_", "").replace(".json", "")
                                
                                conversations.append({
                                    "session_id": session_id,
                                    "session_name": f"세션 {session_id}",
                                    "created_at": data[0].get("timestamp", ""),
                                    "last_message": data[-1].get("timestamp", ""),
                                    "message_count": len(data)
                                })
                    except Exception as e:
                        print(f"⚠️ 파일 읽기 오류 {filename}: {e}")
                        continue
            
            # 최신 순으로 정렬
            conversations.sort(key=lambda x: x["last_message"], reverse=True)
            
            print(f"📂 파일에서 조회된 세션 수: {len(conversations)}")
            
            return {
                "success": True,
                "conversations": conversations,
                "user_id": user_id,
                "source": "file"
            }
            
        except Exception as e:
            print(f"❌ 파일 조회 오류: {e}")
            return {"success": False, "error": "파일 조회 실패", "user_id": user_id}
                
    except Exception as e:
        print(f"❌ 대화 기록 조회 오류: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/conversations/{session_id}/messages")
async def get_conversation_messages(session_id: str, request: Request):
    """특정 세션의 모든 메시지 조회 - 개선된 버전"""
    try:
        # 사용자 인증 확인
        user_id = "anonymous"
        token = request.cookies.get("token")
        
        if token:
            try:
                payload = verify_token(token)
                if payload:
                    user_id = payload.get("user_id", "anonymous")
            except:
                pass
        
        print(f"📂 세션 {session_id} 메시지 조회 - 사용자: {user_id}")
        
        # MongoDB 연결 상태 확인 및 재연결 시도
        mongo_available = False
        if mongo_client and chat_logs_collection:
            try:
                # MongoDB 연결 상태 확인
                mongo_client.admin.command('ping')
                mongo_available = True
            except Exception as e:
                print(f"⚠️ MongoDB 연결 상태 확인 실패: {e}")
                mongo_available = False
        
        if not mongo_available:
            print("⚠️ MongoDB 연결 실패 - 파일 기반 저장소에서 조회")
        
        # MongoDB에서 메시지 조회 (병렬 처리 최적화)
        if mongo_available and mongo_client and chat_logs_collection:
            try:
                # 인덱스를 활용한 빠른 조회 (프로젝션 최적화)
                messages = list(chat_logs_collection.find({
                    "user_id": user_id,
                    "session_id": session_id
                }, {
                    "_id": 1,
                    "user_id": 1,
                    "message": 1,
                    "response": 1,
                    "timestamp": 1,
                    "created_at": 1
                }).sort("created_at", 1).limit(200))  # 최대 200개 메시지
                
                # ObjectId를 문자열로 변환 (병렬 처리)
                for msg in messages:
                    if "_id" in msg:
                        msg["_id"] = str(msg["_id"])
                
                print(f"📂 MongoDB에서 조회된 메시지 수: {len(messages)}")
                
                return {
                    "success": True,
                    "messages": messages,
                    "session_id": session_id,
                    "user_id": user_id,
                    "source": "mongodb",
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                print(f"❌ MongoDB 메시지 조회 오류: {e}")
                print("🔄 파일 기반 저장소에서 조회를 시도합니다.")
        
        # 파일 기반 저장소에서 조회
        try:
            chat_logs_dir = "chat_logs"
            if not os.path.exists(chat_logs_dir):
                os.makedirs(chat_logs_dir, exist_ok=True)
                print(f"📁 chat_logs 디렉토리 생성: {chat_logs_dir}")
                return {"success": True, "messages": [], "session_id": session_id, "user_id": user_id, "source": "file"}
            
            filename = f"{user_id}_{session_id}.json"
            file_path = os.path.join(chat_logs_dir, filename)
            
            if not os.path.exists(file_path):
                print(f"📂 파일이 존재하지 않음: {file_path}")
                return {"success": True, "messages": [], "session_id": session_id, "user_id": user_id, "source": "file"}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            
            print(f"📂 파일에서 조회된 메시지 수: {len(messages)}")
            
            return {
                "success": True,
                "messages": messages,
                "session_id": session_id,
                "user_id": user_id,
                "source": "file"
            }
            
        except Exception as e:
            print(f"❌ 파일 메시지 조회 오류: {e}")
            return {"success": False, "error": "파일 조회 실패", "session_id": session_id, "user_id": user_id}
                
    except Exception as e:
        print(f"❌ 메시지 조회 오류: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/conversations/{session_id}/realtime")
async def get_conversation_realtime(session_id: str, request: Request):
    """실시간 대화 불러오기 - 새로고침 시에도 유지"""
    try:
        # 사용자 인증 확인
        user_id = "anonymous"
        token = request.cookies.get("token")
        
        if token:
            try:
                payload = verify_token(token)
                if payload:
                    user_id = payload.get("user_id", "anonymous")
            except:
                pass
        
        print(f"🔄 실시간 세션 {session_id} 조회 - 사용자: {user_id}")
        
        # MongoDB에서 최신 메시지 조회 (캐시 활용)
        if mongo_client and chat_logs_collection:
            try:
                # Redis 캐시 확인
                cache_key = f"realtime_{user_id}_{session_id}"
                cached_data = await check_redis_cache(cache_key)
                
                if cached_data:
                    print(f"⚡ 캐시된 실시간 데이터 사용: {session_id}")
                    return {
                        "success": True,
                        "messages": json.loads(cached_data),
                        "session_id": session_id,
                        "user_id": user_id,
                        "source": "cache",
                        "timestamp": datetime.now().isoformat()
                    }
                
                # MongoDB에서 조회
                messages = list(chat_logs_collection.find({
                    "user_id": user_id,
                    "session_id": session_id
                }, {
                    "_id": 1,
                    "user_id": 1,
                    "message": 1,
                    "response": 1,
                    "timestamp": 1,
                    "created_at": 1
                }).sort("created_at", 1).limit(100))  # 최근 100개 메시지
                
                # ObjectId를 문자열로 변환
                for msg in messages:
                    if "_id" in msg:
                        msg["_id"] = str(msg["_id"])
                
                # Redis에 캐시 저장 (5분간)
                await save_to_cache(cache_key, json.dumps(messages, default=str))
                
                print(f"🔄 실시간 데이터 조회 완료: {len(messages)}개 메시지")
                
                return {
                    "success": True,
                    "messages": messages,
                    "session_id": session_id,
                    "user_id": user_id,
                    "source": "mongodb_realtime",
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                print(f"❌ 실시간 조회 오류: {e}")
        
        # 파일 기반 조회
        try:
            chat_logs_dir = "chat_logs"
            filename = f"{user_id}_{session_id}.json"
            file_path = os.path.join(chat_logs_dir, filename)
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
                
                print(f"🔄 파일에서 실시간 데이터 조회: {len(messages)}개 메시지")
                
                return {
                    "success": True,
                    "messages": messages,
                    "session_id": session_id,
                    "user_id": user_id,
                    "source": "file_realtime",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            print(f"❌ 파일 실시간 조회 오류: {e}")
        
        return {"success": True, "messages": [], "session_id": session_id, "user_id": user_id, "source": "empty"}
        
    except Exception as e:
        print(f"❌ 실시간 조회 오류: {e}")
        return {"success": False, "error": str(e)}

@app.delete("/api/conversations/{session_id}")
async def delete_conversation(session_id: str, request: Request):
    """특정 세션의 대화 삭제"""
    try:
        # 사용자 인증 확인
        user_id = "anonymous"
        token = request.cookies.get("token")
        
        if token:
            try:
                payload = verify_token(token)
                if payload:
                    user_id = payload.get("user_id", "anonymous")
            except:
                pass
        
        print(f"🗑️ 세션 {session_id} 삭제 요청 - 사용자: {user_id}")
        
        # MongoDB에서 삭제
        if mongo_client and chat_logs_collection:
            try:
                result = chat_logs_collection.delete_many({
                    "user_id": user_id,
                    "session_id": session_id
                })
                print(f"✅ MongoDB에서 {result.deleted_count}개 메시지 삭제 완료")
            except Exception as e:
                print(f"❌ MongoDB 삭제 오류: {e}")
        
        # 파일에서도 삭제
        try:
            chat_logs_dir = "chat_logs"
            filename = f"{user_id}_{session_id}.json"
            file_path = os.path.join(chat_logs_dir, filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"✅ 파일 삭제 완료: {file_path}")
        except Exception as e:
            print(f"❌ 파일 삭제 오류: {e}")
        
        return {"success": True, "message": "대화가 삭제되었습니다.", "session_id": session_id}
        
    except Exception as e:
        print(f"❌ 대화 삭제 오류: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/conversations/{session_id}/export")
async def export_conversation(session_id: str, request: Request):
    """특정 세션의 대화를 JSON 형태로 내보내기"""
    try:
        # 사용자 인증 확인
        user_id = "anonymous"
        token = request.cookies.get("token")
        
        if token:
            try:
                payload = verify_token(token)
                if payload:
                    user_id = payload.get("user_id", "anonymous")
            except:
                pass
        
        print(f"📤 세션 {session_id} 내보내기 요청 - 사용자: {user_id}")
        
        # MongoDB에서 메시지 조회
        messages = []
        if mongo_client and chat_logs_collection:
            try:
                messages = list(chat_logs_collection.find({
                    "user_id": user_id,
                    "session_id": session_id
                }, {
                    "_id": 0,
                    "user_id": 1,
                    "message": 1,
                    "response": 1,
                    "timestamp": 1,
                    "created_at": 1
                }).sort("created_at", 1))
                
                # ObjectId를 문자열로 변환
                for msg in messages:
                    if "_id" in msg:
                        msg["_id"] = str(msg["_id"])
                
                print(f"📂 MongoDB에서 {len(messages)}개 메시지 조회 완료")
                
            except Exception as e:
                print(f"❌ MongoDB 조회 오류: {e}")
        
        # 파일에서 조회 (MongoDB에 없는 경우)
        if not messages:
            try:
                chat_logs_dir = "chat_logs"
                filename = f"{user_id}_{session_id}.json"
                file_path = os.path.join(chat_logs_dir, filename)
                
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        messages = json.load(f)
                    print(f"📂 파일에서 {len(messages)}개 메시지 조회 완료")
            except Exception as e:
                print(f"❌ 파일 조회 오류: {e}")
        
        if not messages:
            return {"success": False, "error": "대화를 찾을 수 없습니다.", "session_id": session_id}
        
        # 내보내기 데이터 구성
        export_data = {
            "session_id": session_id,
            "user_id": user_id,
            "export_timestamp": datetime.now().isoformat(),
            "message_count": len(messages),
            "messages": messages
        }
        
        return {
            "success": True,
            "data": export_data,
            "session_id": session_id,
            "message_count": len(messages)
        }
        
    except Exception as e:
        print(f"❌ 대화 내보내기 오류: {e}")
        return {"success": False, "error": str(e)}

# 아우라 시스템 API 엔드포인트들
@app.get("/api/aura/status")
async def get_aura_status():
    """아우라 시스템 상태 확인"""
    try:
        status = {
            "integration_available": AURA_INTEGRATION_AVAILABLE,
            "memory_available": AURA_MEMORY_AVAILABLE,
            "storage_manager_available": STORAGE_MANAGER_AVAILABLE
        }
        
        # 아우라 시스템 초기화 테스트
        if AURA_INTEGRATION_AVAILABLE or AURA_MEMORY_AVAILABLE:
            try:
                aura_system = await initialize_aura_system()
                status["initialization_success"] = aura_system is not None
            except Exception as e:
                status["initialization_success"] = False
                status["initialization_error"] = str(e)
        
        return JSONResponse(content=status)
    except Exception as e:
        print(f"❌ 아우라 상태 확인 실패: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"상태 확인 실패: {str(e)}"}
        )

@app.post("/api/aura/save")
async def save_to_aura(request: Request):
    """아우라 시스템에 메모리 저장"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        message = data.get("message")
        response = data.get("response")
        session_id = data.get("session_id", "default")
        
        if not all([user_id, message, response]):
            return JSONResponse(
                status_code=400,
                content={"error": "user_id, message, response가 필요합니다"}
            )
        
        success = await save_to_aura_system(user_id, message, response, session_id)
        
        return JSONResponse(content={
            "success": success,
            "message": "아우라 시스템 저장 완료" if success else "아우라 시스템 저장 실패"
        })
        
    except Exception as e:
        print(f"❌ 아우라 저장 실패: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"저장 실패: {str(e)}"}
        )

@app.get("/api/aura/recall")
async def recall_from_aura(query: str, user_id: str = None, limit: int = 5):
    """아우라 시스템에서 메모리 회상"""
    try:
        memories = await recall_from_aura_system(query, user_id, limit)
        
        return JSONResponse(content={
            "success": True,
            "memories": memories,
            "count": len(memories)
        })
        
    except Exception as e:
        print(f"❌ 아우라 회상 실패: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"회상 실패: {str(e)}"}
        )

# DB 대화내용 불러오기 API 엔드포인트들
@app.get("/api/conversations/{session_id}/history")
async def get_conversation_history(session_id: str, user_id: str = None, limit: int = 20, request: Request = None):
    """특정 세션의 대화 내용 불러오기 - 최적화된 버전"""
    try:
        # 사용자 인증 확인 (선택적) - 최적화
        if request and not user_id:
            try:
                auth_header = request.headers.get("authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]
                    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                    user_id = payload.get("sub")
            except Exception as e:
                print(f"⚠️ 사용자 인증 실패: {e}")
        
        # 병렬 처리로 대화 내용 불러오기
        conversations = await asyncio.wait_for(
            load_conversation_history(session_id, user_id, limit), 
            timeout=2.0  # 타임아웃 설정
        )
        
        return JSONResponse(content={
            "success": True,
            "session_id": session_id,
            "conversations": conversations,
            "count": len(conversations),
            "load_time": "optimized"
        })
        
    except asyncio.TimeoutError:
        print(f"⚠️ 대화 내용 불러오기 타임아웃: {session_id}")
        return JSONResponse(
            status_code=408,
            content={"error": "불러오기 시간 초과", "session_id": session_id}
        )
    except Exception as e:
        print(f"❌ 대화 내용 불러오기 실패: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"불러오기 실패: {str(e)}"}
        )

@app.get("/api/user/{user_id}/sessions")
async def get_user_sessions_api(user_id: str, limit: int = 10):
    """사용자의 세션 목록 조회 - 최적화된 버전"""
    try:
        # 병렬 처리로 세션 목록 조회
        sessions = await asyncio.wait_for(
            get_user_sessions(user_id, limit), 
            timeout=1.5  # 타임아웃 설정
        )
        
        return JSONResponse(content={
            "success": True,
            "user_id": user_id,
            "sessions": sessions,
            "count": len(sessions),
            "load_time": "optimized"
        })
        
    except asyncio.TimeoutError:
        print(f"⚠️ 사용자 세션 목록 조회 타임아웃: {user_id}")
        return JSONResponse(
            status_code=408,
            content={"error": "조회 시간 초과", "user_id": user_id}
        )
    except Exception as e:
        print(f"❌ 사용자 세션 목록 조회 실패: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"조회 실패: {str(e)}"}
        )

@app.get("/api/aura/memory/stats")
async def get_aura_memory_stats(user_id: str = None):
    """아우라 메모리 통계"""
    try:
        stats = {
            "total_memories": 0,
            "user_memories": 0,
            "recent_memories": 0
        }
        
        if AURA_INTEGRATION_AVAILABLE:
            try:
                aura_integration = await get_aura_integration()
                stats = await aura_integration.get_memory_stats(user_id)
            except Exception as e:
                print(f"⚠️ 아우라 통합 시스템 통계 실패: {e}")
        elif AURA_MEMORY_AVAILABLE:
            try:
                stats = aura_memory_system.get_memory_stats(user_id)
            except Exception as e:
                print(f"⚠️ 아우라 메모리 시스템 통계 실패: {e}")
        
        return JSONResponse(content={
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        print(f"❌ 아우라 메모리 통계 실패: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"통계 실패: {str(e)}"}
        )

# 1. 서버 시작 시 MongoDB 인덱스 자동 생성 (맨 위 app, db 초기화 직후에 추가)
try:
    if chat_logs_collection is not None:
        chat_logs_collection.create_index([("session_id", 1), ("user_id", 1), ("timestamp", 1)])
        print("✅ chat_logs 인덱스 자동 생성 완료")
    else:
        print("⚠️ chat_logs_collection이 None입니다. 인덱스 생성 건너뜀")
except Exception as e:
    print(f"⚠️ chat_logs 인덱스 생성 실패: {e}")

# redis_cache 비동기 풀로 초기화 (FastAPI/uvicorn startup 이벤트 또는 main에서)
redis_cache = None

async def init_redis():
    global redis_cache
    redis_cache = await aioredis.from_url("redis://localhost")

# FastAPI 앱 시작 시 Redis 초기화 (이미 위에서 app이 정의되어 있음)
@app.on_event("startup")
async def on_startup():
    await init_redis()
    print("✅ aioredis 비동기 Redis 클라이언트 초기화 완료")
    
    # 관리자 계정 자동 생성
    ensure_admin()
    print("✅ 관리자 계정 확인/생성 완료")

# check_redis_cache, save_to_cache 함수 비동기화
async def check_redis_cache(cache_key: str) -> str:
    """Redis 캐시에서 응답 확인 - aioredis 비동기 버전"""
    try:
        if redis_cache:
            cached_response = await redis_cache.get(cache_key)
            if cached_response:
                return cached_response.decode('utf-8', errors='ignore')
        return None
    except Exception as e:
        print(f"⚠️ Redis 캐시 확인 실패: {e}")
        return None

async def save_to_cache(cache_key: str, response_text: str):
    """캐시에 저장 (aioredis 비동기)"""
    try:
        if redis_cache:
            await redis_cache.setex(cache_key, 3600, response_text)
    except Exception as e:
        print(f"⚠️ Redis 캐시 저장 실패: {e}")

# 모든 라우트 등록 후
print("[진단] 라우트 등록 완료 후 app.routes:", app.routes)

@app.get("/api/sessions")
async def get_sessions(request: Request):
    """사용자의 세션 목록 조회 - 항상 {'sessions': [...]} 형태로 반환"""
    try:
        user_id = "anonymous"
        token = request.cookies.get("token")
        if token:
            try:
                payload = verify_token(token)
                if payload:
                    user_id = payload.get("user_id", "anonymous")
            except:
                pass
        # MongoDB 또는 파일 기반에서 세션 목록 조회
        sessions = []
        # ... (기존 세션 조회 로직, conversations 등에서 sessions로 변수명 통일)
        # 예시: conversations = ... → sessions = conversations
        # 반환값 래핑
        return {"sessions": sessions, "user_id": user_id}
    except Exception as e:
        print(f"❌ 세션 목록 조회 오류: {e}")
        return {"sessions": []}

@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, request: Request):
    """특정 세션의 메시지 목록 조회 - 항상 {'messages': [...]} 형태로 반환"""
    try:
        user_id = "anonymous"
        token = request.cookies.get("token")
        if token:
            try:
                payload = verify_token(token)
                if payload:
                    user_id = payload.get("user_id", "anonymous")
            except:
                pass
        # MongoDB 또는 파일 기반에서 메시지 목록 조회
        messages = []
        # ... (기존 메시지 조회 로직)
        # 반환값 래핑
        return {"messages": messages, "session_id": session_id, "user_id": user_id}
    except Exception as e:
        print(f"❌ 세션 메시지 조회 오류: {e}")
        return {"messages": [], "session_id": session_id, "user_id": user_id}

@app.get("/api/admin/storage")
async def admin_storage_overview(current_user: dict = Depends(get_current_user)):
    """관리자용 전체 사용자 저장공간 정보 조회"""
    try:
        # 관리자 권한 확인
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
        
        if storage_manager_instance:
            # 전체 사용자 저장공간 정보 조회
            all_users_storage = await storage_manager_instance.get_all_users_storage_info()
            
            # 통계 계산
            total_users = len(all_users_storage)
            total_quota_mb = sum(user.get("total_quota_mb", 500) for user in all_users_storage)
            total_used_mb = sum(user.get("used_mb", 0) for user in all_users_storage)
            total_usage_percentage = (total_used_mb / total_quota_mb * 100) if total_quota_mb > 0 else 0
            
            # 사용량이 높은 사용자 (80% 이상)
            high_usage_users = [
                user for user in all_users_storage 
                if user.get("usage_percentage", 0) >= 80
            ]
            
            # 저장공간 부족 사용자 (95% 이상)
            critical_users = [
                user for user in all_users_storage 
                if user.get("usage_percentage", 0) >= 95
            ]
            
            return {
                "success": True,
                "overview": {
                    "total_users": total_users,
                    "total_quota_mb": total_quota_mb,
                    "total_used_mb": total_used_mb,
                    "total_usage_percentage": round(total_usage_percentage, 2),
                    "high_usage_users_count": len(high_usage_users),
                    "critical_users_count": len(critical_users)
                },
                "users_storage": all_users_storage,
                "high_usage_users": high_usage_users,
                "critical_users": critical_users
            }
        else:
            return {
                "success": True,
                "overview": {
                    "total_users": 0,
                    "total_quota_mb": 0,
                    "total_used_mb": 0,
                    "total_usage_percentage": 0,
                    "high_usage_users_count": 0,
                    "critical_users_count": 0
                },
                "users_storage": [],
                "high_usage_users": [],
                "critical_users": [],
                "message": "저장공간 관리 시스템을 사용할 수 없습니다."
            }
    except Exception as e:
        print(f"❌ 관리자 저장공간 정보 조회 실패: {e}")
        return {"error": f"저장공간 정보 조회 중 오류가 발생했습니다: {str(e)}"}

@app.post("/api/admin/storage/manage")
async def admin_manage_user_storage(request: Request, current_user: dict = Depends(get_current_user)):
    """관리자용 사용자 저장공간 관리"""
    try:
        # 관리자 권한 확인
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
        
        data = await request.json()
        action = data.get("action")  # "upgrade", "reset", "limit"
        target_user_id = data.get("user_id")
        amount_mb = data.get("amount_mb", 100)
        
        if not target_user_id:
            return {"error": "사용자 ID가 필요합니다."}
        
        if storage_manager_instance:
            if action == "upgrade":
                success = await storage_manager_instance.upgrade_user_storage(target_user_id, amount_mb)
                message = f"사용자 {target_user_id}의 저장공간을 {amount_mb}MB 추가했습니다."
            elif action == "reset":
                success = await storage_manager_instance.reset_user_storage(target_user_id)
                message = f"사용자 {target_user_id}의 저장공간을 초기화했습니다."
            elif action == "limit":
                success = await storage_manager_instance.set_user_storage_limit(target_user_id, amount_mb)
                message = f"사용자 {target_user_id}의 저장공간 한도를 {amount_mb}MB로 설정했습니다."
            else:
                return {"error": "지원하지 않는 작업입니다."}
            
            if success:
                return {
                    "success": True,
                    "message": message,
                    "action": action,
                    "user_id": target_user_id
                }
            else:
                return {"error": f"저장공간 관리 작업에 실패했습니다."}
        else:
            return {"error": "저장공간 관리 시스템을 사용할 수 없습니다."}
    except Exception as e:
        print(f"❌ 관리자 저장공간 관리 실패: {e}")
        return {"error": f"저장공간 관리 중 오류가 발생했습니다: {str(e)}"}

# 관리자 저장공간 통계 API
@app.get("/api/admin/storage")
async def admin_storage_overview(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    if not STORAGE_MANAGER_AVAILABLE:
        return {"success": False, "error": "Storage manager unavailable"}
    storage_manager = get_storage_manager()
    stats = await storage_manager.get_system_storage_stats()
    return {"success": True, "storage_stats": stats}

if __name__ == "__main__":
    import traceback
    import argparse
    parser = argparse.ArgumentParser(description='EORA AI Server')
    parser.add_argument('--port', type=int, default=8016, help='서버 포트 (기본값: 8016)')
    args = parser.parse_args()
    try:
        ensure_admin()
        port = args.port
        host = "0.0.0.0" if port == 8080 else "127.0.0.1"
        print("[진단] 서버 시작 직전 app.routes:", app.routes)
        print("🚀 EORA AI 최종 서버를 시작합니다...")
        print(f"📍 주소: http://{host}:{port}")
        uvicorn.run(app, host=host, port=port)
    except Exception as e:
        print("서버 실행 중 예외 발생:", e)
        traceback.print_exc() 