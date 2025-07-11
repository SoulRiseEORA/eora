#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 오류 수정 완료 버전
모든 들여쓰기 오류와 변수 스코프 오류 해결
"""

import os
import json
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel, EmailStr
import uvicorn
from fastapi.websockets import WebSocket, WebSocketDisconnect

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(title="EORA AI System", version="2.0.0")

# 세션 미들웨어 추가 (중요!)
app.add_middleware(
    SessionMiddleware,
    secret_key="eora_super_secret_key_2024_07_11_!@#",  # 실제 배포시 더 강력하게
    session_cookie="eora_session",
    max_age=60*60*24*7,  # 7일
)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 데이터 모델
class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class LearningSettings(BaseModel):
    interval: int = 24
    threshold: int = 100
    enabled: bool = True

class AttachmentUpload(BaseModel):
    filename: str
    category: str
    description: str
    file_size: int

class PromptTemplate(BaseModel):
    name: str
    category: str
    content: str
    description: str
    tags: List[str] = []

# 메모리 기반 데이터 저장소
users_db: Dict[str, Dict] = {}
sessions_db: Dict[str, Dict] = {}
chat_history: Dict[str, List] = {}
points_db: Dict[str, Dict] = {}
storage_usage: Dict[str, int] = {}

# 새로운 데이터 저장소 추가
learning_settings_db: Dict[str, Any] = {
    "interval": 24,
    "threshold": 100,
    "enabled": True,
    "last_learning": None,
    "accuracy": 85.5,
    "progress": 67.3
}

learning_logs_db: List[Dict] = []
attachments_db: List[Dict] = []
documents_db: List[Dict] = []
knowledge_db: List[Dict] = []
prompts_db: List[Dict] = []
system_logs_db: List[Dict] = []

# 프롬프트 데이터 구조
class Prompt(BaseModel):
    id: str
    name: str
    category: str
    content: str
    description: Optional[str] = ""
    tags: List[str] = []
    ai_name: Optional[str] = None

class CategoryPromptData(BaseModel):
    ai_name: str
    category: str
    prompts: List[Dict[str, Any]]

# 메모리 기반 프롬프트 저장소 (샘플 데이터 포함)
prompts_db: Dict[str, Prompt] = {
    "sample1": Prompt(id="sample1", name="시스템 안내", category="system", content="당신은 친절한 AI입니다.", description="기본 시스템 프롬프트", tags=["system", "guide"]),
    "sample2": Prompt(id="sample2", name="역할 안내", category="role", content="당신은 상담가입니다.", description="역할 프롬프트", tags=["role"])
}

# 간단한 EORA Core 클래스
class EORACore:
    def __init__(self):
        self.name = "EORA Core"
        self.version = "2.0.0"
    
    def process_input(self, message: str, user_id: str = None) -> str:
        """사용자 입력 처리"""
        responses = [
            "안녕하세요! EORA AI 시스템입니다. 무엇을 도와드릴까요?",
            "흥미로운 질문이네요. 더 자세히 설명해주시겠어요?",
            "좋은 질문입니다. 제가 도움을 드릴 수 있는 부분이 있나요?",
            "EORA AI가 당신의 질문에 답변하고 있습니다. 잠시만 기다려주세요.",
            "의식적 AI 시스템과의 대화를 즐기고 계시는군요!",
            "당신의 생각이 흥미롭습니다. 더 자세히 들어보고 싶어요.",
            "EORA AI는 학습과 성장을 통해 더 나은 답변을 제공하려고 합니다.",
            "의식과 지능의 경계에서 당신과 대화하는 것이 즐겁습니다."
        ]
        
        import random
        return random.choice(responses)

# EORA Core 인스턴스 생성
eora_core = EORACore()

# 기본 관리자 계정
DEFAULT_ADMIN = {
    "user_id": "admin_001",
    "name": "관리자",
    "email": "admin@eora.com",
    "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
    "role": "admin",
    "is_admin": True,
    "is_active": True,
    "created_at": datetime.now().isoformat(),
    "last_login": None,
    "storage_used": 0,
    "max_storage": 100 * 1024 * 1024  # 100MB
}

# 유틸리티 함수들
def hash_password(password: str) -> str:
    """비밀번호 해시화"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """비밀번호 검증"""
    return hash_password(password) == hashed

def generate_session_id() -> str:
    """세션 ID 생성"""
    return f"session_{datetime.now().timestamp()}_{secrets.token_hex(8)}"

def get_user_by_email(email: str) -> Optional[Dict]:
    """이메일로 사용자 찾기"""
    for user in users_db.values():
        if user.get("email") == email:
            return user
    return None

def calculate_storage_usage(user_id: str) -> Dict[str, Any]:
    """사용자 저장공간 사용량 계산"""
    user = users_db.get(user_id, {})
    used_bytes = user.get("storage_used", 0)
    max_bytes = user.get("max_storage", 100 * 1024 * 1024)  # 100MB
    usage_percentage = (used_bytes / max_bytes) * 100 if max_bytes > 0 else 0
    
    return {
        "used_bytes": used_bytes,
        "max_bytes": max_bytes,
        "used_mb": round(used_bytes / (1024 * 1024), 2),
        "max_mb": round(max_bytes / (1024 * 1024), 2),
        "usage_percentage": round(usage_percentage, 2)
    }

# 인증 의존성
def get_current_user(request: Request) -> Optional[Dict]:
    """현재 로그인한 사용자 가져오기"""
    user = request.session.get("user")
    if user and user.get("is_active"):
        return user
    return None

def require_auth(request: Request) -> Dict:
    """인증 필요"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다")
    return user

