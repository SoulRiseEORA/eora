#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI 안정 서버 - 세션과 프롬프트 기능 완벽 구현
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import uuid

try:
    import uvicorn
    from fastapi import FastAPI, Request, Response, HTTPException, Depends, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    import jwt
    print("✅ 모든 모듈 로드 성공")
except ImportError as e:
    print(f"❌ 모듈 로드 실패: {e}")
    print("필요한 패키지 설치: pip install fastapi uvicorn jinja2 python-multipart PyJWT")
    sys.exit(1)

# OpenAI 클라이언트 설정
openai_client = None
try:
    import openai
    from openai import OpenAI
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        openai_client = OpenAI(api_key=api_key)
        print("✅ OpenAI 클라이언트 초기화 성공")
    else:
        print("⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("💡 GPT 응답 없이 기본 응답만 제공됩니다.")
except ImportError:
    print("⚠️ OpenAI 패키지가 설치되지 않았습니다.")
    print("💡 설치: pip install openai")

# FastAPI 앱 생성
app = FastAPI(title="EORA AI 안정 서버")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 템플릿 및 정적 파일 설정
templates_dir = os.path.join(os.path.dirname(__file__), "src", "templates")
static_dir = os.path.join(os.path.dirname(__file__), "src", "static")

if os.path.exists(templates_dir):
    templates = Jinja2Templates(directory=templates_dir)
    print(f"✅ 템플릿 디렉토리: {templates_dir}")
else:
    print(f"❌ 템플릿 디렉토리 없음: {templates_dir}")
    sys.exit(1)

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    print(f"✅ 정적 파일 마운트: {static_dir}")

# chat_mockup.png 파일 경로 설정
chat_mockup_path = os.path.join(static_dir, "chat_mockup.png")
if not os.path.exists(chat_mockup_path):
    # 상위 디렉토리에서 찾기
    alt_path = os.path.join(os.path.dirname(__file__), "chat_mockup.png")
    if os.path.exists(alt_path):
        chat_mockup_path = alt_path

# JWT 설정
SECRET_KEY = "your-secret-key-for-jwt-encoding"
ALGORITHM = "HS256"

# 데이터 저장 디렉토리
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    print(f"✅ 데이터 디렉토리 생성: {DATA_DIR}")

# 세션 데이터 파일
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

# 데이터 로드 함수
def load_json_data(file_path, default=None):
    """JSON 파일에서 데이터 로드"""
    if default is None:
        default = {}
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ {file_path} 로드 오류: {e}")
    return default

# 데이터 저장 함수
def save_json_data(file_path, data):
    """JSON 파일에 데이터 저장"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ {file_path} 저장 오류: {e}")
        return False

# 데이터 로드
users_db = load_json_data(USERS_FILE, {
    "admin@eora.ai": {
        "email": "admin@eora.ai",
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "name": "관리자",
        "role": "admin",
        "is_admin": True
    },
    "test@eora.ai": {
        "email": "test@eora.ai",
        "password": hashlib.sha256("test123".encode()).hexdigest(),
        "name": "테스트 사용자",
        "role": "user",
        "is_admin": False
    }
})

sessions_db = load_json_data(SESSIONS_FILE, {})
messages_db = load_json_data(MESSAGES_FILE, {})

# 프롬프트 데이터 로드
prompts_data = {}
prompts_file_paths = [
    os.path.join(os.path.dirname(__file__), "ai_prompts.json"),
    os.path.join(os.path.dirname(__file__), "src", "ai_prompts.json"),
    os.path.join(os.path.dirname(__file__), "src", "templates", "ai_prompts.json"),
    os.path.join(os.path.dirname(__file__), "src", "ai_brain", "ai_prompts.json")
]

def load_prompts():
    """프롬프트 데이터 로드"""
    global prompts_data
    for path in prompts_file_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    prompts_data = json.load(f)
                    print(f"✅ 프롬프트 데이터 로드 성공: {path}")
                    print(f"   로드된 AI: {', '.join(prompts_data.keys())}")
                    # ai1이 문자열인지 확인
                    if "ai1" in prompts_data:
                        if isinstance(prompts_data["ai1"].get("system"), str):
                            print("   ✅ ai1 system은 문자열 형식입니다")
                    return True
            except Exception as e:
                print(f"❌ 프롬프트 로드 오류 ({path}): {e}")
    
    print("⚠️ 프롬프트 파일을 찾을 수 없습니다")
    # 기본 프롬프트 데이터
    prompts_data = {
        "ai1": {
            "system": "AI1 시스템 프롬프트",
            "role": ["AI1 역할"],
            "guide": ["AI1 가이드"],
            "format": ["AI1 포맷"]
        }
    }
    return False

# 프롬프트 로드
load_prompts()

# 인증 헬퍼 함수
def get_current_user(request: Request) -> Optional[Dict]:
    """현재 로그인한 사용자 정보 반환"""
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        if email and email in users_db:
            user = users_db[email].copy()
            # 관리자 여부 확인
            user["is_admin"] = user.get("is_admin", False) or user.get("role") == "admin" or email == "admin@eora.ai"
            return user
    except:
        pass
    
    return None

# ==================== 페이지 라우트 ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """홈페이지"""
    user = get_current_user(request)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "user": user
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """로그인 페이지"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """회원가입 페이지"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """관리자 페이지"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "user": user
    })

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """채팅 페이지"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "user": user
    })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """대시보드 페이지"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user
    })

