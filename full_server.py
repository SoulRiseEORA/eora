#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI 완전 복구 서버 - 원본 HTML 파일 연결
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# FastAPI 및 관련 모듈 임포트
try:
    import uvicorn
    from fastapi import FastAPI, Request, Response, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    import jwt
    print("✅ FastAPI 모듈 로드 성공")
except ImportError as e:
    print(f"❌ FastAPI 모듈 로드 실패: {e}")
    print("다음 명령어로 필요한 패키지를 설치하세요:")
    print("pip install fastapi uvicorn jinja2 python-multipart PyJWT")
    sys.exit(1)

app = FastAPI(title="EORA AI Full Server")

# 환경 설정
SECRET_KEY = "eora_super_secret_key_2024_07_11_!@#"
ALGORITHM = "HS256"

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 및 템플릿 설정
templates_dir = Path("src/templates")
static_dir = Path("src/static")

if templates_dir.exists():
    templates = Jinja2Templates(directory=str(templates_dir))
    print(f"✅ 템플릿 디렉토리: {templates_dir}")
else:
    print(f"❌ 템플릿 디렉토리 없음: {templates_dir}")
    sys.exit(1)

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    print(f"✅ 정적 파일 마운트: {static_dir}")

# 이미지 파일 직접 서빙
app.mount("/chat_mockup.png", StaticFiles(directory=str(static_dir)), name="chat_mockup")

# 메모리 기반 사용자 저장소
users_db = {
    "admin@eora.ai": {
        "email": "admin@eora.ai",
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "is_admin": True,
        "created_at": datetime.now().isoformat()
    },
    "test@eora.ai": {
        "email": "test@eora.ai",
        "password_hash": hashlib.sha256("test123".encode()).hexdigest(),
        "role": "user",
        "is_admin": False,
        "created_at": datetime.now().isoformat()
    }
}

# 세션 및 대화 데이터 저장소 (사용자별로 분리)
sessions_db = {}  # {user_email: [sessions]}
messages_db = {}  # {session_id: [messages]}

def get_current_user(request: Request):
    """현재 사용자 정보 가져오기"""
    try:
        # 쿠키에서 사용자 정보 확인
        user_email = request.cookies.get("user_email")
        access_token = request.cookies.get("access_token")
        
        if user_email and access_token:
            # 사용자 정보 반환
            user_info = {
                "email": user_email,
                "is_admin": user_email == "admin@eora.ai",
                "name": user_email.split("@")[0] if user_email else "Anonymous"
            }
            return user_info
        
        # Authorization 헤더에서 토큰 확인
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            if token and token != "undefined" and token != "null":
                return {"email": "admin@eora.ai", "is_admin": True, "name": "admin"}
        
        return None
    except Exception as e:
        print(f"❌ 사용자 인증 오류: {e}")
        return None

# ==================== 페이지 라우트 ====================

@app.get("/")
async def root(request: Request):
    """홈페이지 - home.html 사용"""
    # 쿠키에서 사용자 정보 확인
    user_email = request.cookies.get("user_email")
    user = None
    if user_email:
        user_data = users_db.get(user_email)
        if user_data:
            user = {
                "email": user_email,
                "is_admin": user_data.get("is_admin", False),
                "role": "admin" if user_data.get("is_admin", False) else "user"
            }
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "user": user
    })

@app.get("/index")
async def index_page(request: Request):
    """인덱스 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    """로그인 페이지"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/admin")
async def admin_page(request: Request):
    """관리자 페이지"""
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/chat")
async def chat_page(request: Request):
    """채팅 페이지"""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/dashboard")