def require_admin(request: Request) -> Dict:
    """관리자 권한 필요"""
    user = require_auth(request)
    if user.get("role") != "admin" and not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다")
    return user

# 초기화
def initialize_system():
    """시스템 초기화"""
    global users_db
    
    # 기본 관리자 계정 생성
    if "admin_001" not in users_db:
        users_db["admin_001"] = DEFAULT_ADMIN.copy()
        logger.info("✅ 기본 관리자 계정 생성 완료")
    
    # 기본 사용자 계정 생성 (테스트용)
    if "user_001" not in users_db:
        users_db["user_001"] = {
            "user_id": "user_001",
            "name": "테스트 사용자",
            "email": "user@eora.com",
            "password_hash": hash_password("user123"),
            "role": "user",
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "storage_used": 1024 * 1024,  # 1MB
            "max_storage": 100 * 1024 * 1024  # 100MB
        }
        logger.info("✅ 기본 사용자 계정 생성 완료")

# API 엔드포인트들

@app.get("/")
async def home(request: Request):
    """홈페이지"""
    user = get_current_user(request)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/home")
async def home_page(request: Request):
    """홈페이지 (home.html)"""
    user = get_current_user(request)
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

@app.get("/login")
async def login_page(request: Request):
    """로그인 페이지"""
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    """회원가입 페이지"""
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard")
async def dashboard_page(request: Request):
    """대시보드 페이지"""
    user = require_auth(request)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@app.get("/admin")
async def admin_page(request: Request):
    """관리자 페이지"""
    user = require_admin(request)
    return templates.TemplateResponse("admin.html", {"request": request, "user": user})

@app.get("/point-management")
async def point_management_page(request: Request):
    """포인트 관리 페이지"""
    user = require_admin(request)
    return templates.TemplateResponse("point_management.html", {"request": request, "user": user})

@app.get("/storage-management")
async def storage_management_page(request: Request):
    """저장소 관리 페이지"""
    user = require_admin(request)
    return templates.TemplateResponse("storage_management.html", {"request": request, "user": user})

@app.get("/prompt-management")
async def prompt_management_page(request: Request):
    """프롬프트 관리 페이지"""
    user = require_admin(request)
    return templates.TemplateResponse("prompt_management.html", {"request": request, "user": user})

@app.get("/profile")
async def profile_page(request: Request):
    """프로필 페이지"""
    user = require_auth(request)
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})

@app.get("/memory")
async def memory_page(request: Request):
    """기억 관리 페이지"""
    user = require_auth(request)
    return templates.TemplateResponse("memory.html", {"request": request, "user": user})

@app.get("/chat")
async def chat_page(request: Request):
    """채팅 페이지"""
    user = get_current_user(request)
    return templates.TemplateResponse("chat.html", {"request": request, "user": user})

# API 엔드포인트들

@app.post("/api/auth/register")
async def register_user(request: Request, user_data: UserRegister):
    """회원가입"""
    log_api_request(request, action="회원가입")
    
    try:
        # 이메일 중복 체크
        if get_user_by_email(user_data.email):
            log_api_response(400, "이미 등록된 이메일")
            return create_error_response("이미 등록된 이메일입니다.", 400, "EMAIL_EXISTS")
        
        # 새 사용자 생성
        user_id = f"user_{len(users_db) + 1:03d}"
        new_user = {
            "user_id": user_id,
            "name": user_data.name,
            "email": user_data.email,
            "password_hash": hash_password(user_data.password),
            "role": "user",
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "storage_used": 0,
            "max_storage": 100 * 1024 * 1024  # 100MB
        }
        
        users_db[user_id] = new_user
        
        # 포인트 초기화
        points_db[user_id] = {
            "user_id": user_id,
            "current_points": 100,  # 가입 보너스
            "total_earned": 100,
            "total_spent": 0,
            "last_updated": datetime.now().isoformat(),
            "history": [{
                "type": "signup_bonus",
                "amount": 100,
                "description": "회원가입 보너스",
                "timestamp": datetime.now().isoformat()
            }]
        }
        
        logger.info(f"✅ 새 사용자 등록: {user_data.email}")
        log_api_response(200, "회원가입 성공")
        return create_success_response({"user_id": user_id}, "회원가입이 완료되었습니다.")
        
    except Exception as e:
        logger.error(f"회원가입 오류: {e}")
        log_api_response(500, "회원가입 오류")
        return create_error_response("회원가입 중 오류가 발생했습니다.", 500, "REGISTRATION_ERROR")

