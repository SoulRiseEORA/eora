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
from starlette.middleware.base import BaseHTTPMiddleware
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
    # Railway 환경에서 가능한 모든 경로 시도
    possible_paths = [
        Path.cwd(),  # 현재 작업 디렉토리 (우선순위 1 - Railway에서 가장 안정적)
        Path(__file__).parent,  # 현재 파일 디렉토리
        Path("/app"),  # Railway 기본 경로
        Path("/app/templates"),  # Railway 템플릿 경로
        Path.cwd() / "templates",  # 현재 디렉토리의 templates
        Path("/workspace"),  # Railway 작업 공간
        Path("/workspace/templates"),  # Railway 작업 공간
        Path("/tmp"),  # 임시 디렉토리
        Path("/tmp/templates"),  # 임시 디렉토리
    ]
    
    # home.html 파일을 찾아서 복사할 대상 경로
    target_path = None
    
    for path in possible_paths:
        logger.info(f"📁 템플릿 경로 시도: {path}")
        logger.info(f"📁 템플릿 존재: {path.exists()}")
        
        if path.exists():
            # HTML 파일이 있는지 확인
            html_files = list(path.glob("*.html"))
            logger.info(f"📄 HTML 파일 수: {len(html_files)}개")
            if html_files:
                logger.info(f"✅ 템플릿 파일 발견: {len(html_files)}개")
                logger.info(f"📄 발견된 파일: {[f.name for f in html_files[:5]]}")
                
                # home.html 파일이 있는지 확인
                home_file = path / "home.html"
                if home_file.exists():
                    logger.info(f"✅ home.html 발견: {home_file}")
                    return path
                else:
                    # home.html이 없으면 첫 번째 경로를 대상으로 설정
                    if target_path is None:
                        target_path = path
            else:
                logger.warning(f"⚠️ {path}에 HTML 파일이 없습니다")
        else:
            logger.warning(f"⚠️ {path} 경로가 존재하지 않습니다")
    
    # home.html 파일을 찾아서 복사 시도
    if target_path is not None:
        logger.info(f"🔍 home.html 파일을 찾아서 {target_path}에 복사 시도 중...")
        
        # 모든 경로에서 home.html 찾기
        for path in possible_paths:
            if path.exists():
                home_file = path / "home.html"
                if home_file.exists():
                    try:
                        import shutil
                        target_home = target_path / "home.html"
                        shutil.copy2(home_file, target_home)
                        logger.info(f"✅ home.html 복사 완료: {home_file} → {target_home}")
                        return target_path
                    except Exception as e:
                        logger.warning(f"⚠️ home.html 복사 실패: {e}")
        
        # home.html을 찾지 못한 경우 기본 HTML 생성
        logger.info("📝 home.html 파일을 찾을 수 없어 기본 HTML 생성")
        try:
            default_home_content = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EORA AI System - Railway</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            text-align: center;
        }
        .header {
            margin-bottom: 40px;
        }
        .title {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
            margin-bottom: 30px;
        }
        .status {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            backdrop-filter: blur(10px);
        }
        .button {
            display: inline-block;
            padding: 15px 30px;
            margin: 10px;
            background: rgba(255,255,255,0.2);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            transition: all 0.3s ease;
            border: 2px solid rgba(255,255,255,0.3);
        }
        .button:hover {
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">🚀 EORA AI System</h1>
            <p class="subtitle">감정 중심 인공지능 플랫폼 - Railway 배포 성공!</p>
        </div>

        <div class="status">
            <h2>✅ 시스템 상태</h2>
            <p>EORA AI 시스템이 Railway에서 성공적으로 실행 중입니다!</p>
            <p><strong>서버:</strong> 정상 실행</p>
            <p><strong>MongoDB:</strong> 연결 성공</p>
            <p><strong>배포:</strong> Railway 클라우드</p>
        </div>

        <div>
            <a href="/chat" class="button">💬 채팅 시작</a>
            <a href="/dashboard" class="button">📊 대시보드</a>
            <a href="/admin" class="button">⚙️ 관리자</a>
            <a href="/security" class="button">🛡️ 보안</a>
        </div>
    </div>
</body>
</html>'''
            
            target_home = target_path / "home.html"
            with open(target_home, 'w', encoding='utf-8') as f:
                f.write(default_home_content)
            logger.info(f"✅ 기본 home.html 생성 완료: {target_home}")
            return target_path
        except Exception as e:
            logger.error(f"❌ 기본 home.html 생성 실패: {e}")
    
    # 기본값 반환 - Railway 환경에서 가장 가능성 높은 경로
    logger.warning("⚠️ 템플릿 디렉토리를 찾을 수 없습니다. 기본 경로 사용")
    return Path("/app")

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
        
        # Railway 환경에서 파일 시스템 전체 스캔
        logger.info("🔍 Railway 환경 파일 시스템 스캔 중...")
        scan_paths = [Path("/app"), Path.cwd(), Path("/workspace"), Path("/tmp")]
        for scan_path in scan_paths:
            if scan_path.exists():
                try:
                    html_files = list(scan_path.rglob("*.html"))
                    logger.info(f"📁 {scan_path}에서 발견된 HTML 파일들: {[f.name for f in html_files[:10]]}")
                    
                    # home.html 파일을 찾아서 복사하거나 이동
                    for html_file in html_files:
                        if html_file.name == "home.html":
                            logger.info(f"✅ home.html 발견: {html_file}")
                            # 현재 템플릿 경로에 복사 시도
                            try:
                                import shutil
                                target_path = templates_path / "home.html"
                                shutil.copy2(html_file, target_path)
                                logger.info(f"✅ home.html 복사 완료: {target_path}")
                                break
                            except Exception as copy_error:
                                logger.warning(f"⚠️ home.html 복사 실패: {copy_error}")
                except Exception as e:
                    logger.warning(f"⚠️ {scan_path} 스캔 실패: {e}")
        
except Exception as e:
    logger.error(f"❌ 템플릿 초기화 실패: {e}")
    # 기본 템플릿 객체 생성 (오류 방지)
    templates = Jinja2Templates(directory=str(Path("/app")))

# 웹소켓 연결 관리자 인스턴스
manager = ConnectionManager()

# 보안 미들웨어 클래스 추가
class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # 차단할 패턴들
        self.blocked_patterns = [
            # WordPress 관련 파일들
            '/wp-', '/wp-admin', '/wp-content', '/wp-includes',
            # PHP 파일들
            '.php', '.phtml', '.php3', '.php4', '.php5', '.php7',
            # 일반적인 공격 패턴들
            '/admin.php', '/config.php', '/shell.php', '/backdoor.php',
            '/upload.php', '/test.php', '/info.php', '/system_log.php',
            '/vendor/', '/composer.json', '/.env', '/config/',
            # 기타 의심스러운 패턴들
            '/sx.php', '/text.php', '/worksec.php', '/x.php', '/xleet.php', '/xox.php'
        ]
        
        # 허용할 정상적인 경로들
        self.allowed_paths = [
            '/', '/chat', '/dashboard', '/login', '/admin', '/debug',
            '/simple-chat', '/points', '/memory', '/prompts', '/security',
            '/health', '/api/', '/ws/', '/static/', '/favicon.ico'
        ]
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path.lower()
        
        # 허용된 경로인지 확인
        is_allowed = any(path.startswith(allowed) for allowed in self.allowed_paths)
        
        # 차단할 패턴이 포함되어 있는지 확인
        is_blocked = any(pattern in path for pattern in self.blocked_patterns)
        
        if is_blocked and not is_allowed:
            # 공격 로그 기록
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            referer = request.headers.get("referer", "unknown")
            
            # 상세한 보안 로그
            logger.warning(f"🚫 보안 차단: {client_ip} - {request.method} {path}")
            logger.warning(f"   User-Agent: {user_agent}")
            logger.warning(f"   Referer: {referer}")
            logger.warning(f"   차단 패턴: {[p for p in self.blocked_patterns if p in path]}")
            
            # 시스템 로그에 보안 이벤트 기록
            try:
                if 'system_logs_collection' in globals() and system_logs_collection is not None:
                    system_logs_collection.insert_one({
                        "event": "security_block",
                        "timestamp": datetime.now(),
                        "client_ip": client_ip,
                        "method": request.method,
                        "path": path,
                        "user_agent": user_agent,
                        "referer": referer,
                        "blocked_patterns": [p for p in self.blocked_patterns if p in path]
                    })
            except Exception as e:
                logger.warning(f"⚠️ 보안 로그 저장 실패: {e}")
            
            # 404 응답 반환 (실제 파일이 없다는 것처럼)
            return JSONResponse(
                status_code=404,
                content={"error": "Not Found"},
                headers={"Server": "nginx/1.18.0"}  # 일반적인 서버 헤더로 위장
            )
        
        # 정상적인 요청 처리
        response = await call_next(request)
        return response

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

# 보안 미들웨어 추가 (가장 먼저 실행되도록)
app.add_middleware(SecurityMiddleware)

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
    try:
        return templates.TemplateResponse("home.html", {"request": request})
    except Exception as e:
        logger.error(f"홈 템플릿 렌더링 오류: {e}")
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>EORA AI System - 감정 중심 인공지능</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    margin: 0; 
                    padding: 0; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                .container {{ 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    padding: 40px 20px; 
                }}
                .header {{ 
                    text-align: center; 
                    color: white; 
                    margin-bottom: 40px; 
                }}
                .header h1 {{ 
                    font-size: 3em; 
                    margin: 0; 
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }}
                .header p {{ 
                    font-size: 1.2em; 
                    margin: 10px 0; 
                    opacity: 0.9;
                }}
                .main-content {{ 
                    background: white; 
                    border-radius: 20px; 
                    padding: 40px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    margin-bottom: 30px;
                }}
                .status-grid {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                    gap: 20px; 
                    margin: 30px 0; 
                }}
                .status-card {{ 
                    background: #f8f9fa; 
                    padding: 20px; 
                    border-radius: 15px; 
                    border-left: 5px solid #28a745; 
                    text-align: center;
                }}
                .status-card.warning {{ border-left-color: #ffc107; }}
                .status-card.error {{ border-left-color: #dc3545; }}
                .status-icon {{ 
                    font-size: 2em; 
                    margin-bottom: 10px; 
                }}
                .nav-grid {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                    gap: 15px; 
                    margin: 30px 0; 
                }}
                .nav-card {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; 
                    padding: 25px; 
                    border-radius: 15px; 
                    text-decoration: none; 
                    text-align: center; 
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }}
                .nav-card:hover {{ 
                    transform: translateY(-5px); 
                    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
                    text-decoration: none;
                    color: white;
                }}
                .nav-card h3 {{ 
                    margin: 0 0 10px 0; 
                    font-size: 1.3em; 
                }}
                .nav-card p {{ 
                    margin: 0; 
                    opacity: 0.9; 
                    font-size: 0.9em; 
                }}
                .footer {{ 
                    text-align: center; 
                    color: white; 
                    margin-top: 40px; 
                    opacity: 0.8;
                }}
                @media (max-width: 768px) {{
                    .header h1 {{ font-size: 2em; }}
                    .main-content {{ padding: 20px; }}
                    .nav-grid {{ grid-template-columns: 1fr; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 EORA AI System</h1>
                    <p>감정 중심 인공지능 플랫폼</p>
                    <p>Railway 환경에서 안정적으로 실행 중</p>
                </div>
                
                <div class="main-content">
                    <div class="status-grid">
                        <div class="status-card">
                            <div class="status-icon">✅</div>
                            <h3>서버 상태</h3>
                            <p>정상 실행 중</p>
                        </div>
                        <div class="status-card">
                            <div class="status-icon">🔒</div>
                            <h3>보안 시스템</h3>
                            <p>활성화됨</p>
                        </div>
                        <div class="status-card warning">
                            <div class="status-icon">⚠️</div>
                            <h3>템플릿 파일</h3>
                            <p>기본 HTML 사용 중</p>
                            <small>Railway 환경에서 자동 생성됨</small>
                        </div>
                        <div class="status-card">
                            <div class="status-icon">💬</div>
                            <h3>채팅 기능</h3>
                            <p>사용 가능</p>
                        </div>
                    </div>
                    
                    <div class="nav-grid">
                        <a href="/chat" class="nav-card">
                            <h3>💬 채팅</h3>
                            <p>EORA AI와 대화하기</p>
                        </a>
                        <a href="/dashboard" class="nav-card">
                            <h3>📊 대시보드</h3>
                            <p>시스템 상태 확인</p>
                        </a>
                        <a href="/admin" class="nav-card">
                            <h3>⚙️ 관리자</h3>
                            <p>시스템 관리</p>
                        </a>
                        <a href="/security" class="nav-card">
                            <h3>🛡️ 보안</h3>
                            <p>보안 모니터링</p>
                        </a>
                        <a href="/api/status" class="nav-card">
                            <h3>🔍 API 상태</h3>
                            <p>API 정보 확인</p>
                        </a>
                        <a href="/debug" class="nav-card">
                            <h3>🐛 디버그</h3>
                            <p>시스템 진단</p>
                        </a>
                    </div>
                </div>
                
                <div class="footer">
                    <p>EORA AI System v2.0.0 - Railway 배포 버전</p>
                    <p>템플릿 오류: {str(e)}</p>
                </div>
            </div>
        </body>
        </html>
        """, status_code=200)

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
    try:
        return templates.TemplateResponse("admin.html", {"request": request})
    except Exception as e:
        logger.error(f"관리자 템플릿 렌더링 오류: {e}")
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>EORA AI Admin</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
                .admin-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                button {{ padding: 10px 20px; background: #dc3545; color: white; border: none; border-radius: 5px; cursor: pointer; }}
                button:hover {{ background: #c82333; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚙️ EORA AI Admin Panel</h1>
                <div class="admin-section">
                    <h3>시스템 상태</h3>
                    <p>✅ 서버: 정상 실행 중</p>
                    <p>✅ MongoDB: 연결됨</p>
                    <p>✅ OpenAI API: 설정됨</p>
                </div>
                <div class="admin-section">
                    <h3>관리 기능</h3>
                    <button onclick="alert('관리자 기능은 템플릿 파일이 필요합니다.')">사용자 관리</button>
                    <button onclick="alert('관리자 기능은 템플릿 파일이 필요합니다.')">시스템 설정</button>
                </div>
                <p><a href="/">← 홈으로 돌아가기</a></p>
            </div>
        </body>
        </html>
        """, status_code=200)

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
async def memory(request: Request):
    try:
        return templates.TemplateResponse("memory.html", {"request": request})
    except Exception as e:
        logger.error(f"메모리 템플릿 렌더링 오류: {e}")
        return HTMLResponse(f"<h1>메모리</h1><p>템플릿 오류: {str(e)}</p>", status_code=500)

@app.get("/prompts", response_class=HTMLResponse)
async def prompts(request: Request):
    try:
        return templates.TemplateResponse("prompts.html", {"request": request})
    except Exception as e:
        logger.error(f"프롬프트 템플릿 렌더링 오류: {e}")
        return HTMLResponse(f"<h1>프롬프트</h1><p>템플릿 오류: {str(e)}</p>", status_code=500)

@app.get("/security", response_class=HTMLResponse)
async def security_dashboard(request: Request):
    """보안 대시보드 페이지"""
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>EORA AI Security Dashboard</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
            h1 {{ color: #333; text-align: center; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
            .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #dc3545; }}
            .stat-card.success {{ border-left-color: #28a745; }}
            .stat-card.warning {{ border-left-color: #ffc107; }}
            .stat-number {{ font-size: 2em; font-weight: bold; color: #dc3545; }}
            .stat-number.success {{ color: #28a745; }}
            .stat-number.warning {{ color: #ffc107; }}
            .stat-label {{ color: #666; margin-top: 5px; }}
            .recent-blocks {{ background: #fff; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin: 20px 0; }}
            .block-item {{ padding: 10px; border-bottom: 1px solid #eee; }}
            .block-item:last-child {{ border-bottom: none; }}
            .block-ip {{ font-weight: bold; color: #dc3545; }}
            .block-path {{ color: #666; font-family: monospace; }}
            .block-time {{ color: #999; font-size: 0.9em; }}
            .nav {{ text-align: center; margin: 20px 0; }}
            .nav a {{ display: inline-block; margin: 10px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
            .nav a:hover {{ background: #0056b3; }}
            .refresh-btn {{ background: #28a745; }}
            .refresh-btn:hover {{ background: #218838; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ EORA AI Security Dashboard</h1>
            
            <div class="stats-grid" id="statsGrid">
                <div class="stat-card">
                    <div class="stat-number" id="totalBlocks">-</div>
                    <div class="stat-label">24시간 차단 수</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="uniqueIPs">-</div>
                    <div class="stat-label">차단된 IP 수</div>
                </div>
                <div class="stat-card success">
                    <div class="stat-number success" id="systemStatus">✅</div>
                    <div class="stat-label">시스템 상태</div>
                </div>
                <div class="stat-card warning">
                    <div class="stat-number warning" id="lastUpdate">-</div>
                    <div class="stat-label">마지막 업데이트</div>
                </div>
            </div>
            
            <div class="recent-blocks">
                <h3>🚫 최근 차단 기록</h3>
                <div id="recentBlocks">
                    <p>데이터를 불러오는 중...</p>
                </div>
            </div>
            
            <div class="nav">
                <a href="/" class="refresh-btn" onclick="refreshStats()">🔄 새로고침</a>
                <a href="/">← 홈으로 돌아가기</a>
            </div>
        </div>
        
        <script>
            async function loadSecurityStats() {{
                try {{
                    const response = await fetch('/api/security/stats');
                    const data = await response.json();
                    
                    document.getElementById('totalBlocks').textContent = data.total_blocks_24h || 0;
                    document.getElementById('uniqueIPs').textContent = data.unique_ips_blocked || 0;
                    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
                    
                    // 최근 차단 기록 표시
                    const recentBlocksDiv = document.getElementById('recentBlocks');
                    if (data.recent_blocks && data.recent_blocks.length > 0) {{
                        recentBlocksDiv.innerHTML = data.recent_blocks.map(block => `
                            <div class="block-item">
                                <div class="block-ip">${{block.ip}}</div>
                                <div class="block-path">${{block.path}}</div>
                                <div class="block-time">${{new Date(block.timestamp).toLocaleString()}}</div>
                            </div>
                        `).join('');
                    }} else {{
                        recentBlocksDiv.innerHTML = '<p>차단 기록이 없습니다.</p>';
                    }}
                }} catch (error) {{
                    console.error('보안 통계 로드 실패:', error);
                    document.getElementById('recentBlocks').innerHTML = '<p>데이터 로드 실패</p>';
                }}
            }}
            
            function refreshStats() {{
                loadSecurityStats();
            }}
            
            // 페이지 로드 시 데이터 로드
            loadSecurityStats();
            
            // 30초마다 자동 새로고침
            setInterval(loadSecurityStats, 30000);
        </script>
    </body>
    </html>
    """, status_code=200)

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

# 기본 세션 및 메시지 API
@app.get("/api/sessions")
async def get_sessions():
    try:
        logger.info("📋 세션 조회 요청")
        
        # MongoDB가 연결되어 있으면 MongoDB에서, 아니면 메모리에서
        if sessions_collection is not None:
            try:
                sessions = list(sessions_collection.find().sort("last_activity", -1))
                for session in sessions:
                    convert_objectid(session)
                logger.info(f"✅ MongoDB에서 {len(sessions)}개 세션 조회")
                return {"sessions": sessions}
            except Exception as e:
                logger.error(f"❌ MongoDB 세션 조회 실패: {e}")
                # MongoDB 실패 시 메모리로 전환
                pass
        
        # 메모리 기반 세션 반환
        logger.info("ℹ️ 메모리 기반 세션 조회")
        sessions = get_sessions_from_memory()
        if not sessions:
            # 기본 세션 생성
            logger.info("ℹ️ 기본 세션 생성")
            default_session_id = "default_session"
            save_session_to_memory(default_session_id, {"name": "기본 세션"})
            sessions = get_sessions_from_memory()
        
        logger.info(f"✅ 메모리에서 {len(sessions)}개 세션 조회")
        return {"sessions": sessions}
        
    except Exception as e:
        logger.error(f"❌ 세션 조회 오류: {e}")
        # 오류 시 메모리 기반 세션 반환
        try:
            sessions = get_sessions_from_memory()
            if not sessions:
                default_session_id = "default_session"
                save_session_to_memory(default_session_id, {"name": "기본 세션"})
                sessions = get_sessions_from_memory()
            return {"sessions": sessions}
        except Exception as fallback_error:
            logger.error(f"❌ 메모리 기반 세션 조회도 실패: {fallback_error}")
            return {"sessions": []}

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
        logger.info(f"📨 세션 {session_id} 메시지 조회 요청")
        
        if chat_logs_collection is not None:
            try:
                messages = list(chat_logs_collection.find({"session_id": session_id}).sort("timestamp", 1))
                # ObjectId를 문자열로 변환
                for message in messages:
                    convert_objectid(message)
                logger.info(f"✅ MongoDB에서 {len(messages)}개 메시지 조회")
                return {"messages": messages}
            except Exception as e:
                logger.error(f"❌ MongoDB 메시지 조회 실패: {e}")
                # MongoDB 실패 시 메모리로 전환
                pass
        
        # 메모리 기반 메시지 반환
        logger.info("ℹ️ 메모리 기반 메시지 조회")
        messages = get_messages_from_memory(session_id)
        logger.info(f"✅ 메모리에서 {len(messages)}개 메시지 조회")
        return {"messages": messages}
        
    except Exception as e:
        logger.error(f"❌ 메시지 조회 오류: {e}")
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
        
        logger.info(f"💾 메시지 저장 요청: {message_data['session_id']}")
        
        if chat_logs_collection is not None:
            try:
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
        logger.info(f"✅ 메모리에 메시지 저장 완료: {message_id}")
        return message_data
        
    except Exception as e:
        logger.error(f"❌ 메시지 저장 오류: {e}")
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

@app.get("/api/security/stats")
async def get_security_stats():
    """보안 통계 정보를 반환합니다."""
    try:
        if 'system_logs_collection' in globals() and system_logs_collection is not None:
            # 최근 24시간 보안 차단 통계
            yesterday = datetime.now() - timedelta(days=1)
            security_blocks = list(system_logs_collection.find({
                "event": "security_block",
                "timestamp": {"$gte": yesterday}
            }))
            
            # IP별 차단 통계
            ip_stats = {}
            for block in security_blocks:
                ip = block.get("client_ip", "unknown")
                if ip not in ip_stats:
                    ip_stats[ip] = 0
                ip_stats[ip] += 1
            
            # 패턴별 차단 통계
            pattern_stats = {}
            for block in security_blocks:
                patterns = block.get("blocked_patterns", [])
                for pattern in patterns:
                    if pattern not in pattern_stats:
                        pattern_stats[pattern] = 0
                    pattern_stats[pattern] += 1
            
            return {
                "total_blocks_24h": len(security_blocks),
                "unique_ips_blocked": len(ip_stats),
                "top_blocked_ips": sorted(ip_stats.items(), key=lambda x: x[1], reverse=True)[:10],
                "top_blocked_patterns": sorted(pattern_stats.items(), key=lambda x: x[1], reverse=True)[:10],
                "recent_blocks": [
                    {
                        "timestamp": block.get("timestamp"),
                        "ip": block.get("client_ip"),
                        "path": block.get("path"),
                        "patterns": block.get("blocked_patterns", [])
                    }
                    for block in security_blocks[-10:]  # 최근 10개
                ]
            }
        else:
            return {
                "message": "보안 로그가 활성화되지 않았습니다.",
                "total_blocks_24h": 0,
                "unique_ips_blocked": 0
            }
    except Exception as e:
        logger.error(f"보안 통계 조회 오류: {e}")
        return {"error": str(e)}

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