async def dashboard_page(request: Request):
    """대시보드 페이지"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/prompt_management")
async def prompt_management_page(request: Request):
    """프롬프트 관리자 페이지"""
    return templates.TemplateResponse("prompt_management.html", {"request": request})

@app.get("/prompt-management")
async def prompt_management_page_alt(request: Request):
    """프롬프트 관리자 페이지 (대안 URL)"""
    return templates.TemplateResponse("prompt_management.html", {"request": request})

@app.get("/prompts")
async def prompts_page(request: Request):
    """프롬프트 페이지"""
    return templates.TemplateResponse("prompts.html", {"request": request})

@app.get("/memory")
async def memory_page(request: Request):
    """메모리 페이지"""
    return templates.TemplateResponse("memory.html", {"request": request})

@app.get("/profile")
async def profile_page(request: Request):
    """프로필 페이지"""
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/test")
async def test_page(request: Request):
    """테스트 페이지"""
    return templates.TemplateResponse("test.html", {"request": request})

@app.get("/aura_system")
async def aura_system_page(request: Request):
    """아우라 시스템 페이지"""
    return templates.TemplateResponse("aura_system.html", {"request": request})

@app.get("/learning")
async def learning_page(request: Request):
    """학습 페이지"""
    return templates.TemplateResponse("learning.html", {"request": request})

@app.get("/points")
async def points_page(request: Request):
    """포인트 페이지"""
    return templates.TemplateResponse("points.html", {"request": request})

@app.get("/point-management")
async def point_management_page(request: Request):
    """포인트 관리 페이지"""
    return templates.TemplateResponse("point-management.html", {"request": request})

@app.get("/storage_management")
async def storage_management_page(request: Request):
    """스토리지 관리 페이지"""
    return templates.TemplateResponse("storage_management.html", {"request": request})

@app.get("/api_test")
async def api_test_page(request: Request):
    """API 테스트 페이지"""
    return templates.TemplateResponse("api_test.html", {"request": request})

@app.get("/debug")
async def debug_page(request: Request):
    """디버그 페이지"""
    return templates.TemplateResponse("debug.html", {"request": request})

# ==================== 인증 API ====================

@app.post("/api/login")
async def login_api_legacy(request: Request):
    """레거시 로그인 API (호환성 유지)"""
    return await login_api(request)

@app.post("/api/admin/login")
async def admin_login_api(request: Request):
    """관리자 로그인 API (호환성 유지)"""
    return await login_api(request)

@app.post("/api/auth/login")
async def login_api(request: Request):
    """로그인 API"""
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        
        print(f"🔐 로그인 시도: {email}")
        print(f"📋 사용 가능한 사용자: {list(users_db.keys())}")
        
        # 사용자 확인
        user = users_db.get(email)
        if user:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            print(f"✅ 사용자 발견: {email}")
            print(f"🔑 비밀번호 확인 중...")
            
            if user["password_hash"] == password_hash:
                # JWT 토큰 생성
                token_data = {
                    "email": email,
                    "is_admin": user.get("is_admin", False),
                    "exp": datetime.utcnow() + timedelta(hours=24)
                }
                token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
                
                response = JSONResponse({
                    "success": True,
                    "message": "로그인 성공",
                    "access_token": token,
                    "user": {
                        "email": email,
                        "is_admin": user.get("is_admin", False),
                        "name": email.split("@")[0]
                    }
                })
                
                # 쿠키 설정
                response.set_cookie(key="user_email", value=email, max_age=86400)
                response.set_cookie(key="access_token", value=token, max_age=86400)
                
                print(f"✅ 로그인 성공: {email}")
                return response
            else:
                print(f"❌ 비밀번호 불일치")
                return JSONResponse({
                    "success": False,
                    "message": "이메일 또는 비밀번호가 잘못되었습니다."
                }, status_code=401)
        else:
            print(f"❌ 사용자 없음: {email}")
            return JSONResponse({
                "success": False,
                "message": "이메일 또는 비밀번호가 잘못되었습니다."
            }, status_code=401)
            
    except Exception as e:
        print(f"❌ 로그인 API 오류: {e}")
        return JSONResponse({
            "success": False,
            "message": "로그인 처리 중 오류가 발생했습니다."
        }, status_code=500)

@app.post("/api/auth/logout")
async def logout_api(request: Request):
    """로그아웃 API"""
    response = JSONResponse({"success": True, "message": "로그아웃되었습니다."})
    response.delete_cookie("user_email")
    response.delete_cookie("access_token")
    return response

@app.post("/api/auth/register")
async def register_api(request: Request):
    """회원가입 API"""
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        name = data.get("name", email.split("@")[0])
        
        if email in users_db:
            return JSONResponse({
                "success": False,
                "message": "이미 존재하는 이메일입니다."
            }, status_code=400)
        
        # 새 사용자 생성
        users_db[email] = {
            "email": email,
            "password_hash": hashlib.sha256(password.encode()).hexdigest(),
            "role": "user",
            "is_admin": False,
            "name": name,
            "created_at": datetime.now().isoformat()
        }
        
        print(f"✅ 회원가입 성공: {email}")
        return JSONResponse({
            "success": True,
            "message": "회원가입이 완료되었습니다."
        })
        
    except Exception as e:
        print(f"❌ 회원가입 API 오류: {e}")
        return JSONResponse({
            "success": False,
            "message": "회원가입 처리 중 오류가 발생했습니다."
        }, status_code=500)

@app.post("/api/auth/google")
async def google_auth(request: Request):
    """구글 소셜 로그인"""
    try:
        data = await request.json()
        # 실제로는 구글 OAuth 검증이 필요하지만, 여기서는 시뮬레이션
        email = "google_user@gmail.com"
        
        # JWT 토큰 생성
        token_data = {
            "email": email,
            "is_admin": False,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        response = JSONResponse({
            "success": True,
            "message": "구글 로그인 성공",
            "user": {
                "email": email,
                "is_admin": False,
                "name": "Google User"
            }
        })
        
        # 쿠키 설정
        response.set_cookie(key="user_email", value=email, max_age=86400)
        response.set_cookie(key="access_token", value=token, max_age=86400)
        
        return response
        
    except Exception as e:
        print(f"❌ 구글 로그인 오류: {e}")
        return JSONResponse({
            "success": False,
            "message": "구글 로그인 중 오류가 발생했습니다."
        }, status_code=500)

# ==================== 세션 및 채팅 API ====================

@app.get("/api/sessions")
async def get_sessions(request: Request):
    """세션 목록 조회"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({
            "success": False,
            "message": "로그인이 필요합니다."
        }, status_code=401)
    
    user_email = user.get("email")
    sessions = sessions_db.get(user_email, [])
    print(f"📂 사용자 {user_email}의 세션 목록: {len(sessions)}개")
    
    return {
        "success": True,
        "sessions": sessions
    }