@app.get("/prompt_management", response_class=HTMLResponse)
async def prompt_management_page(request: Request):
    """프롬프트 관리 페이지"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("prompt_management.html", {
        "request": request,
        "user": user
    })

# chat_mockup.png 서빙
@app.get("/chat_mockup.png")
async def serve_chat_mockup():
    if os.path.exists(chat_mockup_path):
        return FileResponse(chat_mockup_path)
    else:
        raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다")

# ==================== 인증 API ====================

@app.post("/api/auth/register")
async def register_api(request: Request):
    """회원가입 API"""
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        name = data.get("name")
        
        if not email or not password or not name:
            return JSONResponse(
                {"success": False, "message": "모든 필드를 입력해주세요."},
                status_code=400
            )
        
        if email in users_db:
            return JSONResponse(
                {"success": False, "message": "이미 사용 중인 이메일입니다."},
                status_code=400
            )
        
        # 새 사용자 생성
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        users_db[email] = {
            "email": email,
            "password": password_hash,
            "name": name,
            "role": "user",
            "is_admin": False,
            "created_at": datetime.now().isoformat()
        }
        
        # 사용자 데이터 저장
        save_json_data(USERS_FILE, users_db)
        print(f"✅ 회원가입 성공: {email}")
        
        # 자동 로그인
        access_token = jwt.encode(
            {
                "email": email,
                "exp": datetime.utcnow() + timedelta(days=1)
            },
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        
        return JSONResponse({
            "success": True,
            "message": "회원가입이 완료되었습니다.",
            "user": {
                "email": email,
                "name": name,
                "role": "user",
                "is_admin": False
            },
            "access_token": access_token
        })
        
    except Exception as e:
        print(f"❌ 회원가입 오류: {e}")
        return JSONResponse(
            {"success": False, "message": str(e)},
            status_code=500
        )

@app.post("/api/auth/login")
async def login_api(request: Request):
    """로그인 API"""
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        
        print(f"🔐 로그인 시도: {email}")
        
        if email in users_db:
            user = users_db[email]
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if user["password"] == password_hash:
                # JWT 토큰 생성
                access_token = jwt.encode(
                    {
                        "email": email,
                        "exp": datetime.utcnow() + timedelta(days=1)
                    },
                    SECRET_KEY,
                    algorithm=ALGORITHM
                )
                
                print(f"✅ 로그인 성공: {email}")
                
                response = JSONResponse({
                    "success": True,
                    "message": "로그인 성공",
                    "user": {
                        "email": user["email"],
                        "name": user["name"],
                        "role": user.get("role", "user"),
                        "is_admin": user.get("is_admin", False) or email == "admin@eora.ai"
                    },
                    "access_token": access_token
                })
                
                # 쿠키 설정
                response.set_cookie(
                    key="access_token",
                    value=access_token,
                    httponly=True,
                    max_age=86400,
                    path="/"
                )
                response.set_cookie(
                    key="user_email",
                    value=email,
                    max_age=86400,
                    path="/"
                )
                
                return response
            else:
                print(f"❌ 비밀번호 불일치: {email}")
        else:
            print(f"❌ 사용자 없음: {email}")
        
        return JSONResponse(
            {"success": False, "message": "이메일 또는 비밀번호가 올바르지 않습니다."},
            status_code=401
        )
        
    except Exception as e:
        print(f"❌ 로그인 오류: {e}")
        return JSONResponse(
            {"success": False, "message": str(e)},
            status_code=500
        )

# 로그인 호환성 엔드포인트
@app.post("/api/login")
async def login_api_compat(request: Request):
    return await login_api(request)

@app.post("/api/admin/login")
async def admin_login_api(request: Request):
    return await login_api(request)

@app.post("/api/auth/logout")
async def logout_api():
    """로그아웃 API"""
    response = JSONResponse({"success": True, "message": "로그아웃되었습니다."})
    response.delete_cookie("access_token")
    response.delete_cookie("user_email")
    return response

# ==================== 세션 관리 API ====================

@app.get("/api/sessions")
async def get_sessions(request: Request):
    """세션 목록 조회"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({"sessions": []})
    
    user_email = user["email"]
    user_sessions = []
    
    # 사용자의 세션만 필터링
    for session_id, session_data in sessions_db.items():
        if session_data.get("user_email") == user_email:
            # 메시지 개수 계산
            message_count = len(messages_db.get(session_id, []))
            user_sessions.append({
                "id": session_id,
                "name": session_data.get("name", f"세션 {len(user_sessions) + 1}"),
                "created_at": session_data.get("created_at", datetime.now().isoformat()),
                "message_count": message_count
            })
    
    # 생성일 기준 정렬 (최신순)
    user_sessions.sort(key=lambda x: x["created_at"], reverse=True)
    
    print(f"📂 사용자 {user_email}의 세션 목록: {len(user_sessions)}개")
    return JSONResponse({"sessions": user_sessions})