@app.post("/api/auth/login")
async def login_user(request: Request, login_data: UserLogin):
    """로그인"""
    log_api_request(request, action="로그인")
    
    try:
        user = get_user_by_email(login_data.email)
        if not user or not verify_password(login_data.password, user["password_hash"]):
            log_api_response(401, "잘못된 로그인 정보")
            return create_error_response("이메일 또는 비밀번호가 올바르지 않습니다.", 401, "INVALID_CREDENTIALS")
        
        if not user.get("is_active"):
            log_api_response(401, "비활성화된 계정")
            return create_error_response("비활성화된 계정입니다.", 401, "INACTIVE_ACCOUNT")
        
        # 로그인 시간 업데이트
        user["last_login"] = datetime.now().isoformat()
        
        # 세션에 사용자 정보 저장
        request.session["user"] = {
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "is_admin": user.get("is_admin", False),
            "is_active": user["is_active"]
        }
        
        user_data = {
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "is_admin": user.get("is_admin", False),
            "username": user["name"]  # home.html에서 사용하는 필드
        }
        
        logger.info(f"✅ 사용자 로그인 성공: {user['email']}")
        log_api_response(200, "로그인 성공")
        return create_success_response(user_data, "로그인 성공")
        
    except Exception as e:
        logger.error(f"로그인 오류: {e}")
        log_api_response(500, "로그인 오류")
        return create_error_response("로그인 중 오류가 발생했습니다.", 500, "LOGIN_ERROR")

@app.post("/api/login")
async def login_user_legacy(request: Request, login_data: UserLogin):
    """로그인 (레거시 경로 지원)"""
    return await login_user(request, login_data)

@app.post("/api/auth/logout")
async def logout_user(request: Request):
    """로그아웃"""
    try:
        # 세션 정보 로깅
        user_info = request.session.get("user")
        if user_info:
            logger.info(f"✅ 사용자 로그아웃: {user_info.get('email', 'unknown')}")
        
        # 세션 완전 삭제
        request.session.clear()
        
        # 응답 헤더에 캐시 제어 설정
        response = create_success_response(message="로그아웃되었습니다.")
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
        
    except Exception as e:
        logger.error(f"로그아웃 오류: {e}")
        return create_error_response("로그아웃 중 오류가 발생했습니다.", 500, "LOGOUT_ERROR")

@app.get("/api/user/stats")
async def get_user_stats(request: Request):
    """사용자 통계 정보"""
    user = require_auth(request)
    
    try:
        # 저장공간 사용량
        storage_info = calculate_storage_usage(user["user_id"])
        
        # 포인트 정보
        user_points = points_db.get(user["user_id"], {
            "current_points": 0,
            "total_earned": 0,
            "total_spent": 0
        })
        
        # 채팅 세션 수
        user_sessions = [s for s in sessions_db.values() if s.get("user_id") == user["user_id"]]
        
        return JSONResponse(content={
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "storage": storage_info,
            "points": user_points,
            "sessions_count": len(user_sessions),
            "created_at": users_db[user["user_id"]].get("created_at"),
            "last_login": users_db[user["user_id"]].get("last_login")
        })
        
    except Exception as e:
        logger.error(f"사용자 통계 조회 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "통계 조회 중 오류가 발생했습니다."}
        )

@app.get("/api/user/info")
async def get_user_info(request: Request):
    """사용자 정보 조회"""
    user = require_auth(request)
    
    try:
        user_info = users_db.get(user["user_id"], {})
        return JSONResponse(content={
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "is_admin": user_info.get("is_admin", False),
            "is_active": user_info.get("is_active", True),
            "created_at": user_info.get("created_at"),
            "last_login": user_info.get("last_login")
        })
        
    except Exception as e:
        logger.error(f"사용자 정보 조회 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "사용자 정보 조회 중 오류가 발생했습니다."}
        )