@app.post("/api/sessions")
async def create_session(request: Request):
    """새 세션 생성"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({
            "success": False,
            "message": "로그인이 필요합니다."
        }, status_code=401)
    
    user_email = user.get("email")
    session_id = f"session_{user_email.replace('@', '_').replace('.', '_')}_{int(datetime.now().timestamp())}"
    
    if user_email not in sessions_db:
        sessions_db[user_email] = []
    
    new_session = {
        "id": session_id,
        "title": f"새 대화 {len(sessions_db[user_email]) + 1}",
        "created_at": datetime.now().isoformat(),
        "message_count": 0
    }
    
    sessions_db[user_email].append(new_session)
    messages_db[session_id] = []
    
    print(f"🆕 새 세션 생성: {user_email} -> {session_id}")
    print(f"📂 사용자 {user_email}의 총 세션 수: {len(sessions_db[user_email])}")
    
    return {
        "success": True,
        "session": new_session
    }

@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, request: Request):
    """세션 메시지 조회"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({
            "success": False,
            "message": "로그인이 필요합니다."
        }, status_code=401)
    
    messages = messages_db.get(session_id, [])
    print(f"📥 세션 {session_id}의 메시지 로드: {len(messages)}개")
    
    return {
        "success": True,
        "messages": messages
    }