@app.post("/api/sessions")
async def create_session(request: Request):
    """새 세션 생성"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    try:
        data = await request.json()
        session_name = data.get("name", "")
    except:
        session_name = ""
    
    user_email = user["email"]
    timestamp = int(datetime.now().timestamp() * 1000)
    session_id = f"session_{user_email.replace('@', '_').replace('.', '_')}_{timestamp}"
    
    # 세션 생성
    sessions_db[session_id] = {
        "id": session_id,
        "user_email": user_email,
        "name": session_name or f"새 대화 {timestamp}",
        "created_at": datetime.now().isoformat()
    }
    
    # 빈 메시지 배열 생성
    messages_db[session_id] = []
    
    # 데이터 저장
    save_json_data(SESSIONS_FILE, sessions_db)
    save_json_data(MESSAGES_FILE, messages_db)
    
    print(f"🆕 새 세션 생성: {user_email} -> {session_id}")
    
    return JSONResponse({
        "success": True,
        "session": {
            "id": session_id,
            "name": sessions_db[session_id]["name"],
            "created_at": sessions_db[session_id]["created_at"]
        }
    })

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, request: Request):
    """세션 삭제"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    
    # 권한 확인
    if sessions_db[session_id].get("user_email") != user["email"]:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    # 세션과 메시지 삭제
    del sessions_db[session_id]
    if session_id in messages_db:
        del messages_db[session_id]
    
    # 데이터 저장
    save_json_data(SESSIONS_FILE, sessions_db)
    save_json_data(MESSAGES_FILE, messages_db)
    
    print(f"🗑️ 세션 삭제: {user['email']} -> {session_id}")
    
    return JSONResponse({"success": True, "message": "세션이 삭제되었습니다."})

# ==================== 메시지 관리 API ====================

@app.get("/api/sessions/{session_id}/messages")
async def get_messages(session_id: str, request: Request):
    """세션의 메시지 목록 조회"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({"messages": []})
    
    # 세션 존재 및 권한 확인
    if session_id not in sessions_db:
        return JSONResponse({"messages": []})
    
    if sessions_db[session_id].get("user_email") != user["email"]:
        return JSONResponse({"messages": []})
    
    messages = messages_db.get(session_id, [])
    
    # 메시지를 시간 순서대로 정렬 (오래된 메시지부터)
    sorted_messages = sorted(messages, key=lambda x: x.get("timestamp", ""))
    
    print(f"📥 세션 {session_id}의 메시지 로드: {len(sorted_messages)}개")
    
    return JSONResponse({"messages": sorted_messages})

@app.post("/api/messages")
async def messages_api(request: Request):
    """메시지 저장"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    data = await request.json()
    session_id = data.get("session_id")
    role = data.get("role")
    content = data.get("content") or data.get("message")
    
    if not session_id or not role or not content:
        raise HTTPException(status_code=400, detail="필수 필드가 누락되었습니다.")
    
    # 세션이 존재하지 않으면 생성
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
        raise HTTPException(status_code=403, detail="이 세션에 접근할 권한이 없습니다.")
    
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
    
    # 데이터 저장
    save_json_data(MESSAGES_FILE, messages_db)
    save_json_data(SESSIONS_FILE, sessions_db)
    
    print(f"💾 메시지 저장: {session_id} -> {role} ({len(content)}자)")
    
    return JSONResponse({
        "success": True,
        "message": "메시지가 저장되었습니다."
    })

