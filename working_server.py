#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI 작동하는 서버 - 메시지 저장 및 세션 관리 수정
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from typing import Optional, Dict, List, Any

# FastAPI 관련
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware

# Pydantic 모델
from pydantic import BaseModel

# 앱 초기화
app = FastAPI(title="EORA AI Working Server")

# 미들웨어 설정
app.add_middleware(SessionMiddleware, secret_key="eora-secret-key-2024")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

# 데이터 파일 경로
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json") 
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.json")
PROMPTS_FILE = os.path.join(DATA_DIR, "prompts.json")

# 데이터 디렉토리 생성
os.makedirs(DATA_DIR, exist_ok=True)

# 메모리 내 데이터베이스
users_db = {}
sessions_db = {}
messages_db = {}
prompts_db = {}

# ==================== 유틸리티 함수 ====================

def load_json_data(file_path, default=None):
    """JSON 파일에서 데이터 로드"""
    if default is None:
        default = {}
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"✅ {file_path} 로드 완료: {len(data)}개 항목")
                return data
        except Exception as e:
            print(f"⚠️ {file_path} 로드 오류: {e}")
    return default

def save_json_data(file_path, data):
    """JSON 파일에 데이터 저장"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 {file_path} 저장 완료: {len(data)}개 항목")
        return True
    except Exception as e:
        print(f"❌ {file_path} 저장 오류: {e}")
        return False

def get_current_user(request: Request):
    """현재 로그인한 사용자 정보 조회"""
    user_email = request.cookies.get("user_email")
    if user_email and user_email in users_db:
        return users_db[user_email]
    return None

# ==================== 데이터 로드 ====================

# 초기 데이터 로드
print("📂 데이터 파일 로드 중...")

users_db = load_json_data(USERS_FILE, {
    "admin@eora.ai": {
        "email": "admin@eora.ai",
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "name": "관리자",
        "role": "admin",
        "is_admin": True
    }
})

sessions_db = load_json_data(SESSIONS_FILE, {})
messages_db = load_json_data(MESSAGES_FILE, {})
prompts_db = load_json_data(PROMPTS_FILE, {})

# ==================== 페이지 라우트 ====================

@app.get("/")
async def home(request: Request):
    """홈페이지"""
    user = get_current_user(request)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "user": user
    })

@app.get("/login")
async def login_page(request: Request):
    """로그인 페이지"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/chat")
async def chat_page(request: Request):
    """채팅 페이지"""
    user = get_current_user(request)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "user": user
    })

@app.get("/admin")
async def admin_page(request: Request):
    """관리자 페이지"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return templates.TemplateResponse("login.html", {"request": request})
    
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "user": user
    })

# ==================== 인증 API ====================

@app.post("/api/auth/login")
async def auth_login(request: Request):
    """로그인 API"""
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="이메일과 비밀번호를 입력하세요.")
    
    # 사용자 확인
    user = users_db.get(email)
    if not user:
        raise HTTPException(status_code=401, detail="존재하지 않는 계정입니다.")
    
    # 비밀번호 확인
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if user["password"] != password_hash:
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")
    
    # 로그인 성공
    response = JSONResponse({
        "success": True,
        "user": {
            "email": user["email"],
            "name": user["name"],
            "is_admin": user.get("is_admin", False)
        }
    })
    
    # 쿠키 설정
    response.set_cookie("user_email", email, httponly=True)
    response.set_cookie("access_token", "dummy-token", httponly=True)
    
    print(f"✅ 로그인 성공: {email}")
    return response

@app.post("/api/auth/logout")
async def auth_logout(response: Response):
    """로그아웃 API"""
    response = JSONResponse({"success": True})
    response.delete_cookie("user_email")
    response.delete_cookie("access_token")
    return response

# ==================== 세션 API ====================

@app.get("/api/sessions")
async def get_sessions(request: Request):
    """사용자의 세션 목록 조회"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    # 사용자의 세션만 필터링
    user_sessions = []
    for session_id, session in sessions_db.items():
        if session.get("user_email") == user["email"]:
            # 메시지 수 계산
            message_count = len(messages_db.get(session_id, []))
            session_data = session.copy()
            session_data["message_count"] = message_count
            user_sessions.append(session_data)
    
    # 최신 순으로 정렬
    user_sessions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    print(f"📂 사용자 {user['email']}의 세션 목록: {len(user_sessions)}개")
    
    return JSONResponse({
        "success": True,
        "sessions": user_sessions
    })