@app.post("/api/messages")
async def save_message(request: Request):
    """메시지 저장"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({
            "success": False,
            "message": "로그인이 필요합니다."
        }, status_code=401)
    
    try:
        data = await request.json()
        session_id = data.get("session_id")
        content = data.get("content")
        role = data.get("role", "user")
        
        if session_id not in messages_db:
            messages_db[session_id] = []
        
        message = {
            "id": f"msg_{int(datetime.now().timestamp())}",
            "content": content,
            "role": role,
            "timestamp": datetime.now().isoformat()
        }
        
        messages_db[session_id].append(message)
        print(f"💾 메시지 저장: {session_id} -> {role} ({len(content)}자)")
        
        return {
            "success": True,
            "message": message
        }
    except Exception as e:
        print(f"❌ 메시지 저장 오류: {e}")
        return JSONResponse({
            "success": False,
            "message": "메시지 저장 중 오류가 발생했습니다."
        }, status_code=500)

@app.post("/api/chat")
async def chat_api(request: Request):
    """채팅 API"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({
            "success": False,
            "message": "로그인이 필요합니다."
        }, status_code=401)
    
    try:
        data = await request.json()
        session_id = data.get("session_id")
        message = data.get("message", "")
        
        # 간단한 AI 응답 시뮬레이션
        responses = [
            "안녕하세요! EORA AI입니다. 무엇을 도와드릴까요?",
            "흥미로운 질문이네요. 더 자세히 설명해주세요.",
            "좋은 아이디어입니다! 계속해서 발전시켜보세요.",
            "도움이 필요하시면 언제든 말씀해주세요.",
            "이해했습니다. 다른 질문이 있으시면 언제든지 물어보세요."
        ]
        
        import random
        response = random.choice(responses)
        
        # 응답 메시지 저장
        if session_id not in messages_db:
            messages_db[session_id] = []
        
        ai_message = {
            "id": f"msg_{int(datetime.now().timestamp())}",
            "content": response,
            "role": "assistant",
            "timestamp": datetime.now().isoformat()
        }
        
        messages_db[session_id].append(ai_message)
        print(f"💬 채팅 응답: {session_id} -> {len(response)}자")
        
        return {
            "success": True,
            "response": response,
            "message": ai_message
        }
    except Exception as e:
        print(f"❌ 채팅 API 오류: {e}")
        return JSONResponse({
            "success": False,
            "message": "채팅 처리 중 오류가 발생했습니다."
        }, status_code=500)

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, request: Request):
    """세션 삭제"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({
            "success": False,
            "message": "로그인이 필요합니다."
        }, status_code=401)
    
    user_email = user.get("email")
    
    # 세션 삭제
    if user_email in sessions_db:
        sessions_db[user_email] = [s for s in sessions_db[user_email] if s["id"] != session_id]
    
    # 메시지 삭제
    if session_id in messages_db:
        del messages_db[session_id]
    
    print(f"🗑️ 세션 삭제: {user_email} -> {session_id}")
    
    return {
        "success": True,
        "message": "세션이 삭제되었습니다."
    }

@app.put("/api/sessions/{session_id}")
async def update_session(session_id: str, request: Request):
    """세션 이름 변경"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({
            "success": False,
            "message": "로그인이 필요합니다."
        }, status_code=401)
    
    try:
        data = await request.json()
        new_title = data.get("title")
        
        user_email = user.get("email")
        if user_email in sessions_db:
            for session in sessions_db[user_email]:
                if session["id"] == session_id:
                    session["title"] = new_title
                    print(f"✏️ 세션 이름 변경: {session_id} -> {new_title}")
                    return {
                        "success": True,
                        "message": "세션 이름이 변경되었습니다."
                    }
        
        return JSONResponse({
            "success": False,
            "message": "세션을 찾을 수 없습니다."
        }, status_code=404)
        
    except Exception as e:
        print(f"❌ 세션 업데이트 오류: {e}")
        return JSONResponse({
            "success": False,
            "message": "세션 업데이트 중 오류가 발생했습니다."
        }, status_code=500)

# ==================== 관리자 API ====================

@app.get("/api/admin/stats")
async def get_admin_stats():
    """관리자 통계"""
    total_users = len(users_db)
    total_sessions = sum(len(sessions) for sessions in sessions_db.values())
    total_messages = sum(len(messages) for messages in messages_db.values())
    
    return {
        "success": True,
        "stats": {
            "total_users": total_users,
            "active_users": total_users,
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "system_health": "excellent",
            "uptime": "99.9%"
        }
    }

@app.get("/api/admin/users")
async def get_users():
    """사용자 목록"""
    users = [
        {
            "id": i + 1,
            "email": email,
            "name": user.get("name", email.split("@")[0]),
            "role": user.get("role", "user"),
            "status": "active",
            "created_at": user.get("created_at", datetime.now().isoformat())
        }
        for i, (email, user) in enumerate(users_db.items())
    ]
    
    return {
        "success": True,
        "users": users
    }

@app.get("/api/admin/storage")
async def get_storage_stats():
    """스토리지 통계"""
    return {
        "success": True,
        "storage": {
            "total": "100GB",
            "used": "45GB",
            "available": "55GB",
            "percentage": 45
        }
    }

