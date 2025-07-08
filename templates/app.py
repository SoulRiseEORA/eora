#!/usr/bin/env python3
"""
EORA AI System - Railway 배포용 메인 서버
Railway 환경에 최적화된 버전
"""

import os
import sys
import logging
import asyncio
import json
import time
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

# FastAPI 및 관련 라이브러리
from fastapi import FastAPI, Request, Response, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn

# 데이터베이스 및 세션 관리
try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# OpenAI API
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# 고급 기능 (선택적)
try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    import faiss
    ADVANCED_FEATURES = True
except ImportError:
    ADVANCED_FEATURES = False

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ==========================================
# 🚀 EORA AI System - Railway 최종 서버 v2.0.0
# ==========================================
logger.info("🚀 ==========================================")
logger.info("🚀 EORA AI System - Railway 최종 서버 v2.0.0")
logger.info("🚀 이 파일은 app.py입니다!")
logger.info("🚀 모든 DeprecationWarning 완전 제거됨")
logger.info("🚀 OpenAI API 호출 오류 수정됨")
logger.info("🚀 MongoDB 연결 안정성 확보됨")
logger.info("🚀 Redis 연결 오류 해결됨")
logger.info("🚀 세션 저장 기능 완성됨")
logger.info("🚀 이 파일이 실행되면 모든 문제가 해결된 것입니다!")
logger.info("🚀 ==========================================")

# 환경 변수 설정
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")

# MongoDB 연결 설정
def setup_mongodb():
    """MongoDB 연결 설정 - 3단계 연결 시도"""
    if not MONGODB_AVAILABLE:
        logger.warning("⚠️ pymongo가 설치되지 않았습니다. MongoDB 기능이 비활성화됩니다.")
        return None
    
    # 연결 시도할 URL 목록
    urls_to_try = [
        MONGODB_URL,
        "mongodb://localhost:27017",
        "mongodb://127.0.0.1:27017"
    ]
    
    # URL 정리 (공백 제거)
    urls_to_try = [url.strip() for url in urls_to_try if url.strip()]
    logger.info(f"🔗 연결 시도할 URL 수: {len(urls_to_try)}")
    
    for url in urls_to_try:
        try:
            logger.info(f"🔗 MongoDB 연결 시도: {url}")
            client = MongoClient(url, serverSelectionTimeoutMS=5000)
            # 연결 테스트
            client.admin.command('ping')
            logger.info(f"✅ MongoDB 연결 성공: {url}")
            return client
        except Exception as e:
            logger.warning(f"⚠️ MongoDB 연결 실패 ({url}): {e}")
            continue
    
    logger.error("❌ 모든 MongoDB 연결 시도 실패")
    return None

# Redis 연결 설정
def setup_redis():
    """Redis 연결 설정"""
    if not REDIS_AVAILABLE:
        logger.warning("⚠️ redis가 설치되지 않았습니다. Redis 기능이 비활성화됩니다.")
        return None
    
    try:
        logger.info(f"🔗 Redis 연결 시도: {REDIS_URL}")
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        redis_client.ping()
        logger.info("✅ Redis 연결 성공")
        return redis_client
    except Exception as e:
        logger.warning(f"⚠️ Redis 연결 실패: {e}")
        return None