@app.post("/api/sessions")
async def create_session(request: Request):
    """새 세션 생성"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    data = await request.json()
    session_name = data.get("name", f"대화 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # 세션 ID 생성
    timestamp = int(datetime.now().timestamp() * 1000)
    session_id = f"session_{user['email'].replace('@', '_').replace('.', '_')}_{timestamp}"
    
    # 세션 생성
    new_session = {
        "id": session_id,
        "user_email": user["email"],
        "name": session_name,
        "created_at": datetime.now().isoformat(),
        "message_count": 0
    }
    
    sessions_db[session_id] = new_session
    messages_db[session_id] = []
    
    # 저장
    save_json_data(SESSIONS_FILE, sessions_db)
    save_json_data(MESSAGES_FILE, messages_db)
    
    print(f"🆕 새 세션 생성: {user['email']} -> {session_id}")
    
    return JSONResponse({
        "success": True,
        "session": new_session
    })

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, request: Request):
    """세션 삭제"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    # 세션 존재 및 권한 확인
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    
    if sessions_db[session_id].get("user_email") != user["email"]:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    # 세션 및 메시지 삭제
    del sessions_db[session_id]
    if session_id in messages_db:
        del messages_db[session_id]
    
    # 저장
    save_json_data(SESSIONS_FILE, sessions_db)
    save_json_data(MESSAGES_FILE, messages_db)
    
    print(f"🗑️ 세션 삭제: {user['email']} -> {session_id}")
    
    return JSONResponse({"success": True})

# ==================== 메시지 API ====================

@app.get("/api/sessions/{session_id}/messages")
async def get_messages(session_id: str, request: Request):
    """세션의 메시지 목록 조회"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    # 세션 존재 및 권한 확인
    if session_id not in sessions_db:
        # 세션이 없으면 빈 메시지 반환
        return JSONResponse({
            "success": True,
            "messages": []
        })
    
    if sessions_db[session_id].get("user_email") != user["email"]:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    # 메시지 조회
    messages = messages_db.get(session_id, [])
    
    print(f"📥 세션 {session_id}의 메시지 로드: {len(messages)}개")
    
    return JSONResponse({
        "success": True,
        "messages": messages
    })

@app.post("/api/messages")
async def save_message(request: Request):
    """메시지 저장"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    data = await request.json()
    session_id = data.get("session_id")
    content = data.get("content") or data.get("message")
    role = data.get("role", "user")
    
    if not session_id or not content:
        raise HTTPException(status_code=400, detail="세션 ID와 메시지가 필요합니다.")
    
    # 세션이 없으면 자동 생성
    if session_id not in sessions_db:
        sessions_db[session_id] = {
            "id": session_id,
            "user_email": user["email"],
            "name": f"대화 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "created_at": datetime.now().isoformat(),
            "message_count": 0
        }
        messages_db[session_id] = []
        save_json_data(SESSIONS_FILE, sessions_db)
        print(f"🆕 메시지 저장 시 새 세션 자동 생성: {session_id}")
    
    # 권한 확인
    if sessions_db[session_id].get("user_email") != user["email"]:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    # 메시지 추가
    message = {
        "role": role,
        "content": content,
        "timestamp": data.get("timestamp", datetime.now().isoformat())
    }
    
    if session_id not in messages_db:
        messages_db[session_id] = []
    
    messages_db[session_id].append(message)
    
    # 세션의 메시지 카운트 업데이트
    sessions_db[session_id]["message_count"] = len(messages_db[session_id])
    
    # 저장
    save_json_data(MESSAGES_FILE, messages_db)
    save_json_data(SESSIONS_FILE, sessions_db)
    
    print(f"💾 메시지 저장: {session_id} -> {role} ({len(content)}자)")
    
    return JSONResponse({
        "success": True,
        "message": "메시지가 저장되었습니다."
    })