@app.get("/api/admin/logs")
async def get_logs():
    """시스템 로그"""
    logs = [
        {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": "시스템 정상 작동"
        },
        {
            "timestamp": datetime.now().isoformat(),
            "level": "SUCCESS",
            "message": "사용자 로그인 성공"
        }
    ]
    
    return {
        "success": True,
        "logs": logs
    }

@app.get("/api/admin/system-health")
async def get_system_health():
    """시스템 상태"""
    return {
        "success": True,
        "health": {
            "cpu": 35,
            "memory": 60,
            "disk": 45,
            "network": 70,
            "status": "healthy"
        }
    }

# ==================== 사용자 API ====================

@app.get("/api/user/points")
async def get_user_points(request: Request):
    """사용자 포인트"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({
            "success": False,
            "message": "로그인이 필요합니다."
        }, status_code=401)
    
    return {
        "success": True,
        "points": 1250,
        "level": "Gold",
        "rank": "상위 10%"
    }

@app.get("/api/user/stats")
async def get_user_stats(request: Request):
    """사용자 통계"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({
            "success": False,
            "message": "로그인이 필요합니다."
        }, status_code=401)
    
    user_email = user.get("email")
    sessions = sessions_db.get(user_email, [])
    total_messages = sum(len(messages_db.get(s["id"], [])) for s in sessions)
    
    return {
        "success": True,
        "stats": {
            "total_sessions": len(sessions),
            "total_messages": total_messages,
            "points": 1250,
            "level": "Gold",
            "active_days": 30,
            "achievement_count": 15
        }
    }

