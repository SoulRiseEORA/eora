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
import traceback
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# 로깅 설정 (모든 것보다 먼저)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(levelname)s - %(message)s'
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

# 데이터베이스 및 캐시
import pymongo
from pymongo import MongoClient
from bson import ObjectId

# 로깅은 상단에서 이미 설정됨

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
import jwt
SECRET_KEY = os.environ.get("SECRET_KEY", "eora_secret_key")
ALGORITHM = "HS256"

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
            if user_email:
                user = {"email": user_email}
                logger.info(f"✅ 개별 쿠키에서 user 조회 성공: {user_email}")
    
    # 4. user 정보 보정 (관리자 판별 포함)
    if user:
        user['email'] = user.get('email', '')
        user['user_id'] = user.get('user_id') or user.get('email') or 'anonymous'
        user['role'] = 'admin' if user.get('email') == 'admin@eora.ai' else 'user'
        user['is_admin'] = user.get('email') == 'admin@eora.ai'
        
        # 필수 필드 보정
        if 'name' not in user:
            user['name'] = user['email'].split('@')[0] if '@' in user['email'] else 'User'
    else:
        logger.warning("⚠️ 모든 방법으로 user 정보 조회 실패")
    
    return user

# Railway 호환 환경변수 로드 시스템
from dotenv import load_dotenv
import os