@app.post("/api/chat")
async def chat_api(request: Request):
    """채팅 응답 생성"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    data = await request.json()
    session_id = data.get("session_id")
    message = data.get("message")
    
    if not session_id or not message:
        raise HTTPException(status_code=400, detail="세션 ID와 메시지가 필요합니다.")
    
    # 세션이 존재하는지 확인
    if session_id not in sessions_db:
        # 세션이 없으면 생성
        sessions_db[session_id] = {
            "id": session_id,
            "user_email": user["email"],
            "name": f"대화 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "created_at": datetime.now().isoformat()
        }
        messages_db[session_id] = []
        save_json_data(SESSIONS_FILE, sessions_db)
    
    # 사용자 메시지 저장
    if session_id not in messages_db:
        messages_db[session_id] = []
    
    user_message = {
        "role": "user",
        "content": message,
        "timestamp": datetime.now().isoformat()
    }
    messages_db[session_id].append(user_message)
    save_json_data(MESSAGES_FILE, messages_db)
    
    # OpenAI 클라이언트가 있으면 GPT 응답 생성
    if openai_client:
        try:
            # 기본 AI는 ai1 사용
            ai_key = data.get("ai_key", "ai1")
            
            # 해당 AI의 프롬프트 가져오기
            prompt_data = prompts_data.get(ai_key, prompts_data.get("ai1", {}))
            
            # 시스템 프롬프트 구성
            system_parts = []
            
            # system 프롬프트 추가
            if "system" in prompt_data:
                if isinstance(prompt_data["system"], str):
                    system_parts.append(prompt_data["system"])
                elif isinstance(prompt_data["system"], list):
                    system_parts.extend(prompt_data["system"])
            
            # role 프롬프트 추가
            if "role" in prompt_data:
                if isinstance(prompt_data["role"], str):
                    system_parts.append(prompt_data["role"])
                elif isinstance(prompt_data["role"], list):
                    system_parts.extend(prompt_data["role"])
            
            # guide 프롬프트 추가
            if "guide" in prompt_data:
                if isinstance(prompt_data["guide"], str):
                    system_parts.append(prompt_data["guide"])
                elif isinstance(prompt_data["guide"], list):
                    system_parts.extend(prompt_data["guide"])
            
            # format 프롬프트 추가
            if "format" in prompt_data:
                if isinstance(prompt_data["format"], str):
                    system_parts.append(prompt_data["format"])
                elif isinstance(prompt_data["format"], list):
                    system_parts.extend(prompt_data["format"])
            
            system_prompt = "\n\n".join(filter(None, system_parts))
            
            # 이전 대화 내역 가져오기
            messages = [{"role": "system", "content": system_prompt}]
            
            # 세션의 이전 메시지들 추가 (최근 10개만)
            session_messages = messages_db.get(session_id, [])[-10:]
            for msg in session_messages:
                if msg["role"] in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            print(f"🤖 GPT 호출 - AI: {ai_key}, 프롬프트 길이: {len(system_prompt)}자")
            print(f"📝 대화 컨텍스트: {len(messages)-1}개 메시지")
            
            # GPT 응답 생성
            completion = openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            # AI 응답 생성
            response = completion.choices[0].message.content
            
            print(f"✅ GPT 응답 생성 완료: {len(response)}자")
            
        except Exception as e:
            print(f"❌ GPT 호출 오류: {e}")
            # 오류 발생 시 기본 응답
            response = f"죄송합니다. 응답을 생성하는 중 오류가 발생했습니다: {str(e)}"
    else:
        # OpenAI 클라이언트가 없으면 기본 응답
        responses = [
            "안녕하세요! 무엇을 도와드릴까요?",
            "네, 이해했습니다. 더 자세히 설명해 주시겠어요?",
            "좋은 질문이네요! 함께 고민해 보겠습니다.",
            "흥미로운 주제네요. 더 알려주세요.",
            "도움이 필요하시면 언제든 말씀해 주세요!"
        ]
        
        import random
        response = random.choice(responses)
        print(f"💬 기본 응답 사용 (OpenAI 클라이언트 없음)")
    
    # AI 응답 저장
    ai_message = {
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().isoformat()
    }
    messages_db[session_id].append(ai_message)
    
    # 세션의 메시지 카운트 업데이트
    if session_id in sessions_db:
        sessions_db[session_id]["message_count"] = len(messages_db[session_id])
    
    # 데이터 저장
    save_json_data(MESSAGES_FILE, messages_db)
    save_json_data(SESSIONS_FILE, sessions_db)
    
    print(f"💬 채팅 응답: {session_id} -> {len(response)}자")
    print(f"💾 세션의 총 메시지 수: {len(messages_db[session_id])}개")
    
    return JSONResponse({
        "success": True,
        "response": response,
        "session_id": session_id
    })

# ==================== 프롬프트 관리 API ====================

@app.get("/api/prompts")
async def get_prompts(request: Request):
    """프롬프트 목록 조회"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    # 프롬프트 데이터를 API 응답 형식으로 변환
    prompt_list = []
    for ai_id, prompt_data in prompts_data.items():
        # ai1의 system은 문자열로 처리
        if ai_id == "ai1" and isinstance(prompt_data.get("system"), str):
            system_text = prompt_data.get("system", "")
            # ai1의 나머지는 리스트로 처리
            role_text = "\n".join(prompt_data.get("role", [])) if isinstance(prompt_data.get("role"), list) else prompt_data.get("role", "")
            guide_text = "\n".join(prompt_data.get("guide", [])) if isinstance(prompt_data.get("guide"), list) else prompt_data.get("guide", "")
            format_text = "\n".join(prompt_data.get("format", [])) if isinstance(prompt_data.get("format"), list) else prompt_data.get("format", "")
        else:
            # 다른 AI들은 리스트로 처리
            system_text = "\n".join(prompt_data.get("system", [])) if isinstance(prompt_data.get("system"), list) else prompt_data.get("system", "")
            role_text = "\n".join(prompt_data.get("role", [])) if isinstance(prompt_data.get("role"), list) else prompt_data.get("role", "")
            guide_text = "\n".join(prompt_data.get("guide", [])) if isinstance(prompt_data.get("guide"), list) else prompt_data.get("guide", "")
            format_text = "\n".join(prompt_data.get("format", [])) if isinstance(prompt_data.get("format"), list) else prompt_data.get("format", "")
        
        prompt_list.append({
            "id": ai_id,
            "name": ai_id.upper(),
            "system": system_text,
            "role": role_text,
            "guide": guide_text,
            "format": format_text
        })
    
    print(f"📋 프롬프트 목록 조회: {len(prompt_list)}개")
    
    return JSONResponse({
        "success": True,
        "prompts": prompt_list
    })