# ==================== 채팅 API ====================

@app.post("/api/chat")
async def chat(request: Request):
    """채팅 응답 생성"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    data = await request.json()
    session_id = data.get("session_id")
    message = data.get("message")
    
    if not session_id or not message:
        raise HTTPException(status_code=400, detail="세션 ID와 메시지가 필요합니다.")
    
    # 세션이 없으면 자동 생성
    if session_id not in sessions_db:
        sessions_db[session_id] = {
            "id": session_id,
            "user_email": user["email"],
            "name": f"대화 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "created_at": datetime.now().isoformat(),
            "message_count": 0
        }
        messages_db[session_id] = []
        save_json_data(SESSIONS_FILE, sessions_db)
        print(f"🆕 채팅 시 새 세션 자동 생성: {session_id}")
    
    # 사용자 메시지 저장
    user_message = {
        "role": "user",
        "content": message,
        "timestamp": datetime.now().isoformat()
    }
    
    if session_id not in messages_db:
        messages_db[session_id] = []
    
    messages_db[session_id].append(user_message)
    
    # AI 응답 생성 (간단한 응답)
    responses = [
        "안녕하세요! EORA AI입니다. 무엇을 도와드릴까요?",
        "좋은 질문이네요! 더 자세히 알려주시겠어요?",
        "흥미로운 주제입니다. 함께 탐구해보겠습니다.",
        "네, 이해했습니다. 계속 말씀해주세요.",
        "도움이 될 수 있도록 최선을 다하겠습니다!"
    ]
    
    import random
    ai_response = random.choice(responses)
    
    # AI 응답 저장
    ai_message = {
        "role": "assistant",
        "content": ai_response,
        "timestamp": datetime.now().isoformat()
    }
    
    messages_db[session_id].append(ai_message)
    
    # 세션의 메시지 카운트 업데이트
    sessions_db[session_id]["message_count"] = len(messages_db[session_id])
    
    # 저장
    save_json_data(MESSAGES_FILE, messages_db)
    save_json_data(SESSIONS_FILE, sessions_db)
    
    print(f"💬 채팅 응답: {session_id} -> {len(ai_response)}자")
    print(f"💾 세션의 총 메시지 수: {len(messages_db[session_id])}개")
    
    return JSONResponse({
        "success": True,
        "response": ai_response,
        "session_id": session_id
    })

# ==================== 기타 API ====================

@app.post("/api/set-language")
async def set_language(request: Request):
    """언어 설정"""
    data = await request.json()
    lang = data.get("lang", "ko")
    
    response = JSONResponse({"success": True, "lang": lang})
    response.set_cookie("lang", lang)
    
    return response

@app.get("/api/user/points")
async def get_user_points(request: Request):
    """사용자 포인트 조회"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({"points": 0})
    
    return JSONResponse({"points": 1000})

# ==================== 관리자 API ====================

@app.get("/api/admin/stats")
async def admin_stats(request: Request):
    """관리자 통계"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    total_messages = sum(len(msgs) for msgs in messages_db.values())
    
    return JSONResponse({
        "users": len(users_db),
        "sessions": len(sessions_db),
        "messages": total_messages
    })

# ==================== 서버 실행 ====================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 50)
    print("🚀 EORA AI 작동하는 서버 시작...")
    print("📍 접속 주소: http://127.0.0.1:8200")
    print("🔐 로그인: http://127.0.0.1:8200/login")
    print("💬 채팅: http://127.0.0.1:8200/chat")
    print("⚙️ 관리자: http://127.0.0.1:8200/admin")
    print("=" * 50)
    print("📧 관리자 계정: admin@eora.ai")
    print("🔑 비밀번호: admin123")
    print("=" * 50)
    
    uvicorn.run(app, host="127.0.0.1", port=8200) 