@app.get("/api/user/activity")
async def get_user_activity(request: Request):
    """사용자 활동 내역"""
    user = require_auth(request)
    
    try:
        # 최근 채팅 세션
        user_sessions = [s for s in sessions_db.values() if s.get("user_id") == user["user_id"]]
        recent_sessions = sorted(user_sessions, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
        
        # 최근 포인트 활동
        user_points = points_db.get(user["user_id"], {})
        recent_points = user_points.get("history", [])[-5:] if user_points else []
        
        return JSONResponse(content={
            "recent_sessions": recent_sessions,
            "recent_points": recent_points
        })
        
    except Exception as e:
        logger.error(f"사용자 활동 조회 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "활동 내역 조회 중 오류가 발생했습니다."}
        )

@app.get("/api/admin/users")
async def get_all_users(request: Request):
    """관리자: 모든 사용자 목록"""
    admin = require_admin(request)
    
    try:
        users_list = []
        for user in users_db.values():
            users_list.append({
                "user_id": user["user_id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
                "is_active": user["is_active"],
                "created_at": user["created_at"],
                "last_login": user["last_login"],
                "storage": calculate_storage_usage(user["user_id"])
            })
        
        return JSONResponse(content={"users": users_list})
        
    except Exception as e:
        logger.error(f"사용자 목록 조회 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "사용자 목록 조회 중 오류가 발생했습니다."}
        )

@app.put("/api/admin/users/{user_id}/role")
async def update_user_role(request: Request, user_id: str, role: str):
    """관리자: 사용자 권한 변경"""
    admin = require_admin(request)
    
    try:
        if user_id not in users_db:
            return JSONResponse(
                status_code=404,
                content={"error": "사용자를 찾을 수 없습니다."}
            )
        
        if role not in ["user", "admin"]:
            return JSONResponse(
                status_code=400,
                content={"error": "유효하지 않은 권한입니다."}
            )
        
        users_db[user_id]["role"] = role
        logger.info(f"✅ 사용자 권한 변경: {user_id} -> {role}")
        
        return JSONResponse(content={"message": "권한이 변경되었습니다."})
        
    except Exception as e:
        logger.error(f"사용자 권한 변경 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "권한 변경 중 오류가 발생했습니다."}
        )

@app.delete("/api/admin/users/{user_id}")
async def delete_user(request: Request, user_id: str):
    """관리자: 사용자 삭제"""
    admin = require_admin(request)
    
    try:
        if user_id not in users_db:
            return JSONResponse(
                status_code=404,
                content={"error": "사용자를 찾을 수 없습니다."}
            )
        
        if user_id == admin["user_id"]:
            return JSONResponse(
                status_code=400,
                content={"error": "자신의 계정은 삭제할 수 없습니다."}
            )
        
        # 사용자 관련 데이터 삭제
        del users_db[user_id]
        if user_id in points_db:
            del points_db[user_id]
        
        # 관련 세션 삭제
        sessions_to_delete = [sid for sid, session in sessions_db.items() if session.get("user_id") == user_id]
        for sid in sessions_to_delete:
            del sessions_db[sid]
        
        logger.info(f"✅ 사용자 삭제: {user_id}")
        return JSONResponse(content={"message": "사용자가 삭제되었습니다."})
        
    except Exception as e:
        logger.error(f"사용자 삭제 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "사용자 삭제 중 오류가 발생했습니다."}
        )

@app.post("/api/sessions")
async def create_session(request: Request):
    """채팅 세션 생성"""
    user = get_current_user(request)
    
    try:
        session_id = generate_session_id()
        session_data = {
            "session_id": session_id,
            "user_id": user["user_id"] if user else "anonymous",
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "message_count": 0
        }
        
        sessions_db[session_id] = session_data
        chat_history[session_id] = []
        
        logger.info(f"✅ 새 채팅 세션 생성: {session_id}")
        return JSONResponse(content={"session_id": session_id})
        
    except Exception as e:
        logger.error(f"세션 생성 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "세션 생성 중 오류가 발생했습니다."}
        )

@app.post("/api/chat")
async def chat_endpoint(request: Request, chat_data: ChatMessage):
    """채팅 API"""
    user = get_current_user(request)
    user_id = user["user_id"] if user else "anonymous"
    
    try:
        logger.info(f"💬 채팅 요청 - 사용자: {user_id}, 메시지: {chat_data.message[:20]}...")
        
        # EORA Core를 사용한 응답 생성
        try:
            response = eora_core.process_input(chat_data.message, user_id)
        except Exception as e:
            logger.error(f"EORA Core 처리 실패: {e}")
            response = "죄송합니다. 현재 응답을 생성할 수 없습니다. 잠시 후 다시 시도해주세요."
        
        # 채팅 기록 저장
        if chat_data.session_id and chat_data.session_id in chat_history:
            chat_history[chat_data.session_id].append({
                "user": user_id,
                "message": chat_data.message,
                "response": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # 세션 업데이트
            if chat_data.session_id in sessions_db:
                sessions_db[chat_data.session_id]["message_count"] += 1
                sessions_db[chat_data.session_id]["last_activity"] = datetime.now().isoformat()
        
        return JSONResponse(content={
            "response": response,
            "session_id": chat_data.session_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"채팅 처리 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "채팅 처리 중 오류가 발생했습니다."}
        )

@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(request: Request, session_id: str):
    """세션 메시지 조회"""
    user = get_current_user(request)  # 인증 없이도 접근 가능하도록 수정
    
    try:
        if session_id not in chat_history:
            return JSONResponse(content={"messages": []})
        
        return JSONResponse(content={"messages": chat_history[session_id]})
        
    except Exception as e:
        logger.error(f"세션 메시지 조회 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "메시지 조회 중 오류가 발생했습니다."}
        )

@app.get("/api/sessions")
async def get_sessions(request: Request):
    """사용자 세션 목록 조회"""
    user = get_current_user(request)
    user_id = user["user_id"] if user else "anonymous"
    
    try:
        user_sessions = [s for s in sessions_db.values() if s.get("user_id") == user_id]
        return JSONResponse(content={"sessions": user_sessions})
        
    except Exception as e:
        logger.error(f"세션 목록 조회 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "세션 목록 조회 중 오류가 발생했습니다."}
        )

@app.get("/api/user/points/{user_id}")
async def get_user_points(request: Request, user_id: str):
    """사용자 포인트 조회"""
    user = require_auth(request)
    
    try:
        user_points = points_db.get(user_id, {
            "user_id": user_id,
            "current_points": 0,
            "total_earned": 0,
            "total_spent": 0,
            "last_updated": datetime.now().isoformat(),
            "history": []
        })
        
        return JSONResponse(content=user_points)
        
    except Exception as e:
        logger.error(f"포인트 조회 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "포인트 조회 중 오류가 발생했습니다."}
        )

@app.get("/api/aura/memory/stats")
async def get_aura_memory_stats(request: Request):
    """AURA 메모리 통계"""
    user = require_auth(request)
    
    try:
        # 사용자의 모든 세션에서 메시지 수 계산
        user_sessions = [s for s in sessions_db.values() if s.get("user_id") == user["user_id"]]
        total_messages = sum(s.get("message_count", 0) for s in user_sessions)
        
        return JSONResponse(content={
            "total_sessions": len(user_sessions),
            "total_messages": total_messages,
            "active_sessions": len([s for s in user_sessions if s.get("last_activity")]),
            "memory_usage": calculate_storage_usage(user["user_id"])
        })
        
    except Exception as e:
        logger.error(f"AURA 메모리 통계 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "메모리 통계 조회 중 오류가 발생했습니다."}
        )

@app.get("/api/aura/recall")
async def get_aura_recall(request: Request):
    """AURA 회상 기능"""
    user = require_auth(request)
    
    try:
        # 사용자의 최근 대화 기록
        user_sessions = [s for s in sessions_db.values() if s.get("user_id") == user["user_id"]]
        recent_messages = []
        
        for session in user_sessions[-3:]:  # 최근 3개 세션
            session_id = session["session_id"]
            if session_id in chat_history:
                recent_messages.extend(chat_history[session_id][-5:])  # 각 세션의 최근 5개 메시지
        
        return JSONResponse(content={
            "recent_messages": recent_messages,
            "total_sessions": len(user_sessions)
        })
        
    except Exception as e:
        logger.error(f"AURA 회상 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "회상 기능 처리 중 오류가 발생했습니다."}
        )

@app.post("/api/messages")
async def save_message(request: Request):
    """메시지 저장"""
    user = get_current_user(request)
    user_id = user["user_id"] if user else "anonymous"
    
    try:
        data = await request.json()
        message = data.get("message", "")
        session_id = data.get("session_id", "")
        
        if session_id and session_id in chat_history:
            chat_history[session_id].append({
                "user": user_id,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # 세션 업데이트
            if session_id in sessions_db:
                sessions_db[session_id]["message_count"] += 1
                sessions_db[session_id]["last_activity"] = datetime.now().isoformat()
        
        return JSONResponse(content={"status": "success"})
        
    except Exception as e:
        logger.error(f"메시지 저장 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "메시지 저장 중 오류가 발생했습니다."}
        )

@app.post("/api/set-language")
async def set_language(request: Request):
    """언어 설정"""
    user = get_current_user(request)
    
    try:
        data = await request.json()
        language = data.get("language", "ko")
        
        if user:
            # 사용자 언어 설정 저장
            user["language"] = language
        
        return JSONResponse(content={"status": "success", "language": language})
        
    except Exception as e:
        logger.error(f"언어 설정 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "언어 설정 중 오류가 발생했습니다."}
        )

@app.get("/points")
async def points_page(request: Request):
    """포인트 페이지"""
    user = require_auth(request)
    return templates.TemplateResponse("points.html", {"request": request, "user": user})

# 시스템 상태 확인
@app.get("/health")
async def health_check():
    """시스템 상태 확인"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/status")
async def api_status():
    """API 상태 확인"""
    return {
        "status": "running",
        "version": "2.0.0",
        "users_count": len(users_db),
        "sessions_count": len(sessions_db),
        "timestamp": datetime.now().isoformat()
    }

# 새로운 관리자 API 엔드포인트들

@app.get("/api/admin/overview")
async def get_admin_overview(request: Request):
    """관리자: 시스템 개요"""
    admin = require_admin(request)
    
    try:
        total_users = len(users_db)
        total_conversations = len(chat_history)
        total_points = sum(user.get("points", {}).get("current_points", 0) for user in users_db.values())
        active_sessions = len([s for s in sessions_db.values() if s.get("is_active", False)])
        
        return JSONResponse(content={
            "total_users": total_users,
            "total_conversations": total_conversations,
            "total_points": total_points,
            "active_sessions": active_sessions
        })
        
    except Exception as e:
        logger.error(f"관리자 개요 조회 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "개요 데이터 조회 중 오류가 발생했습니다."}
        )

@app.get("/api/admin/points")
async def get_admin_points(request: Request):
    """관리자 포인트 관리 데이터"""
    user = require_admin(request)
    
    try:
        # 모든 사용자의 포인트 정보 수집
        users_with_points = []
        total_points = 0
        active_users = 0
        
        for user_id, user_data in users_db.items():
            user_points = points_db.get(user_id, {
                "current_points": 0,
                "total_earned": 0,
                "total_spent": 0,
                "last_updated": datetime.now().isoformat()
            })
            
            total_points += user_points["current_points"]
            if user_data.get("is_active"):
                active_users += 1
            
            users_with_points.append({
                "user_id": user_id,
                "name": user_data.get("name", "Unknown"),
                "email": user_data.get("email", ""),
                "current_points": user_points["current_points"],
                "total_earned": user_points["total_earned"],
                "total_spent": user_points["total_spent"],
                "last_updated": user_points["last_updated"]
            })
        
        # 평균 포인트 계산
        average_points = total_points / len(users_with_points) if users_with_points else 0
        
        # 최고 포인트 사용자 찾기
        top_user_points = max([u["current_points"] for u in users_with_points]) if users_with_points else 0
        
        return JSONResponse(content={
            "total_points": total_points,
            "active_users": active_users,
            "average_points": round(average_points, 2),
            "top_user_points": top_user_points,
            "users": users_with_points
        })
        
    except Exception as e:
        logger.error(f"관리자 포인트 데이터 조회 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "포인트 데이터 조회 중 오류가 발생했습니다."}
        )

@app.get("/api/admin/repository")
async def get_admin_repository(request: Request):
    """관리자 저장소 관리 데이터"""
    user = require_admin(request)
    
    try:
        # 모든 사용자의 저장소 사용량 수집
        users_with_storage = []
        total_storage = 0
        total_files = 0
        active_users = 0
        storage_warnings = 0
        
        for user_id, user_data in users_db.items():
            storage_used = user_data.get("storage_used", 0)
            max_storage = user_data.get("max_storage", 100 * 1024 * 1024)  # 100MB
            usage_percentage = (storage_used / max_storage) * 100 if max_storage > 0 else 0
            
            total_storage += storage_used
            if user_data.get("is_active"):
                active_users += 1
            if usage_percentage > 70:
                storage_warnings += 1
            
            users_with_storage.append({
                "user_id": user_id,
                "name": user_data.get("name", "Unknown"),
                "email": user_data.get("email", ""),
                "storage_used": storage_used,
                "max_storage": max_storage,
                "usage_percentage": round(usage_percentage, 2)
            })
        
        # 샘플 파일 데이터 (실제로는 파일 시스템에서 가져와야 함)
        sample_files = [
            {
                "id": "file_001",
                "name": "document.pdf",
                "type": "pdf",
                "size": 1024 * 1024,  # 1MB
                "owner": "user_001",
                "upload_date": datetime.now().isoformat()
            },
            {
                "id": "file_002", 
                "name": "image.jpg",
                "type": "image",
                "size": 512 * 1024,  # 512KB
                "owner": "user_002",
                "upload_date": datetime.now().isoformat()
            }
        ]
        
        return JSONResponse(content={
            "total_storage": total_storage,
            "total_files": len(sample_files),
            "active_users": active_users,
            "storage_warnings": storage_warnings,
            "users": users_with_storage,
            "files": sample_files
        })
        
    except Exception as e:
        logger.error(f"관리자 저장소 데이터 조회 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "저장소 데이터 조회 중 오류가 발생했습니다."}
        )

@app.get("/api/admin/auto-learning")
async def get_admin_auto_learning(request: Request):
    """관리자: 자동학습 관리"""
    admin = require_admin(request)
    
    try:
        # 학습 로그 샘플 데이터
        learning_logs = [
            {
                "timestamp": datetime.now().isoformat(),
                "type": "자동학습",
                "processed_data": 150,
                "accuracy": 87.5,
                "status": "완료"
            },
            {
                "timestamp": (datetime.now() - timedelta(hours=24)).isoformat(),
                "type": "수동학습",
                "processed_data": 200,
                "accuracy": 89.2,
                "status": "완료"
            }
        ]
        
        return JSONResponse(content={
            "accuracy": learning_settings_db["accuracy"],
            "progress": learning_settings_db["progress"],
            "last_learning": learning_settings_db["last_learning"],
            "learning_logs": learning_logs
        })
        
    except Exception as e:
        logger.error(f"자동학습 관리 조회 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "자동학습 데이터 조회 중 오류가 발생했습니다."}
        )

@app.get("/api/admin/attachment-learning")
async def get_admin_attachment_learning(request: Request):
    """관리자: 첨부학습 관리"""
    admin = require_admin(request)
    
    try:
        total_attachments = len(attachments_db)
        processed_attachments = len([a for a in attachments_db if a.get("status") == "완료"])
        success_rate = (processed_attachments / total_attachments * 100) if total_attachments > 0 else 0
        
        # 샘플 첨부파일 데이터
        attachments = [
            {
                "_id": "att_001",
                "filename": "학습자료.pdf",
                "category": "교육",
                "size": 1048576,
                "upload_date": datetime.now().isoformat(),
                "status": "완료",
                "processing_time": "2분 30초"
            },
            {
                "_id": "att_002",
                "filename": "기술문서.docx",
                "category": "기술",
                "size": 512000,
                "upload_date": datetime.now().isoformat(),
                "status": "처리 중",
                "processing_time": "-"
            }
        ]
        
        return JSONResponse(content={
            "total_attachments": total_attachments,
            "processed_attachments": processed_attachments,
            "success_rate": round(success_rate, 1),
            "attachments": attachments
        })
        
    except Exception as e:
        logger.error(f"첨부학습 관리 조회 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "첨부학습 데이터 조회 중 오류가 발생했습니다."}
        )

@app.get("/api/admin/system-status")
async def get_admin_system_status(request: Request):
    """관리자: 시스템 상태"""
    admin = require_admin(request)
    
    try:
        # 시스템 상태 샘플 데이터
        system_status = {
            "mongodb": True,
            "redis": False,
            "openai": True,
            "cpu_usage": "23%",
            "memory_usage": "45%",
            "disk_usage": "67%",
            "network_status": "정상"
        }
        
        return JSONResponse(content=system_status)
        
    except Exception as e:
        logger.error(f"시스템 상태 조회 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "시스템 상태 조회 중 오류가 발생했습니다."}
        )

@app.get("/api/admin/logs")
async def get_admin_logs(request: Request):
    """관리자: 시스템 로그"""
    admin = require_admin(request)
    
    try:
        # 샘플 로그 데이터
        logs = [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "사용자 로그인 성공: admin@eora.com",
                "user_email": "admin@eora.com"
            },
            {
                "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
                "level": "WARNING",
                "message": "Redis 연결 실패",
                "user_email": None
            },
            {
                "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat(),
                "level": "INFO",
                "message": "새 채팅 세션 생성",
                "user_email": "user@eora.com"
            }
        ]
        
        return JSONResponse(content={"logs": logs})
        
    except Exception as e:
        logger.error(f"시스템 로그 조회 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "로그 데이터 조회 중 오류가 발생했습니다."}
        )

@app.post("/api/admin/learning-settings")
async def update_learning_settings(request: Request, settings: LearningSettings):
    """관리자: 자동학습 설정 업데이트"""
    admin = require_admin(request)
    
    try:
        learning_settings_db.update({
            "interval": settings.interval,
            "threshold": settings.threshold,
            "enabled": settings.enabled
        })
        
        logger.info(f"✅ 자동학습 설정 업데이트: {admin['email']}")
        return JSONResponse(content={"message": "학습 설정이 업데이트되었습니다."})
        
    except Exception as e:
        logger.error(f"자동학습 설정 업데이트 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "학습 설정 업데이트 중 오류가 발생했습니다."}
        )

@app.post("/api/admin/start-learning")
async def start_manual_learning(request: Request):
    """관리자: 수동 학습 시작"""
    admin = require_admin(request)
    
    try:
        # 학습 로그 추가
        learning_log = {
            "timestamp": datetime.now().isoformat(),
            "type": "수동학습",
            "processed_data": 200,
            "accuracy": 89.2,
            "status": "진행 중"
        }
        learning_logs_db.append(learning_log)
        
        # 학습 설정 업데이트
        learning_settings_db["last_learning"] = datetime.now().isoformat()
        learning_settings_db["progress"] = min(100, learning_settings_db["progress"] + 5)
        
        logger.info(f"✅ 수동 학습 시작: {admin['email']}")
        return JSONResponse(content={"message": "수동 학습이 시작되었습니다."})
        
    except Exception as e:
        logger.error(f"수동 학습 시작 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "수동 학습 시작 중 오류가 발생했습니다."}
        )

# 시스템 시작 시 초기화
@app.on_event("startup")
async def startup_event():
    """시스템 시작 시 실행"""
    logger.info("🚀 EORA AI 시스템 시작 중...")
    initialize_system()
    logger.info("🚀 EORA AI 시스템이 성공적으로 시작되었습니다!")

# 시스템 종료 시 정리
@app.on_event("shutdown")
async def shutdown_event():
    """시스템 종료 시 실행"""
    logger.info("✅ 시스템 종료 중...")

import os
import json

PROMPT_JSON_PATH = os.path.join(os.path.dirname(__file__), 'ai_brain', 'ai_prompts.json')

def load_prompts_from_file():
    """ai_brain/ai_prompts.json 파일에서 프롬프트 로드"""
    try:
        if not os.path.exists(PROMPT_JSON_PATH):
            logger.warning("ai_brain/ai_prompts.json 파일을 찾을 수 없습니다.")
            return []
            
        with open(PROMPT_JSON_PATH, 'r', encoding='utf-8') as f:
            prompts_data = json.load(f)
            
        # JSON 구조를 프롬프트 목록으로 변환
        prompts = []
        for ai_name, ai_data in prompts_data.items():
            for category, content_list in ai_data.items():
                if isinstance(content_list, list):
                    for i, content in enumerate(content_list):
                        prompt = {
                            "id": f"{ai_name}_{category}_{i}",
                            "name": f"{ai_name.upper()} - {category}",
                            "category": category,
                            "content": content,
                            "description": f"{ai_name.upper()}의 {category} 프롬프트",
                            "tags": [ai_name, category],
                            "ai_name": ai_name,
                            "content_index": i
                        }
                        prompts.append(prompt)
        return prompts
    except Exception as e:
        logger.error(f"프롬프트 로드 오류: {e}")
        return []

def save_prompts_to_file(prompts):
    """ai_brain/ai_prompts.json 파일로 프롬프트 저장"""
    try:
        # 기존 파일 로드
        with open(PROMPT_JSON_PATH, 'r', encoding='utf-8') as f:
            prompts_data = json.load(f)
        
        # 프롬프트 목록을 JSON 구조로 변환
        for prompt in prompts:
            ai_name = prompt.get("ai_name")
            category = prompt.get("category")
            content_index = prompt.get("content_index", 0)
            content = prompt.get("content")
            
            if ai_name and category and content is not None:
                if ai_name not in prompts_data:
                    prompts_data[ai_name] = {}
                if category not in prompts_data[ai_name]:
                    prompts_data[ai_name][category] = []
                
                # 기존 배열 크기 확장
                while len(prompts_data[ai_name][category]) <= content_index:
                    prompts_data[ai_name][category].append("")
                
                prompts_data[ai_name][category][content_index] = content
        
        # 파일 저장
        with open(PROMPT_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(prompts_data, f, ensure_ascii=False, indent=2)
            
        logger.info("✅ ai_prompts.json 파일이 업데이트되었습니다.")
    except Exception as e:
        logger.error(f"프롬프트 저장 오류: {e}")

@app.get("/api/prompts")
async def get_prompts():
    """프롬프트 목록 조회"""
    prompts = load_prompts_from_file()
    return JSONResponse(content=prompts)

@app.post("/api/prompts")
async def add_prompt(prompt: Prompt):
    """새 프롬프트 추가"""
    prompts = load_prompts_from_file()
    
    # AI 이름 추출 (ai_name 필드 사용)
    ai_name = getattr(prompt, 'ai_name', None)
    if not ai_name:
        # 태그에서 AI 이름 추출 (하위 호환성)
        ai_name = prompt.tags[0] if prompt.tags else "ai1"
    
    category = prompt.category
    
    # 해당 AI의 카테고리에서 최대 인덱스 찾기
    max_index = 0
    for p in prompts:
        if p.get("ai_name") == ai_name and p.get("category") == category:
            max_index = max(max_index, p.get("content_index", 0) + 1)
    
    # 새 프롬프트 정보 설정
    new_prompt = prompt.dict()
    new_prompt["ai_name"] = ai_name
    new_prompt["content_index"] = max_index
    new_prompt["id"] = f"{ai_name}_{category}_{max_index}"
    
    prompts.append(new_prompt)
    save_prompts_to_file(prompts)
    
    logger.info(f"✅ 새 프롬프트 추가: {ai_name} - {category}")
    return JSONResponse(content={"message": "프롬프트가 추가되었습니다.", "prompt": new_prompt})

@app.put("/api/prompts/{prompt_id}")
async def update_prompt(prompt_id: str, prompt: Prompt):
    """프롬프트 수정"""
    prompts = load_prompts_from_file()
    for i, p in enumerate(prompts):
        if p["id"] == prompt_id:
            # AI 이름 추출 (ai_name 필드 사용)
            ai_name = getattr(prompt, 'ai_name', None)
            if not ai_name:
                ai_name = p.get("ai_name", "ai1")
            
            content_index = p.get("content_index", 0)
            
            updated_prompt = prompt.dict()
            updated_prompt["ai_name"] = ai_name
            updated_prompt["content_index"] = content_index
            updated_prompt["id"] = prompt_id  # ID 유지
            
            prompts[i] = updated_prompt
            save_prompts_to_file(prompts)
            
            logger.info(f"✅ 프롬프트 수정: {prompt_id}")
            return JSONResponse(content={"message": "프롬프트가 수정되었습니다."})
    
    return JSONResponse(status_code=404, content={"error": "프롬프트를 찾을 수 없습니다."})

@app.delete("/api/prompts/{prompt_id}")
async def delete_prompt(prompt_id: str):
    """프롬프트 삭제"""
    prompts = load_prompts_from_file()
    original_length = len(prompts)
    prompts = [p for p in prompts if p["id"] != prompt_id]
    
    if len(prompts) < original_length:
        save_prompts_to_file(prompts)
        logger.info(f"✅ 프롬프트 삭제: {prompt_id}")
        return JSONResponse(content={"message": "프롬프트가 삭제되었습니다."})
    
    return JSONResponse(status_code=404, content={"error": "프롬프트를 찾을 수 없습니다."})

@app.post("/api/prompts/category")
async def save_category_prompts(category_data: CategoryPromptData):
    """카테고리별 프롬프트 저장"""
    try:
        # 기존 프롬프트 파일 로드
        prompts = load_prompts_from_file()
        
        ai_name = category_data.ai_name
        category = category_data.category
        new_prompts = category_data.prompts
        
        # 해당 AI와 카테고리의 기존 프롬프트 제거
        prompts = [p for p in prompts if not (p.get("ai_name") == ai_name and p.get("category") == category)]
        
        # 새 프롬프트 추가
        for i, prompt_data in enumerate(new_prompts):
            content = prompt_data.get("content", "")
            if content.strip():  # 빈 내용이 아닌 경우만 추가
                new_prompt = {
                    "id": f"{ai_name}_{category}_{i}",
                    "name": f"{ai_name} {category} 프롬프트 {i+1}",
                    "category": category,
                    "content": content,
                    "description": f"{ai_name}의 {category} 프롬프트",
                    "tags": [ai_name, category],
                    "ai_name": ai_name,
                    "content_index": i
                }
                prompts.append(new_prompt)
        
        # 파일 저장
        save_prompts_to_file(prompts)
        
        logger.info(f"✅ {ai_name} {category} 카테고리 저장 완료: {len(new_prompts)}개 프롬프트")
        return JSONResponse(content={
            "message": f"{ai_name} {category} 카테고리가 저장되었습니다.",
            "saved_count": len(new_prompts)
        })
        
    except Exception as e:
        logger.error(f"카테고리 저장 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "카테고리 저장 중 오류가 발생했습니다."}
        )

# WebSocket 연결 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)

manager = ConnectionManager()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 간단한 에코 응답
            response_data = {
                "type": "message",
                "session_id": session_id,
                "message": f"Echo: {data}",
                "timestamp": datetime.now().isoformat()
            }
            await manager.send_personal_message(json.dumps(response_data), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket 오류: {e}")
        manager.disconnect(websocket)

# 에러 처리 및 응답 헬퍼 함수들
def create_success_response(data: Any = None, message: str = "성공") -> JSONResponse:
    """성공 응답 생성"""
    response_data = {
        "success": True,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    if data is not None:
        response_data["data"] = data
    return JSONResponse(content=response_data)

def create_error_response(message: str, status_code: int = 400, error_code: str = None) -> JSONResponse:
    """에러 응답 생성"""
    response_data = {
        "success": False,
        "error": message,
        "timestamp": datetime.now().isoformat()
    }
    if error_code:
        response_data["error_code"] = error_code
    return JSONResponse(status_code=status_code, content=response_data)

def log_api_request(request: Request, user_id: str = None, action: str = ""):
    """API 요청 로깅"""
    user_info = f"user:{user_id}" if user_id else "anonymous"
    logger.info(f"🌐 API 요청 - {request.method} {request.url.path} - {user_info} - {action}")

def log_api_response(status_code: int, message: str = ""):
    """API 응답 로깅"""
    status_icon = "✅" if status_code < 400 else "❌"
    logger.info(f"{status_icon} API 응답 - {status_code} - {message}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002, reload=True) 