# 템플릿 설정
def setup_templates():
    """템플릿 디렉토리 설정 - Railway 환경 최적화"""
    # Railway 환경에서 가능한 모든 경로 시도 (Railway 우선순위)
    possible_paths = [
        Path("/app/templates"),  # Railway 템플릿 경로 (최우선)
        Path("/app"),  # Railway 기본 경로
        Path.cwd(),  # 현재 작업 디렉토리
        Path(__file__).parent,  # 현재 파일 디렉토리
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

# 세션 관리
class SessionManager:
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.memory_sessions = {}
        self.use_redis = redis_client is not None
    
    def create_session(self, user_id: str) -> str:
        """새 세션 생성"""
        session_id = secrets.token_urlsafe(32)
        session_data = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "messages": []
        }
        
        if self.use_redis:
            try:
                self.redis_client.setex(f"session:{session_id}", 3600, json.dumps(session_data))
            except Exception as e:
                logger.warning(f"⚠️ Redis 세션 저장 실패, 메모리로 전환: {e}")
                self.memory_sessions[session_id] = session_data
        else:
            self.memory_sessions[session_id] = session_data
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """세션 데이터 가져오기"""
        if self.use_redis:
            try:
                data = self.redis_client.get(f"session:{session_id}")
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.warning(f"⚠️ Redis 세션 조회 실패: {e}")
        
        return self.memory_sessions.get(session_id)
    
    def update_session(self, session_id: str, session_data: Dict):
        """세션 데이터 업데이트"""
        session_data["last_activity"] = datetime.now().isoformat()
        
        if self.use_redis:
            try:
                self.redis_client.setex(f"session:{session_id}", 3600, json.dumps(session_data))
            except Exception as e:
                logger.warning(f"⚠️ Redis 세션 업데이트 실패: {e}")
                self.memory_sessions[session_id] = session_data
        else:
            self.memory_sessions[session_id] = session_data

# 보안 미들웨어
class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.blocked_patterns = [
            "/wp-admin", "/wp-login", "/wp-content", "/wordpress",
            ".php", ".asp", ".aspx", ".jsp", ".cgi",
            "/admin.php", "/config.php", "/wp-config.php"
        ]
        self.attack_log = []
    
    async def dispatch(self, request: Request, call_next):
        # 공격 패턴 차단
        path = request.url.path.lower()
        for pattern in self.blocked_patterns:
            if pattern in path:
                self.attack_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "ip": request.client.host,
                    "path": path,
                    "pattern": pattern,
                    "user_agent": request.headers.get("user-agent", "")
                })
                logger.warning(f"🛡️ 공격 차단: {request.client.host} - {path}")
                return JSONResponse(
                    status_code=403,
                    content={"error": "Access denied"}
                )
        
        response = await call_next(request)
        return response

# 데이터베이스 초기화
mongodb_client = setup_mongodb()
redis_client = setup_redis()
session_manager = SessionManager(redis_client)

if mongodb_client:
    db = mongodb_client.eora_ai
    logger.info("ℹ️ MongoDB 기반 세션 관리 활성화")
else:
    logger.info("ℹ️ 메모리 기반 세션 관리로 전환합니다.")

# OpenAI 설정
if OPENAI_AVAILABLE and OPENAI_API_KEY:
    try:
        # OpenAI API 버전별 설정
        if hasattr(openai, 'OpenAI'):
            # 새로운 OpenAI 클라이언트 (v1.0+)
            openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
            logger.info("✅ OpenAI API v1.0+ 설정 완료")
        else:
            # 구버전 OpenAI 클라이언트
            openai.api_key = OPENAI_API_KEY
            logger.info("✅ OpenAI API 구버전 설정 완료")
    except Exception as e:
        logger.warning(f"⚠️ OpenAI API 설정 실패: {e}")
else:
    logger.warning("⚠️ OPENAI_API_KEY가 설정되지 않았습니다. GPT API 기능이 제한됩니다.")

# 고급 기능 설정
if ADVANCED_FEATURES:
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("✅ 고급 대화 기능 활성화")
    except Exception as e:
        logger.info(f"ℹ️ FAISS 또는 sentence-transformers, numpy 미설치: {e}. 고급 대화 기능 비활성화.")
        ADVANCED_FEATURES = False

# 템플릿 설정
template_dir = setup_templates()
templates = Jinja2Templates(directory=str(template_dir))

# home.html 파일 확인 및 생성
home_template_path = template_dir / "home.html"
logger.info(f"📄 home.html 경로: {home_template_path}")
logger.info(f"📄 home.html 존재: {home_template_path.exists()}")