@app.get("/api/prompts/{ai_id}")
async def get_prompt(ai_id: str, request: Request):
    """특정 프롬프트 조회"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    if ai_id not in prompts_data:
        raise HTTPException(status_code=404, detail="프롬프트를 찾을 수 없습니다.")
    
    prompt_data = prompts_data[ai_id]
    
    # ai1의 system은 문자열로 처리
    if ai_id == "ai1" and isinstance(prompt_data.get("system"), str):
        system_text = prompt_data.get("system", "")
        # ai1의 나머지는 리스트로 처리
        role_text = "\n".join(prompt_data.get("role", [])) if isinstance(prompt_data.get("role"), list) else prompt_data.get("role", "")
        guide_text = "\n".join(prompt_data.get("guide", [])) if isinstance(prompt_data.get("guide"), list) else prompt_data.get("guide", "")
        format_text = "\n".join(prompt_data.get("format", [])) if isinstance(prompt_data.get("format"), list) else prompt_data.get("format", "")
    else:
        # 다른 AI들은 리스트로 처리
        system_text = "\n".join(prompt_data.get("system", [])) if isinstance(prompt_data.get("system"), list) else prompt_data.get("system", "")
        role_text = "\n".join(prompt_data.get("role", [])) if isinstance(prompt_data.get("role"), list) else prompt_data.get("role", "")
        guide_text = "\n".join(prompt_data.get("guide", [])) if isinstance(prompt_data.get("guide"), list) else prompt_data.get("guide", "")
        format_text = "\n".join(prompt_data.get("format", [])) if isinstance(prompt_data.get("format"), list) else prompt_data.get("format", "")
    
    return JSONResponse({
        "success": True,
        "prompt": {
            "id": ai_id,
            "name": ai_id.upper(),
            "system": system_text,
            "role": role_text,
            "guide": guide_text,
            "format": format_text
        }
    })

@app.put("/api/prompts/{ai_id}")
async def update_prompt(ai_id: str, request: Request):
    """프롬프트 수정"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    try:
        data = await request.json()
        
        # ai1은 문자열로 저장
        if ai_id == "ai1":
            prompts_data[ai_id] = {
                "system": data.get("system", ""),
                "role": data.get("role", ""),
                "guide": data.get("guide", ""),
                "format": data.get("format", "")
            }
        else:
            # 다른 AI들은 리스트로 저장
            prompts_data[ai_id] = {
                "system": [data.get("system", "")],
                "role": [data.get("role", "")],
                "guide": [data.get("guide", "")],
                "format": [data.get("format", "")]
            }
        
        # 파일에 저장
        for path in prompts_file_paths:
            if os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(prompts_data, f, ensure_ascii=False, indent=2)
                print(f"✅ 프롬프트 업데이트: {ai_id} -> {path}")
                break
        
        return JSONResponse({
            "success": True,
            "message": "프롬프트가 성공적으로 업데이트되었습니다."
        })
        
    except Exception as e:
        print(f"❌ 프롬프트 업데이트 오류: {e}")
        return JSONResponse(
            {"success": False, "message": str(e)},
            status_code=500
        )