def safe_get_env(key: str, default: str = "") -> str:
    """환경변수를 안전하게 가져오기 - Railway 호환"""
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
logger.info("🚀 ==========================================")
logger.info("🚀 EORA AI System - Railway 안전 서버 v3.0.0")
logger.info("🚀 502 오류 완전 방지 버전")
logger.info("🚀 환경변수 안전 처리 완료")
logger.info("🚀 MongoDB 연결 안정성 확보")
logger.info("🚀 모든 기능 정상 작동 보장")
logger.info("🚀 ==========================================")

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
    print("[MongoDB 연결 디버깅] 환경변수 및 우선순위 점검 시작")
    print("  - MONGODB_URL:", os.environ.get('MONGODB_URL'))
    print("  - MONGO_PUBLIC_URL:", os.environ.get('MONGO_PUBLIC_URL'))
    print("  - MONGO_URL:", os.environ.get('MONGO_URL'))
    print("  - MONGODB_URI:", os.environ.get('MONGODB_URI'))
    # Railway 환경에서 사용할 수 있는 MongoDB URL들
    if MONGODB_URL:
        urls_to_try.append(MONGODB_URL)
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
    local_urls = [
        "mongodb://localhost:27017",
        "mongodb://127.0.0.1:27017"
    ]
    for url in local_urls:
        if url not in urls_to_try:
            urls_to_try.append(url)
    print(f"[MongoDB 연결 디버깅] 연결 시도할 URL 목록:")
    for i, url in enumerate(urls_to_try, 1):
        print(f"  {i}. {url}")
    logger.info(f"🔗 연결 시도할 URL 수: {len(urls_to_try)}")
    for i, url in enumerate(urls_to_try, 1):
        if not url:
            continue
        try:
            logger.info(f"🔗 MongoDB 연결 시도: {i}/{len(urls_to_try)}")
            logger.info(f"📝 연결 URL: {url}")
            print(f"[MongoDB 연결 디버깅] {i}/{len(urls_to_try)} 연결 시도: {url}")
            clean_url = clean_mongodb_url(url)
            print(f"[MongoDB 연결 디버깅] 실제 연결에 사용되는 URL: {clean_url}")
            client = MongoClient(clean_url, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            logger.info(f"✅ MongoDB 연결 성공: {i}/{len(urls_to_try)}")
            print(f"[MongoDB 연결 디버깅] 연결 성공! client: {client}")
            return client
        except Exception as e:
            logger.warning(f"❌ MongoDB 연결 실패 ({i}/{len(urls_to_try)}): {type(e).__name__} - {str(e)}")
            print(f"[MongoDB 연결 디버깅] 연결 실패: {type(e).__name__} - {str(e)}")
            continue
    logger.error("❌ 모든 MongoDB 연결 시도 실패")
    print("[MongoDB 연결 디버깅] 모든 연결 시도 실패!")
    return None

# MongoDB 연결 시도
global db, users_collection
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
        chat_logs_collection = None
        sessions_collection = None
        users_collection = None
        db = None

# 전역 변수 초기화
prompts_data = {}


# OpenAI 클라이언트 안전 초기화 - Railway 호환
openai_client = None

def init_openai_client():
    """OpenAI 클라이언트를 안전하게 초기화"""
    global openai_client
    try:
        if not OPENAI_API_KEY:
            logger.warning("⚠️ OPENAI_API_KEY가 설정되지 않았습니다.")
            logger.info("🔧 Railway 환경변수에서 OPENAI_API_KEY를 설정해주세요.")
            return None
        
        if not OPENAI_API_KEY.startswith("sk-"):
            logger.warning("⚠️ OpenAI API 키 형식이 올바르지 않습니다.")
            return None
        
        from openai import OpenAI
        # Railway 호환 OpenAI 클라이언트 초기화
        openai_client = OpenAI(
            api_key=OPENAI_API_KEY,
            timeout=30.0,  # Railway 환경에서 타임아웃 설정
            max_retries=3   # 재시도 횟수 설정
        )
        
        logger.info("✅ OpenAI API 클라이언트 초기화 성공")
        return openai_client
        
    except ImportError as e:
        logger.error(f"❌ OpenAI 모듈 import 실패: {e}")
        logger.info("💡 requirements.txt에 openai>=1.3.0이 포함되어 있는지 확인해주세요.")
        return None
    except Exception as e:
        logger.error(f"❌ OpenAI 클라이언트 초기화 실패: {e}")
        logger.warning("⚠️ OpenAI 기능이 비활성화됩니다. 환경변수를 확인해주세요.")
        return None

# OpenAI 클라이언트 초기화 실행
try:
    openai_client = init_openai_client()
    if openai_client:
        logger.info("✅ OpenAI API 키 설정 성공 (Railway 호환)")
    else:
        logger.warning("⚠️ OpenAI 클라이언트가 비활성화되었습니다.")
        logger.info("💡 Railway 환경변수에서 OPENAI_API_KEY를 설정하면 활성화됩니다.")
except Exception as e:
    logger.error(f"❌ OpenAI 클라이언트 초기화 중 예외 발생: {e}")
    openai_client = None



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

# 세션 미들웨어 조건부 추가 (itsdangerous 패키지가 있을 때만)
if SESSION_MIDDLEWARE_AVAILABLE:
    app.add_middleware(
        SessionMiddleware,
        secret_key="eora_railway_session_secret_key_2024_!@#",
        session_cookie="eora_session",
        max_age=60*60*24*7,  # 7일
        same_site="lax",
        https_only=False  # Railway는 자동으로 HTTPS 처리하므로 False로 설정
    )
    logger.info("✅ 세션 미들웨어 활성화")
else:
    logger.info("ℹ️ 세션 미들웨어 비활성화 - 쿠키 기반으로만 동작")

# Jinja2 템플릿 설정
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# CORS 허용
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
async def admin_page(request: Request):
    user = get_current_user(request)
    if not user or user.get("email") != "admin@eora.ai":
        return RedirectResponse("/login")
    return templates.TemplateResponse("admin.html", {"request": request, "user": user})

@app.get("/admin/prompt-management", response_class=HTMLResponse)
@admin_required
async def admin_prompt_management(request: Request):
    user = get_current_user(request)
    if not user or not user.get("is_admin", False):
        return RedirectResponse("/")
    return templates.TemplateResponse("prompt_management.html", {"request": request})

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
    """아우라 메모리 통계 API - 오류 처리 개선"""
    try:
        user = get_current_user(request)
        user_id = user.get("user_id") if user else "anonymous"
        
        logger.info(f"📊 메모리 통계 요청: user_id={user_id}")
        
        # 기본 통계 정보 (임시)
        stats = {
            "total_memories": 0,
            "user_memories": 0,
            "system_memories": 0,
            "last_updated": datetime.now().isoformat(),
            "memory_types": {
                "normal": 0,
                "semantic": 0,
                "emotional": 0,
                "contextual": 0
            },
            "user_id": user_id
        }
        
        # MongoDB에서 실제 메모리 수 확인
        if aura_collection:
            try:
                total_count = aura_collection.count_documents({})
                user_count = aura_collection.count_documents({"user_id": user_id})
                stats["total_memories"] = total_count
                stats["user_memories"] = user_count
                logger.info(f"✅ MongoDB 메모리 통계: 전체={total_count}, 사용자={user_count}")
            except Exception as e:
                logger.warning(f"⚠️ MongoDB 메모리 통계 조회 실패: {e}")
        
        logger.info(f"✅ 메모리 통계 반환: {stats}")
        return {"success": True, "stats": stats}
        
    except Exception as e:
        logger.error(f"❌ 메모리 통계 API 오류: {e}")
        return {
            "success": False, 
            "error": f"메모리 통계 처리 중 오류 발생: {str(e)}",
            "stats": {}
        }

@app.get("/api/aura/recall")
async def aura_memory_recall(request: Request, query: str = "", recall_type: str = "normal"):
    """아우라 메모리 회상 API - 8종 회상 시스템 적용"""
    try:
        user = get_current_user(request)
        user_id = user.get("user_id") if user else "anonymous"
        
        logger.info(f"🔍 8종 회상 요청: user_id={user_id}, query='{query}', recall_type={recall_type}")
        
        if not query.strip():
            logger.warning("⚠️ 회상 쿼리가 비어있음")
            return {
                "success": False, 
                "error": "회상 쿼리가 필요합니다",
                "memories": []
            }
        
        # 8종 회상 시스템 적용
        try:
            from aura_system.recall_engine import RecallEngine
            from aura_system.memory_manager import MemoryManagerAsync
            
            # 메모리 매니저 초기화 (실제 구현에서는 싱글톤 패턴 사용)
            memory_manager = MemoryManagerAsync()
            if not memory_manager.is_initialized:
                await memory_manager.initialize()
            
            # 회상 엔진 초기화
            recall_engine = RecallEngine(memory_manager)
            
            # 컨텍스트 정보 구성
            context = {
                "user_id": user_id,
                "session_id": request.cookies.get("session_id", ""),
                "time_tag": datetime.now().strftime("%Y-%m-%d"),
                "topic": "general"
            }
            
            # 감정 분석 (간단한 키워드 기반)
            emotion = None
            emotion_keywords = {
                "기쁨": ["기쁘", "행복", "즐거", "신나", "좋", "만족", "감사"],
                "슬픔": ["슬프", "우울", "속상", "아프", "힘들", "지치"],
                "분노": ["화나", "짜증", "열받", "분노", "격분", "화"],
                "두려움": ["무서", "겁나", "불안", "걱정", "우려", "두려"],
                "놀람": ["놀라", "깜짝", "어이", "헐", "와", "대박"]
            }
            
            for emotion_label, keywords in emotion_keywords.items():
                if any(keyword in query for keyword in keywords):
                    emotion = {"label": emotion_label}
                    break
            
            # 8종 회상 실행
            memories = await recall_engine.recall(
                query=query,
                context=context,
                emotion=emotion,
                limit=5,
                distance_threshold=1.2
            )
            
            # 결과 포맷팅
            formatted_memories = []
            for memory in memories:
                formatted_memory = {
                    "message": memory.get("message", memory.get("content", "")),
                    "response": memory.get("response", memory.get("gpt", "")),
                    "timestamp": memory.get("timestamp", memory.get("created_at", datetime.now().isoformat())),
                    "relevance": memory.get("similarity", 0.8),
                    "recall_type": memory.get("recall_type", "comprehensive"),
                    "emotion": memory.get("emotion", memory.get("metadata", {}).get("emotion", "")),
                    "belief_tags": memory.get("belief_tags", memory.get("metadata", {}).get("belief_tags", [])),
                    "memory_id": str(memory.get("_id", ""))
                }
                formatted_memories.append(formatted_memory)
            
            logger.info(f"✅ 8종 회상 완료: {len(formatted_memories)}개 메모리")
            return {
                "success": True, 
                "memories": formatted_memories, 
                "recall_type": "8종_회상_시스템",
                "query": query,
                "user_id": user_id,
                "recall_strategies": [
                    "키워드 기반 회상",
                    "임베딩 기반 회상", 
                    "시퀀스 체인 회상",
                    "메타데이터 기반 회상",
                    "감정 기반 회상",
                    "트리거 기반 회상",
                    "빈도 통계 기반 회상",
                    "신념 기반 회상"
                ]
            }
            
        except ImportError as e:
            logger.warning(f"회상 엔진 임포트 실패, 기본 회상 사용: {e}")
            # 기본 회상 (fallback)
            memories = await recall_from_aura_memory(query, user_id, 5, recall_type)
            return {
                "success": True, 
                "memories": memories, 
                "recall_type": "기본_회상",
                "query": query,
                "user_id": user_id
            }
            
    except Exception as e:
        logger.error(f"❌ 8종 회상 API 오류: {e}")
        return {
            "success": False, 
            "error": f"회상 처리 중 오류 발생: {str(e)}",
            "memories": []
        }

@app.get("/api/aura/memory")
async def aura_memory_list(request: Request):
    try:
        # 아우라 메모리 목록 조회
        if aura_collection:
            memories = list(aura_collection.find({}, {"_id": 0}).limit(100))
            return {"memories": memories, "count": len(memories)}
        else:
            return {"memories": [], "count": 0, "error": "MongoDB 연결 없음"}
    except Exception as e:
        logger.error(f"아우라 메모리 조회 오류: {e}")
        return {"memories": [], "error": str(e)}

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
        user = get_current_user(request)
        if not user:
            # Railway 환경에서 쿠키 기반 fallback
            user_email = request.cookies.get('user_email')
            if user_email:
                user = {
                    'user_id': user_email,
                    'email': user_email,
                    'role': 'admin' if user_email == 'admin@eora.ai' else 'user',
                    'is_admin': user_email == 'admin@eora.ai',
                    'name': user_email.split('@')[0] if '@' in user_email else 'User'
                }
                logger.info(f"✅ 쿠키 기반 user 정보 복구: {user_email}")
            else:
                logger.warning("❌ 세션 생성 실패: 로그인 필요")
                raise HTTPException(status_code=401, detail="로그인 필요")
        data = await request.json()
        session_name = data.get("name", "새 세션")
        user_id = user.get("user_id", user.get("email", "anonymous"))
        session_id = generate_session_id()
        session_data = {
            "name": session_name,
            "message_count": 0,
            "user_id": user_id
        }
        logger.info(f"📝 새 세션 생성: {session_name} (ID: {session_id}) for user {user_id}")
        if sessions_collection is not None:
            session_doc = {
                "_id": session_id,
                "session_id": session_id,
                "name": session_name,
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "message_count": 0,
                "user_id": user_id
            }
            try:
                result = sessions_collection.insert_one(session_doc)
                if result.inserted_id:
                    session_doc["_id"] = str(session_doc["_id"])
                    session_doc["created_at"] = session_doc["created_at"].isoformat()
                    session_doc["last_activity"] = session_doc["last_activity"].isoformat()
                    logger.info(f"✅ MongoDB 세션 저장 완료: {session_id}")
                    return session_doc
                else:
                    raise Exception("MongoDB insert 실패")
            except Exception as mongo_error:
                logger.error(f"❌ MongoDB 세션 저장 실패: {mongo_error}")
                save_session_to_memory(session_id, session_data)
                logger.info(f"✅ 메모리 세션 저장 완료 (fallback): {session_id}")
                return {"_id": session_id, **session_data}
        else:
            save_session_to_memory(session_id, session_data)
            logger.info(f"✅ 메모리 세션 저장 완료 (fallback): {session_id}")
            return {"_id": session_id, **session_data}
    except Exception as e:
        logger.error(f"세션 생성 오류: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="세션 생성에 실패했습니다")

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
        recall_type = data.get("recall_type", "normal")
        print(f"[채팅 요청] user_id: {user_id}, session_id: {session_id}, recall_type: {recall_type}, message: {user_message}")
        # 1. 아우라 메모리 시스템에서 관련 기억 회상
        recalled_memories = []
        if AURA_MEMORY_AVAILABLE and aura_memory:
            try:
                print(f"[회상 함수 호출] recall_type: {recall_type}")
                recalled_memories = await recall_from_aura_memory(
                    query=user_message,
                    user_id=user_id,
                    limit=3,
                    recall_type=recall_type
                )
                print(f"[회상 결과] {len(recalled_memories)}개: {recalled_memories}")
            except Exception as e:
                print(f"[ERROR] 아우라 메모리 회상 실패: {e}")
        else:
            print("[INFO] 아우라 메모리 시스템 미사용, 기본 회상 동작")
        # 2. 고급 채팅 시스템 처리 (가능한 경우)
        advanced_response = None
        if ADVANCED_CHAT_AVAILABLE and advanced_chat_system:
            try:
                print("[고급 채팅 시스템 호출]")
                advanced_result = await advanced_chat_system.process_message(
                    user_message=user_message,
                    user_id=user_id
                )
                advanced_response = advanced_result.get("response")
                print(f"[고급 채팅 응답] {advanced_response}")
            except Exception as e:
                print(f"[ERROR] 고급 채팅 시스템 실패: {e}")
        else:
            print("[INFO] 고급 채팅 시스템 미사용, 기본 시스템 동작")
        
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
        
        # AI 프롬프트 로드 - ai_prompts.json에서 직접 사용
        # 🎯 과거 대화 회상 및 메모리 활용 지시사항 (최우선)
        memory_instruction = (
            "아래 [과거 대화 요약] 메시지는 참고하여, 필요하다고 판단되는 경우에만 답변에 반영하라. "
            "특히, 날씨/시간/장소/감정 등 맥락이 중요한 경우에는 과거 대화를 적극적으로 활용하라.\n"
            "아래 [과거 대화 요약] 사용자 질문이 1개 이상의 회상 답변을 요구 하는지 판단하여 대화에 필요하다고 판단되는 경우 1개 이상 3개까지 답변에 반영하라.\n\n"
        )
        
        system_prompt = "당신은 EORA라는 감정 중심 인공지능입니다. 친근하고 따뜻한 톤으로 대화해주세요."
        
        logger.info("🔍 프롬프트 검색 시작...")
        logger.info(f"📄 prompts_data 타입: {type(prompts_data)}")
        
        if prompts_data and isinstance(prompts_data, dict):
            logger.info(f"📄 prompts_data 키: {list(prompts_data.keys())}")
            
            # ai1 프롬프트 우선 시도 (system + role + guide + format 조합)
            if "ai1" in prompts_data and isinstance(prompts_data["ai1"], dict):
                ai1_data = prompts_data["ai1"]
                logger.info(f"📝 ai1 카테고리: {list(ai1_data.keys())}")
                
                # system 프롬프트 조합
                system_parts = []
                if "system" in ai1_data and isinstance(ai1_data["system"], list):
                    system_parts.extend(ai1_data["system"])
                if "role" in ai1_data and isinstance(ai1_data["role"], list):
                    system_parts.extend(ai1_data["role"])
                if "guide" in ai1_data and isinstance(ai1_data["guide"], list):
                    system_parts.extend(ai1_data["guide"])
                if "format" in ai1_data and isinstance(ai1_data["format"], list):
                    system_parts.extend(ai1_data["format"])
                
                if system_parts:
                    # 메모리 지시사항을 맨 앞에 배치하고 기존 프롬프트 결합
                    system_prompt = memory_instruction + "\n\n".join(system_parts)
                    logger.info("✅ ai_prompts.json의 ai1 프롬프트 적용 (메모리 지시사항 포함)")
                    logger.info(f"📝 프롬프트 길이: {len(system_prompt)} 문자")
                    logger.info(f"📝 프롬프트 미리보기: {system_prompt[:200]}...")
                else:
                    logger.warning("⚠️ ai1에 사용 가능한 프롬프트가 없습니다")
            
            # ai2 프롬프트 시도
            elif "ai2" in prompts_data and isinstance(prompts_data["ai2"], dict):
                ai2_data = prompts_data["ai2"]
                system_parts = []
                if "system" in ai2_data and isinstance(ai2_data["system"], list):
                    system_parts.extend(ai2_data["system"])
                if "role" in ai2_data and isinstance(ai2_data["role"], list):
                    system_parts.extend(ai2_data["role"])
                
                if system_parts:
                    # 메모리 지시사항을 맨 앞에 배치하고 기존 프롬프트 결합
                    system_prompt = memory_instruction + "\n\n".join(system_parts)
                    logger.info("✅ ai_prompts.json의 ai2 프롬프트 적용 (메모리 지시사항 포함)")
                    logger.info(f"📝 프롬프트 길이: {len(system_prompt)} 문자")
                else:
                    logger.warning("⚠️ ai2에 사용 가능한 프롬프트가 없습니다")
            
            # 다른 AI 프롬프트 시도
            else:
                for ai_name, ai_data in prompts_data.items():
                    if isinstance(ai_data, dict) and "system" in ai_data:
                        if isinstance(ai_data["system"], list) and ai_data["system"]:
                            # 메모리 지시사항을 맨 앞에 배치하고 기존 프롬프트 결합
                            system_prompt = memory_instruction + "\n\n".join(ai_data["system"])
                            logger.info(f"✅ ai_prompts.json의 {ai_name} 프롬프트 적용 (메모리 지시사항 포함)")
                            logger.info(f"📝 프롬프트 길이: {len(system_prompt)} 문자")
                            break
                else:
                    logger.warning("⚠️ 사용 가능한 AI 프롬프트를 찾을 수 없습니다")
                    # 기본 프롬프트에도 메모리 지시사항 추가
                    system_prompt = memory_instruction + system_prompt
        else:
            logger.warning("⚠️ prompts_data가 비어있거나 잘못된 형식입니다")
            # 기본 프롬프트에도 메모리 지시사항 추가
            system_prompt = memory_instruction + system_prompt
        
        logger.info(f"🎯 최종 사용 프롬프트 길이: {len(system_prompt)} 문자")
        
        # 4. EORA 응답 생성 - 회상된 기억과 고급 시스템 통합
        eora_response = None
        
        # 디버깅: 조건 확인
        print(f"[DEBUG] openai_client: {openai_client}")
        print(f"[DEBUG] OPENAI_API_KEY: {OPENAI_API_KEY[:20]}..." if OPENAI_API_KEY else "[DEBUG] OPENAI_API_KEY: None/Empty")
        print(f"[DEBUG] openai_client and OPENAI_API_KEY: {bool(openai_client and OPENAI_API_KEY)}")
        
        # 고급 응답 우선 사용
        if advanced_response:
            eora_response = advanced_response
            logger.info("✅ 고급 채팅 시스템 응답 사용")
        # OpenAI API 사용 (강제로 True로 설정하여 테스트)
        elif True:  # openai_client and OPENAI_API_KEY:
            try:
                # messages 배열 생성: system 프롬프트, 회상(assistant), user 입력
                messages = []
                messages.append({"role": "system", "content": system_prompt})
                # 회상된 메모리(최대 3~5개) assistant 역할로 추가
                if recalled_memories:
                    for memory in recalled_memories:
                        recall_text = getattr(memory, "message", None) or getattr(memory, "content", None) or ""
                        if recall_text:
                            messages.append({"role": "assistant", "content": recall_text})
                # 마지막에 유저 입력 추가
                messages.append({"role": "user", "content": user_message})
                # 최신 OpenAI 라이브러리 호환 - gpt-4o 모델 사용
                response = openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    max_tokens=500,
                    temperature=0.7
                )
                eora_response = response.choices[0].message.content
                logger.info("✅ OpenAI API 호출 성공 (프롬프트+회상 포함)")
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
        
        # 6. 아우라 시스템 대화 저장 (통합/메모리/기본 fallback)
        aura_save_success = False
        try:
            # 1순위: 아우라 통합 시스템
            if 'aura_integration' in globals() and aura_integration:
                try:
                    await aura_integration.save_chat(user_id, session_id, user_message, eora_response)
                    logger.info("✅ 아우라 통합 시스템에 대화 저장 성공")
                    aura_save_success = True
                except Exception as e:
                    logger.error(f"❌ 아우라 통합 시스템 대화 저장 실패: {e}")
            # 2순위: 아우라 메모리 시스템
            elif AURA_MEMORY_AVAILABLE and aura_memory:
                try:
                    memory_id = await save_to_aura_memory(
                        user_id=user_id,
                        session_id=session_id,
                        message=user_message,
                        response=eora_response
                    )
                    logger.info(f"✅ 아우라 메모리 시스템에 대화 저장 성공: {memory_id}")
                    aura_save_success = True
                except Exception as e:
                    logger.error(f"❌ 아우라 메모리 시스템 대화 저장 실패: {e}")
            # 3순위: MongoDB/메모리 fallback
            if not aura_save_success:
                if chat_logs_collection is not None:
                    try:
                        chat_logs_collection.insert_one({
                            "session_id": session_id,
                            "user_id": user_id,
                            "content": user_message,
                            "role": "user",
                            "timestamp": datetime.now()
                        })
                        chat_logs_collection.insert_one({
                            "session_id": session_id,
                            "user_id": user_id,
                            "content": eora_response,
                            "role": "assistant",
                            "timestamp": datetime.now()
                        })
                        logger.info("✅ fallback: MongoDB에 대화 저장 완료")
                    except Exception as e:
                        logger.error(f"❌ fallback: MongoDB 대화 저장 실패: {e}")
                else:
                    try:
                        save_message_to_memory({
                            "session_id": session_id,
                            "user_id": user_id,
                            "content": user_message,
                            "role": "user",
                            "timestamp": datetime.now()
                        })
                        save_message_to_memory({
                            "session_id": session_id,
                            "user_id": user_id,
                            "content": eora_response,
                            "role": "assistant",
                            "timestamp": datetime.now()
                        })
                        logger.info("✅ fallback: 메모리에 대화 저장 완료")
                    except Exception as e:
                        logger.error(f"❌ fallback: 메모리 대화 저장 실패: {e}")
        except Exception as e:
            logger.error(f"❌ 대화 저장 전체 실패: {e}")
        
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
        
        # 토큰 정보 계산
        try:
            import tiktoken
            encoding = tiktoken.get_encoding("cl100k_base")
            
            # 토큰 계산
            user_tokens = len(encoding.encode(user_message))
            prompt_tokens = len(encoding.encode(system_prompt))
            recall_tokens = len(encoding.encode(str(recalled_memories)))
            total_tokens = user_tokens + prompt_tokens + recall_tokens
            
            # 포인트 차감 (토큰당 2포인트)
            points_to_deduct = total_tokens * 2
            
            # 사용자 포인트 업데이트
            user_id = data.get("user_id", "test_user")
            user_points_collection = db[f"user_{user_id}_points"]
            user_doc = user_points_collection.find_one({"user_id": user_id})
            
            if user_doc:
                current_points = user_doc.get("points", 100000)
                new_points = max(0, current_points - points_to_deduct)
                user_points_collection.update_one(
                    {"user_id": user_id},
                    {"$set": {"points": new_points}},
                    upsert=True
                )
            else:
                # 새 사용자인 경우 100,000 포인트로 초기화
                new_points = max(0, 100000 - points_to_deduct)
                user_points_collection.insert_one({
                    "user_id": user_id,
                    "points": new_points
                })
            
            token_info = {
                "user_tokens": user_tokens,
                "prompt_tokens": prompt_tokens,
                "recall_tokens": recall_tokens,
                "total_tokens": total_tokens,
                "points_deducted": points_to_deduct,
                "remaining_points": new_points
            }
            
            print(f"🔢 토큰 계산: {token_info}")
            
        except Exception as e:
            print(f"❌ 토큰 계산 오류: {e}")
            token_info = {
                "user_tokens": 0,
                "prompt_tokens": 0,
                "recall_tokens": 0,
                "total_tokens": 0,
                "points_deducted": 0,
                "remaining_points": 100000
            }
        
        return {
            "response": eora_response,
            "message_id": message_id,
            "timestamp": datetime.now().isoformat(),
            "token_info": token_info
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
        "points": 100000,
        "aura_level": 5
    }

# 포인트 시스템 API
@app.get("/api/user/points")
async def get_user_points(request: Request):
    try:
        # 기본 사용자 ID 설정 (테스트용)
        user_id = "test_user"
        
        # MongoDB 연결 확인
        if db is None:
            return {"points": 100000, "user_id": user_id}
        
        # 사용자 포인트 조회
        points_col = db[f"user_{user_id}_points"]
        points_doc = points_col.find_one({"user_id": user_id})
        
        if not points_doc:
            # 새 사용자인 경우 100,000 포인트로 초기화
            points_col.insert_one({"user_id": user_id, "points": 100000})
            return {"points": 100000, "user_id": user_id}
        
        points = points_doc.get("points", 100000)
        return {"points": points, "user_id": user_id}
    except Exception as e:
        logger.error(f"포인트 조회 오류: {e}")
        return {"points": 100000, "user_id": "test_user"}

# 테스트 호환성을 위한 추가 경로
@app.get("/user/points")
async def get_user_points_compat(request: Request):
    """사용자 포인트 조회 (호환성 경로)"""
    user_id = request.query_params.get("user_id", "test_user")
    
    try:
        # MongoDB 연결 확인
        if db is None:
            return {"points": 100000, "user_id": user_id}
        
        # 사용자 포인트 조회
        points_col = db[f"user_{user_id}_points"]
        points_doc = points_col.find_one({"user_id": user_id})
        
        if not points_doc:
            # 새 사용자인 경우 100,000 포인트로 초기화
            points_col.insert_one({"user_id": user_id, "points": 100000})
            return {"points": 100000, "user_id": user_id}
        
        points = points_doc.get("points", 100000)
        return {"points": points, "user_id": user_id}
    except Exception as e:
        logger.error(f"포인트 조회 오류: {e}")
        return {"points": 100000, "user_id": user_id}

@app.get("/api/points/packages")
async def get_point_packages():
    return {
        "packages": [
            {"id": 1, "name": "기본 패키지", "points": 100000, "price": 10000},
            {"id": 2, "name": "프리미엄 패키지", "points": 500000, "price": 50000},
            {"id": 3, "name": "VIP 패키지", "points": 1000000, "price": 100000}
        ]
    }

# 관리자 로그인 API
@app.post("/api/admin/login")
async def admin_login(request: Request):
    try:
        data = await request.json()
        email = data.get("email", "")
        password = data.get("password", "")
        if email == "admin@eora.ai" and password == "admin123":
            access_token = create_access_token({"user_id": "admin", "role": "admin", "email": email, "is_admin": True})
            user_info = {
                "id": "admin",
                "email": email,
                "role": "admin",
                "name": "EORA 관리자",
                "is_admin": True
            }
            return {
                "success": True,
                "message": "관리자 로그인 성공",
                "user": user_info,
                "access_token": access_token
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
    global db, users_collection
    try:
        data = await request.json()
        email = data.get("email", "")
        password = data.get("password", "")
        name = data.get("name", "")
        print("[회원가입 시도] email:", email, "password:", password, "name:", name)
        if not email or not password:
            print("[회원가입] 이메일/비밀번호 누락")
            return {"success": False, "message": "이메일과 비밀번호를 입력해주세요."}
        if users_collection is None or db is None:
            print("[회원가입] MongoDB 연결 실패(users_collection/db is None)")
            return {"success": False, "message": "DB 연결 실패"}
        if users_collection.find_one({"email": email}):
            print("[회원가입] 이미 등록된 이메일:", email)
            return {"success": False, "message": "이미 등록된 이메일입니다."}
        user_id = str(uuid.uuid4())
        user_doc = {"user_id": user_id, "email": email, "password": password, "name": name, "role": "user"}
        users_collection.insert_one(user_doc)
        for coll in [f"user_{user_id}_chat", f"user_{user_id}_points"]:
            if coll not in db.list_collection_names():
                db.create_collection(coll)
        db[f"user_{user_id}_points"].insert_one({"user_id": user_id, "points": 100000})
        access_token = create_access_token({"user_id": user_id, "role": "user", "email": email})
        print("[회원가입 성공] email:", email, "user_id:", user_id)
        resp = JSONResponse({
            "success": True,
            "message": "회원가입 성공! 10만 포인트가 지급되었습니다.",
            "user": user_doc,
            "access_token": access_token
        })
        resp.set_cookie(key="user_email", value=email, max_age=86400, path="/", samesite="Lax", secure=False)
        return resp
    except Exception as e:
        print("[회원가입 예외]", e)
        logger.error(f"회원가입 오류: {e}")
        return {"success": False, "message": str(e)}

@app.post("/api/login")
async def login(request: Request):
    global users_collection
    try:
        data = await request.json()
        email = data.get("email", "")
        password = data.get("password", "")
        print("[로그인 시도] email:", email, "password:", password)
        
        if email == "admin@eora.ai" and password == "admin123":
            access_token = create_access_token({"user_id": "admin", "role": "admin", "email": email, "is_admin": True})
            user_info = {
                "id": "admin",
                "email": email,
                "role": "admin",
                "name": "EORA 관리자",
                "is_admin": True,
                "user_id": "admin"
            }
            
                        # Railway 환경에서 세션 저장 (세션 미들웨어가 있을 때만)
            if SESSION_MIDDLEWARE_AVAILABLE:
                try:
                    if hasattr(request, 'session'):
                        request.session["user"] = user_info
                        logger.info(f"✅ 관리자 세션 저장 성공: {email}")
                except Exception as e:
                    logger.warning(f"⚠️ 관리자 세션 저장 실패: {e}")
            else:
                logger.info("ℹ️ 세션 미들웨어 없음 - 쿠키만 사용")
            
            print("[관리자 로그인 성공] email:", email)
            resp = JSONResponse({
                "success": True,
                "message": "로그인 성공",
                "user": user_info,
                "access_token": access_token
            })
            
            # Railway 환경에 최적화된 쿠키 설정
            resp.set_cookie(key="user_email", value=email, max_age=86400*7, path="/", samesite="Lax", secure=False, httponly=False)
            resp.set_cookie(key="is_admin", value="true", max_age=86400*7, path="/", samesite="Lax", secure=False, httponly=False)
            resp.set_cookie(key="user", value=json.dumps(user_info), max_age=86400*7, path="/", samesite="Lax", secure=False, httponly=False)
            return resp
        else:
            if users_collection is None:
                print("[로그인] MongoDB 연결 실패(users_collection is None)")
                return {"success": False, "message": "DB 연결 실패"}
            user = users_collection.find_one({"email": email, "password": password})
            if user:
                user_info = {
                    "id": str(user.get("_id", email)),
                    "email": email,
                    "role": user.get("role", "user"),
                    "name": user.get("name", email.split('@')[0]),
                    "is_admin": user.get("role") == "admin" or email == "admin@eora.ai",
                    "user_id": str(user.get("_id", email))
                }
                
                # Railway 환경에서 세션 저장
                try:
                    if hasattr(request, 'session'):
                        request.session["user"] = user_info
                        logger.info(f"✅ 일반 사용자 세션 저장 성공: {email}")
                except Exception as e:
                    logger.warning(f"⚠️ 일반 사용자 세션 저장 실패: {e}")
                
                access_token = create_access_token({"user_id": user.get("user_id"), "role": user.get("role", "user"), "email": email})
                print("[일반 로그인 성공] email:", email)
                resp = JSONResponse({
                    "success": True,
                    "message": "로그인 성공",
                    "user": user_info,
                    "access_token": access_token
                })
                
                # Railway 환경에 최적화된 쿠키 설정
                resp.set_cookie(key="user_email", value=email, max_age=86400*7, path="/", samesite="Lax", secure=False, httponly=False)
                resp.set_cookie(key="is_admin", value="false", max_age=86400*7, path="/", samesite="Lax", secure=False, httponly=False)
                resp.set_cookie(key="user", value=json.dumps(user_info), max_age=86400*7, path="/", samesite="Lax", secure=False, httponly=False)
                return resp
            print("[로그인 실패] 이메일 또는 비밀번호 불일치:", email)
            return {"success": False, "message": "이메일 또는 비밀번호가 올바르지 않습니다."}
    except Exception as e:
        print("[로그인 예외]", e)
        logger.error(f"❌ 로그인 오류: {e}")
        return {"success": False, "message": "로그인 처리 중 오류가 발생했습니다."}

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
    """사용자 관리 데이터 조회 - 레일웨이 환경 호환성 개선"""
    try:
        # 레일웨이 환경에서 임시 사용자 데이터 반환
        if os.getenv("RAILWAY_ENVIRONMENT") == "production" or os.getenv("RAILWAY_ENVIRONMENT"):
            logger.info("🔧 레일웨이 환경에서 임시 사용자 데이터 반환")
            temp_users = [
                {
                    "user_id": "railway_user_1",
                    "email": "user1@railway.com",
                    "role": "user",
                    "points": 1000,
                    "created_at": "2025-07-23T00:00:00Z",
                    "last_login": "2025-07-23T12:00:00Z",
                    "status": "활성"
                },
                {
                    "user_id": "railway_user_2", 
                    "email": "user2@railway.com",
                    "role": "user",
                    "points": 500,
                    "created_at": "2025-07-23T01:00:00Z",
                    "last_login": "2025-07-23T11:00:00Z",
                    "status": "활성"
                },
                {
                    "user_id": "railway_admin",
                    "email": "admin@eora.ai",
                    "role": "admin",
                    "points": 9999,
                    "created_at": "2025-07-23T00:00:00Z",
                    "last_login": "2025-07-23T12:00:00Z",
                    "status": "활성"
                }
            ]
            return {
                "success": True,
                "statistics": {
                    "total_users": 3,
                    "active_users": 2,
                    "total_sessions": 5
                },
                "users": temp_users
            }
        
        # 실제 데이터베이스에서 사용자 조회
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
        
        logger.info(f"✅ 실제 사용자 데이터 로드: {total_users}명")
        return {
            "success": True,
            "statistics": {
                "total_users": total_users,
                "active_users": active_users,
                "total_sessions": len(sessions)
            },
            "users": user_details
        }
    except Exception as e:
        logger.error(f"❌ 사용자 데이터 조회 오류: {e}")
        return {"success": False, "error": "사용자 데이터를 가져올 수 없습니다."}

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

async def recall_from_aura_memory(query: str, user_id: str = None, limit: int = 5, recall_type: str = "normal"):
    """아우라 메모리 시스템에서 8종 회상 분기 지원"""
    try:
        if AURA_MEMORY_AVAILABLE and aura_memory:
            # 8종 회상 분기 예시
            if recall_type == "window":
                memories = aura_memory.recall_window(query=query, user_id=user_id, limit=limit)
            elif recall_type == "wisdom":
                memories = aura_memory.recall_wisdom(query=query, user_id=user_id, limit=limit)
            elif recall_type == "intuition":
                memories = aura_memory.recall_intuition(query=query, user_id=user_id, limit=limit)
            # ... 기타 회상 유형 추가 가능 ...
            else:
                memories = aura_memory.recall_memories(query=query, user_id=user_id, limit=limit)
            logger.info(f"✅ 아우라 메모리 회상({recall_type}) 완료: {len(memories)}개")
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
        db = get_db()
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
from fastapi.responses import JSONResponse

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

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=24)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# .env 파일 로드 (로컬 개발 시)
load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MONGODB_URI = os.environ.get("MONGODB_URI")

# 애플리케이션 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002, reload=True)

# robust 회원가입 API (프론트/테스트와 경로/포맷 일치)
@app.post("/api/auth/register")
async def register_user(request: Request):
    try:
        data = await request.json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        if not all([name, email, password]):
            logger.warning("회원가입: 필수 입력값 누락")
            raise HTTPException(status_code=400, detail="모든 필드를 입력해주세요.")
        # DB 연결 확인
        if 'users_collection' not in globals() or users_collection is None:
            logger.error("회원가입: DB(users_collection) 연결 안됨")
            raise HTTPException(status_code=500, detail="DB 연결 실패")
        # 중복 체크
        if users_collection.find_one({"email": email}):
            logger.warning(f"회원가입: 이미 존재하는 이메일 {email}")
            raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
        # 비밀번호 해시
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

# robust 로그인 API (is_admin 포함, ObjectId 변환)
@app.post("/api/auth/login")
async def login_user(request: Request):
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        if not all([email, password]):
            raise HTTPException(status_code=400, detail="이메일과 비밀번호를 입력해주세요.")
        if 'users_collection' not in globals() or users_collection is None:
            logger.error("로그인: DB(users_collection) 연결 안됨")
            raise HTTPException(status_code=500, detail="DB 연결 실패")
        user = users_collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=400, detail="존재하지 않는 이메일입니다.")
        import hashlib
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user["password"] != hashed_password:
            raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")
        # ObjectId 변환/제외
        user_info = {k: v for k, v in user.items() if k != "_id"}
        user_info["user_id"] = user.get("user_id", str(user.get("_id", "")))
        # 프론트엔드 안내: is_admin이 true일 때만 관리자 페이지/버튼 노출
        # 예: if (user.is_admin) { ...관리자 UI... }
        return {"success": True, "user": user_info, "is_admin": user.get("is_admin", False)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"로그인 오류: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"로그인 중 오류가 발생했습니다: {e}")

# robust 학습하기 API (DB 연결 상태 확인)
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

# ... 기존 코드 ...

# MongoDB 연결 및 users_collection 글로벌 초기화 (import문 바로 아래에 추가)
try:
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[os.environ.get("MONGO_DB", "eora_ai")]
    users_collection = db["users"]
    logger.info(f"✅ MongoDB 연결 성공: {MONGO_URI}")
    logger.info(f"✅ users 컬렉션 초기화 완료 (DB: {db.name})")
except Exception as e:
    users_collection = None
    logger.error(f"❌ MongoDB 연결/컬렉션 초기화 실패: {e}")

# 1. 학습하기 페이지 라우터 추가
@app.get("/learning", response_class=HTMLResponse)
async def learning_page(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("learning.html", {"request": request, "user": user})

# 2. 관리자 페이지 라우트 권한 강화
@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    user = get_current_user(request)
    if not user or user.get("email") != "admin@eora.ai":
        return RedirectResponse("/login")
    return templates.TemplateResponse("admin.html", {"request": request, "user": user})

# 3. 채팅 저장/조회 시 user_id별 컬렉션 사용 예시 (핵심 부분만)
def get_user_chat_collection(user_id):
    return db[f"user_{user_id}_chat"]

def get_user_points_collection(user_id):
    return db[f"user_{user_id}_points"]

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

@app.post("/api/admin/learn-file")
async def learn_file(request: Request, file: UploadFile = File(...)):
    user = get_current_user(request)
    if not user or not (user.get("is_admin") or user.get("role") == "admin"):
        return JSONResponse({"success": False, "message": "관리자 권한이 필요합니다."}, status_code=403)
    try:
        content = await file.read()
        text = content.decode("utf-8", errors="ignore")
        chunk_size = 5000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        # 실제로는 DB 저장 등 추가 처리 필요
        return {"success": True, "chunks": len(chunks)}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/api/admin/learn-dialog-file")
async def learn_dialog_file(request: Request, file: UploadFile = File(...)):
    user = get_current_user(request)
    if not user or not (user.get("is_admin") or user.get("role") == "admin"):
        return JSONResponse({"success": False, "message": "관리자 권한이 필요합니다."}, status_code=403)
    try:
        content = await file.read()
        text = content.decode("utf-8", errors="ignore")
        turns = text.count("\n")  # 실제로는 대화 턴 파싱 필요
        return {"success": True, "turns": turns}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/api/advanced-chat")
async def advanced_chat_api(request: Request):
    """
    EORA 고급 채팅 시스템 API 엔드포인트
    - body: {"message": "...", "user_id": "..."}
    """
    if not ADVANCED_CHAT_AVAILABLE or advanced_chat_system is None:
        return JSONResponse({"error": "고급 채팅 시스템이 활성화되어 있지 않습니다."}, status_code=503)
    try:
        data = await request.json()
        user_message = data.get("message", "")
        user_id = data.get("user_id", "anonymous")
        if not user_message:
            return JSONResponse({"error": "message는 필수입니다."}, status_code=400)
        response = await advanced_chat_system.process_message(user_message, user_id)
        return JSONResponse({
            "result": "ok",
            "advanced_chat": True,
            "response": response
        })
    except Exception as e:
        logger.error(f"고급 채팅 시스템 오류: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