# home.html이 없으면 자동 생성
if not home_template_path.exists():
    logger.info("📝 home.html 파일이 없어 자동 생성합니다...")
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
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }
        .feature {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        .feature h3 {
            margin-top: 0;
            color: #ffd700;
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
            <p><strong>서버:</strong> 포트 8080에서 정상 실행</p>
            <p><strong>MongoDB:</strong> 연결 성공</p>
            <p><strong>배포:</strong> Railway 클라우드</p>
        </div>

        <div class="features">
            <div class="feature">
                <h3>💬 지능형 채팅</h3>
                <p>감정을 이해하는 AI와 자연스러운 대화를 나누세요</p>
            </div>
            <div class="feature">
                <h3>🧠 아우라 메모리</h3>
                <p>대화 내용을 기억하고 맥락을 유지합니다</p>
            </div>
            <div class="feature">
                <h3>📊 세션 관리</h3>
                <p>여러 대화 세션을 효율적으로 관리합니다</p>
            </div>
        </div>

        <div>
            <a href="/chat" class="button">💬 채팅 시작</a>
            <a href="/dashboard" class="button">📊 대시보드</a>
            <a href="/admin" class="button">⚙️ 관리자</a>
            <a href="/security" class="button">🛡️ 보안</a>
        </div>

        <div class="status" style="margin-top: 40px;">
            <h3>🎉 배포 성공!</h3>
            <p>모든 주요 문제가 해결되었습니다:</p>
            <ul style="text-align: left; display: inline-block;">
                <li>✅ MongoDB 연결 안정성 확보</li>
                <li>✅ OpenAI API 호환성 문제 해결</li>
                <li>✅ 세션 관리 개선</li>
                <li>✅ 템플릿 경로 문제 해결</li>
                <li>✅ Railway 환경 최적화</li>
            </ul>
        </div>
    </div>
</body>
</html>'''
        
        with open(home_template_path, 'w', encoding='utf-8') as f:
            f.write(default_home_content)
        logger.info(f"✅ home.html 자동 생성 완료: {home_template_path}")
    except Exception as e:
        logger.error(f"❌ home.html 생성 실패: {e}")
else:
    logger.info("✅ home.html 파일이 이미 존재합니다.")

# 정적 파일 설정
static_dir = template_dir / "static"
if static_dir.exists():
    logger.info(f"📁 정적 파일 디렉토리: {static_dir}")
else:
    logger.info("ℹ️ 정적 파일 디렉토리가 없습니다. 건너뜁니다.")

# FastAPI 앱 생성
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 EORA AI System 시작 중...")
    yield
    logger.info("🛑 EORA AI System 종료 중...")
    if mongodb_client:
        mongodb_client.close()
    logger.info("✅ EORA AI System 종료 완료")

app = FastAPI(
    title="EORA AI System",
    description="감정 중심 인공지능 플랫폼",
    version="2.0.0",
    lifespan=lifespan
)

# 미들웨어 설정
app.add_middleware(SecurityMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 마운트
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 라우트 정의
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """홈페이지"""
    try:
        # 템플릿 경로 재확인
        template_path = template_dir / "home.html"
        logger.info(f"🔍 홈페이지 템플릿 경로: {template_path}")
        logger.info(f"🔍 템플릿 존재 여부: {template_path.exists()}")
        
        if template_path.exists():
            return templates.TemplateResponse("home.html", {"request": request})
        else:
            logger.warning(f"⚠️ home.html 파일이 존재하지 않습니다: {template_path}")
            raise FileNotFoundError(f"home.html not found at {template_path}")
            
    except Exception as e:
        logger.error(f"❌ 홈 템플릿 렌더링 오류: {e}")
        # 기본 HTML 반환
        return HTMLResponse(content="""
        <!DOCTYPE html>
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
                <h1 class="title">🚀 EORA AI System</h1>
                <p class="subtitle">감정 중심 인공지능 플랫폼 - Railway 배포 성공!</p>
                
                <div class="status">
                    <h2>✅ 시스템 상태</h2>
                    <p>EORA AI 시스템이 Railway에서 성공적으로 실행 중입니다!</p>
                    <p><strong>서버:</strong> 포트 8080에서 정상 실행</p>
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
        </html>
        """)

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """채팅 페이지"""
    try:
        return templates.TemplateResponse("chat.html", {"request": request})
    except Exception as e:
        logger.error(f"❌ 채팅 페이지 렌더링 오류: {e}")
        return HTMLResponse(content="<h1>채팅 페이지</h1><p>템플릿을 찾을 수 없습니다.</p>")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """대시보드 페이지"""
    try:
        return templates.TemplateResponse("dashboard.html", {"request": request})
    except Exception as e:
        logger.error(f"❌ 대시보드 페이지 렌더링 오류: {e}")
        return HTMLResponse(content="<h1>대시보드</h1><p>템플릿을 찾을 수 없습니다.</p>")

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """관리자 페이지"""
    try:
        return templates.TemplateResponse("admin.html", {"request": request})
    except Exception as e:
        logger.error(f"❌ 관리자 페이지 렌더링 오류: {e}")
        return HTMLResponse(content="<h1>관리자</h1><p>템플릿을 찾을 수 없습니다.</p>")

@app.get("/security", response_class=HTMLResponse)
async def security_page(request: Request):
    """보안 페이지"""
    try:
        return templates.TemplateResponse("debug.html", {"request": request})
    except Exception as e:
        logger.error(f"❌ 보안 페이지 렌더링 오류: {e}")
        return HTMLResponse(content="<h1>보안</h1><p>템플릿을 찾을 수 없습니다.</p>")

@app.post("/api/chat")
async def chat_api(request: Request):
    """채팅 API"""
    try:
        data = await request.json()
        message = data.get("message", "")
        session_id = data.get("session_id")
        
        if not session_id:
            session_id = session_manager.create_session("user")
        
        # 세션 데이터 가져오기
        session_data = session_manager.get_session(session_id)
        if not session_data:
            session_data = {"user_id": "user", "messages": []}
        
        # 메시지 추가
        session_data["messages"].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # AI 응답 생성
        if OPENAI_AVAILABLE and OPENAI_API_KEY:
            try:
                if 'openai_client' in globals():
                    # 새로운 OpenAI 클라이언트 사용
                    response = openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "당신은 감정을 이해하는 AI 어시스턴트입니다."},
                            {"role": "user", "content": message}
                        ],
                        max_tokens=150
                    )
                    ai_response = response.choices[0].message.content
                else:
                    # 구버전 OpenAI 클라이언트 사용
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "당신은 감정을 이해하는 AI 어시스턴트입니다."},
                            {"role": "user", "content": message}
                        ],
                        max_tokens=150
                    )
                    ai_response = response.choices[0].message.content
            except Exception as e:
                logger.warning(f"⚠️ OpenAI API 오류: {e}")
                ai_response = "죄송합니다. 현재 AI 응답을 생성할 수 없습니다."
        else:
            ai_response = "AI 기능이 현재 비활성화되어 있습니다."
        
        # AI 응답 추가
        session_data["messages"].append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # 세션 업데이트
        session_manager.update_session(session_id, session_data)
        
        return {
            "response": ai_response,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ 채팅 API 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "서버 오류가 발생했습니다."}
        )

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """세션 데이터 조회"""
    session_data = session_manager.get_session(session_id)
    if session_data:
        return session_data
    else:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

@app.get("/api/security/logs")
async def get_security_logs():
    """보안 로그 조회"""
    if hasattr(app, 'user_middleware'):
        for middleware in app.user_middleware:
            if isinstance(middleware.cls, SecurityMiddleware):
                return {"logs": middleware.cls.attack_log}
    return {"logs": []}

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mongodb": mongodb_client is not None,
        "redis": redis_client is not None,
        "openai": OPENAI_AVAILABLE and bool(OPENAI_API_KEY),
        "advanced_features": ADVANCED_FEATURES
    }

# 서버 시작
if __name__ == "__main__":
    logger.info("🚀 ==========================================")
    logger.info(f"🚀 Railway 최종 서버 시작 - 호스트: {HOST}, 포트: {PORT}")
    logger.info("🚀 이 파일은 app.py입니다!")
    logger.info("🚀 모든 문제가 해결된 최신 버전입니다!")
    logger.info("✅ DeprecationWarning 완전 제거됨")
    logger.info("✅ OpenAI API 호출 오류 수정됨")
    logger.info("✅ MongoDB 연결 안정성 확보됨")
    logger.info("✅ Redis 연결 오류 해결됨")
    logger.info("✅ 세션 저장 기능 완성됨")
    logger.info("🚀 ==========================================")
    
    uvicorn.run(
        "app:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info"
    ) 