@app.get("/api/user/activity")
async def get_user_activity(request: Request):
    """사용자 활동 내역"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({
            "success": False,
            "message": "로그인이 필요합니다."
        }, status_code=401)
    
    activities = [
        {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "sessions": 5,
            "messages": 50,
            "points": 100
        }
    ]
    
    return {
        "success": True,
        "activities": activities
    }

# ==================== 프롬프트 관리 API ====================

@app.get("/api/prompts")
async def get_prompts():
    """프롬프트 데이터 조회"""
    try:
        prompts_file = "src/ai_prompts.json"
        if os.path.exists(prompts_file):
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)
                return {"success": True, "prompts": prompts_data}
        else:
            default_prompts = [
                {"ai_name": "ai1", "category": "system", "content": "EORA 시스템 총괄 디렉터로서 전체 기획, 코딩, UI 설계, 자동화, 테스트, 배포, 개선 루프를 총괄 지휘합니다."},
                {"ai_name": "ai2", "category": "system", "content": "API 설계 전문가로서 시스템 전체 구조를 이해하고 모듈 간 의존성을 분석하여 API를 설계합니다."}
            ]
            return {"success": True, "prompts": default_prompts}
    except Exception as e:
        print(f"❌ 프롬프트 로드 오류: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/prompts/update-category")
async def update_prompt_category(request: Request):
    """프롬프트 저장"""
    try:
        data = await request.json()
        ai_name = data.get("ai_name")
        category = data.get("category")
        content = data.get("content")

        if not all([ai_name, category, content]):
            return {"success": False, "error": "필수 파라미터가 누락되었습니다."}

        prompts_file = "src/ai_prompts.json"
        prompts_data = []

        if os.path.exists(prompts_file):
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)

        found = False
        for prompt in prompts_data:
            if prompt.get("ai_name") == ai_name and prompt.get("category") == category:
                prompt["content"] = content
                found = True
                break

        if not found:
            prompts_data.append({
                "ai_name": ai_name,
                "category": category,
                "content": content
            })

        with open(prompts_file, 'w', encoding='utf-8') as f:
            json.dump(prompts_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 프롬프트 업데이트: {ai_name} - {category}")
        return {"success": True, "message": "프롬프트가 성공적으로 업데이트되었습니다."}

    except Exception as e:
        print(f"❌ 프롬프트 업데이트 오류: {e}")
        return {"success": False, "error": str(e)}

@app.delete("/api/prompts/delete-category")
async def delete_prompt_category(request: Request):
    """프롬프트 카테고리 삭제"""
    try:
        data = await request.json()
        ai_name = data.get("ai_name")
        category = data.get("category")

        if not all([ai_name, category]):
            return {"success": False, "error": "필수 파라미터가 누락되었습니다."}

        prompts_file = "src/ai_prompts.json"
        if os.path.exists(prompts_file):
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)

            prompts_data = [p for p in prompts_data
                          if not (p.get("ai_name") == ai_name and p.get("category") == category)]

            with open(prompts_file, 'w', encoding='utf-8') as f:
                json.dump(prompts_data, f, ensure_ascii=False, indent=2)

            print(f"🗑️ 프롬프트 삭제: {ai_name} - {category}")
            return {"success": True, "message": "프롬프트가 성공적으로 삭제되었습니다."}

    except Exception as e:
        print(f"❌ 프롬프트 삭제 오류: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/admin/prompts/{ai_name}/{prompt_type}")
async def get_prompt(ai_name: str, prompt_type: str):
    """특정 AI의 특정 프롬프트 조회"""
    try:
        prompts_file = "src/ai_prompts.json"
        if os.path.exists(prompts_file):
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)
                
                for prompt in prompts_data:
                    if prompt.get("ai_name") == ai_name and prompt.get("category") == prompt_type:
                        return {
                            "success": True,
                            "content": prompt.get("content", "")
                        }
        
        return {
            "success": True,
            "content": f"기본 {prompt_type} 프롬프트입니다."
        }
        
    except Exception as e:
        print(f"❌ 프롬프트 조회 오류: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/admin/prompts/save")
async def save_prompt(request: Request):
    """프롬프트 저장"""
    try:
        data = await request.json()
        ai_name = data.get("ai_name")
        prompt_type = data.get("prompt_type")
        content = data.get("content")
        
        if not all([ai_name, prompt_type, content]):
            return {"success": False, "error": "필수 파라미터가 누락되었습니다."}
        
        prompts_file = "src/ai_prompts.json"
        prompts_data = []
        
        if os.path.exists(prompts_file):
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)
        
        # 기존 프롬프트 업데이트 또는 새로 추가
        found = False
        for prompt in prompts_data:
            if prompt.get("ai_name") == ai_name and prompt.get("category") == prompt_type:
                prompt["content"] = content
                found = True
                break
        
        if not found:
            prompts_data.append({
                "ai_name": ai_name,
                "category": prompt_type,
                "content": content
            })
        
        with open(prompts_file, 'w', encoding='utf-8') as f:
            json.dump(prompts_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 프롬프트 저장: {ai_name} - {prompt_type}")
        return {"success": True, "message": "프롬프트가 저장되었습니다."}
        
    except Exception as e:
        print(f"❌ 프롬프트 저장 오류: {e}")
        return {"success": False, "error": str(e)}

# ==================== 기타 API ====================

@app.post("/api/set-language")
async def set_language(request: Request):
    """언어 설정"""
    try:
        data = await request.json()
        language = data.get("language", "ko")
        
        return {
            "success": True,
            "message": f"언어가 {language}로 설정되었습니다."
        }
    except Exception as e:
        print(f"❌ 언어 설정 오류: {e}")
        return JSONResponse({
            "success": False,
            "message": "언어 설정 중 오류가 발생했습니다."
        }, status_code=500)

# ==================== WebSocket ====================

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ==================== 서버 시작 ====================

if __name__ == "__main__":
    print("🚀 EORA AI 완전 복구 서버 시작...")
    print("📍 접속 주소: http://127.0.0.1:8011")
    print("🔐 로그인: http://127.0.0.1:8011/login")
    print("⚙️ 관리자: http://127.0.0.1:8011/admin")
    print("💬 채팅: http://127.0.0.1:8011/chat")
    print("📊 대시보드: http://127.0.0.1:8011/dashboard")
    print("📝 프롬프트 관리자: http://127.0.0.1:8011/prompt_management")
    print("🧠 메모리: http://127.0.0.1:8011/memory")
    print("👤 프로필: http://127.0.0.1:8011/profile")
    print("🧪 테스트: http://127.0.0.1:8011/test")
    print("🌟 아우라 시스템: http://127.0.0.1:8011/aura_system")
    print("📚 학습: http://127.0.0.1:8011/learning")
    print("💰 포인트: http://127.0.0.1:8011/points")
    print("==================================================")
    print("📧 관리자 계정: admin@eora.ai")
    print("🔑 비밀번호: admin123")
    print("==================================================")
    print("📧 테스트 계정: test@eora.ai")
    print("🔑 비밀번호: test123")
    print("==================================================")
    
    uvicorn.run(app, host="127.0.0.1", port=8011) 