# ==================== 기타 API ====================

@app.get("/api/user/points")
async def get_user_points(request: Request):
    """사용자 포인트 조회"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({"points": 0})
    
    return JSONResponse({
        "points": 1000,
        "level": 3,
        "badges": ["초보자", "활발한 사용자"]
    })

@app.get("/api/user/stats")
async def get_user_stats(request: Request):
    """사용자 통계"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    # 사용자의 세션 수 계산
    user_sessions = [s for s in sessions_db.values() if s.get("user_email") == user["email"]]
    total_messages = sum(len(messages_db.get(s["id"], [])) for s in user_sessions)
    
    return JSONResponse({
        "total_sessions": len(user_sessions),
        "total_messages": total_messages,
        "active_days": 15,
        "points": 1000
    })

@app.get("/api/user/activity")
async def user_activity(request: Request):
    """사용자 활동 내역"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    return JSONResponse({
        "activities": [
            {"date": "2024-01-29", "type": "chat", "count": 5},
            {"date": "2024-01-28", "type": "chat", "count": 8}
        ]
    })

@app.get("/api/admin/stats")
async def admin_stats(request: Request):
    """관리자 통계 API"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    return JSONResponse({
        "total_users": len(users_db),
        "total_sessions": len(sessions_db),
        "total_messages": sum(len(msgs) for msgs in messages_db.values()),
        "active_users": 2
    })

@app.post("/api/set-language")
async def set_language(request: Request):
    """언어 설정"""
    data = await request.json()
    language = data.get("language", "ko")
    return JSONResponse({"success": True, "language": language})

# WebSocket 연결 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            # 에코 응답
            await manager.send_message(f"Echo: {data}", client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)

# 기타 페이지들
pages = ["memory", "profile", "test", "aura_system", "learning", "points", "prompts"]
for page in pages:
    @app.get(f"/{page}", response_class=HTMLResponse, name=f"{page}_page")
    async def generic_page(request: Request, page=page):
        user = get_current_user(request)
        if not user:
            return RedirectResponse(url="/login", status_code=303)
        return templates.TemplateResponse(f"{page}.html", {
            "request": request,
            "user": user
        })

# 메인 실행
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 EORA AI 안정 서버")
    print("="*60)
    print(f"📍 홈페이지: http://127.0.0.1:8100")
    print(f"🔐 로그인: http://127.0.0.1:8100/login")
    print(f"📝 회원가입: http://127.0.0.1:8100/register")
    print(f"⚙️ 관리자: http://127.0.0.1:8100/admin")
    print(f"💬 채팅: http://127.0.0.1:8100/chat")
    print(f"📋 프롬프트 관리: http://127.0.0.1:8100/prompt_management")
    print("="*60)
    print("📧 관리자: admin@eora.ai / 비밀번호: admin123")
    print("📧 테스트: test@eora.ai / 비밀번호: test123")
    print("="*60)
    print(f"💾 데이터 디렉토리: {DATA_DIR}")
    print(f"📄 프롬프트: {len(prompts_data)}개 AI 로드됨")
    print("="*60)
    
    uvicorn.run(app, host="127.0.0.1", port=8100, log_level="info") 