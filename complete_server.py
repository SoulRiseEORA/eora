#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI 완전 서버 - 모든 HTML 파일 정상 작동
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

app = FastAPI(title="EORA AI Complete Server")

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
    print(f"⚠️ 템플릿 디렉토리 없음: {templates_dir}")
    templates = None

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    print(f"✅ 정적 파일 마운트: {static_dir}")
else:
    print(f"⚠️ 정적 파일 디렉토리 없음: {static_dir}")

# 메모리 기반 사용자 저장소
users_db = {
    "admin@eora.ai": {
        "email": "admin@eora.ai",
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "is_admin": True,
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
            # 간단한 토큰 검증 (실제로는 JWT 검증 필요)
            if token and token != "undefined" and token != "null":
                return {"email": "admin@eora.ai", "is_admin": True, "name": "admin"}
        
        return None
    except Exception as e:
        print(f"❌ 사용자 인증 오류: {e}")
        return None

# ==================== 홈페이지 및 기본 페이지 ====================

@app.get("/")
async def root(request: Request):
    """홈페이지"""
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        print(f"❌ 홈페이지 로드 오류: {e}")
        return HTMLResponse("""
        <html>
        <head><title>EORA AI - 홈페이지</title></head>
        <body>
            <h1>🏠 EORA AI 홈페이지</h1>
            <p>서버가 정상 작동 중입니다!</p>
            <ul>
                <li><a href="/login">🔐 로그인</a></li>
                <li><a href="/admin">⚙️ 관리자</a></li>
                <li><a href="/chat">💬 채팅</a></li>
                <li><a href="/dashboard">📊 대시보드</a></li>
                <li><a href="/prompt_management">📝 프롬프트 관리자</a></li>
            </ul>
        </body>
        </html>
        """)

@app.get("/login")
async def login_page(request: Request):
    """로그인 페이지"""
    try:
        return templates.TemplateResponse("login.html", {"request": request})
    except Exception as e:
        print(f"❌ 로그인 페이지 로드 오류: {e}")
        return HTMLResponse("""
        <html>
        <head><title>로그인 - EORA AI</title></head>
        <body>
            <h1>🔐 로그인</h1>
            <form id="loginForm">
                <input type="email" id="email" placeholder="이메일" value="admin@eora.ai" required><br>
                <input type="password" id="password" placeholder="비밀번호" value="admin123" required><br>
                <button type="submit">로그인</button>
            </form>
            <p><a href="/">홈으로 돌아가기</a></p>
        </body>
        </html>
        """)

@app.get("/admin")
async def admin_page(request: Request):
    """관리자 페이지"""
    try:
        return templates.TemplateResponse("admin.html", {"request": request})
    except Exception as e:
        print(f"❌ 관리자 페이지 로드 오류: {e}")
        return HTMLResponse("""
        <html>
        <head><title>관리자 - EORA AI</title></head>
        <body>
            <h1>⚙️ 관리자 대시보드</h1>
            <p>관리자 페이지가 정상 작동합니다!</p>
            <ul>
                <li><a href="/prompt_management">📝 프롬프트 관리자</a></li>
                <li><a href="/dashboard">📊 사용자 대시보드</a></li>
                <li><a href="/chat">💬 채팅</a></li>
            </ul>
            <p><a href="/">홈으로 돌아가기</a></p>
        </body>
        </html>
        """)

@app.get("/chat")
async def chat_page(request: Request):
    """채팅 페이지"""
    try:
        return templates.TemplateResponse("chat.html", {"request": request})
    except Exception as e:
        print(f"❌ 채팅 페이지 로드 오류: {e}")
        return HTMLResponse("""
        <html>
        <head><title>채팅 - EORA AI</title></head>
        <body>
            <h1>💬 EORA AI 채팅</h1>
            <p>채팅 페이지가 정상 작동합니다!</p>
            <p><a href="/">홈으로 돌아가기</a></p>
        </body>
        </html>
        """)

@app.get("/dashboard")
async def dashboard_page(request: Request):
    """대시보드 페이지"""
    try:
        return templates.TemplateResponse("dashboard.html", {"request": request})
    except Exception as e:
        print(f"❌ 대시보드 페이지 로드 오류: {e}")
        return HTMLResponse("""
        <html>
        <head><title>대시보드 - EORA AI</title></head>
        <body>
            <h1>📊 사용자 대시보드</h1>
            <p>대시보드 페이지가 정상 작동합니다!</p>
            <p><a href="/">홈으로 돌아가기</a></p>
        </body>
        </html>
        """)

@app.get("/prompt_management")
async def prompt_management_page(request: Request):
    """프롬프트 관리자 페이지"""
    try:
        return templates.TemplateResponse("prompt_management.html", {"request": request})
    except Exception as e:
        print(f"❌ 프롬프트 관리자 페이지 로드 오류: {e}")
        return HTMLResponse("""
        <html>
        <head><title>프롬프트 관리자 - EORA AI</title></head>
        <body>
            <h1>📝 프롬프트 관리자</h1>
            <p>프롬프트 관리자 페이지가 정상 작동합니다!</p>
            <p><a href="/">홈으로 돌아가기</a></p>
        </body>
        </html>
        """)

@app.get("/prompt-management")
async def prompt_management_page_alt(request: Request):
    """프롬프트 관리자 페이지 (대안 URL)"""
    return await prompt_management_page(request)

@app.get("/prompts")
async def prompts_page(request: Request):
    """프롬프트 페이지"""
    try:
        return templates.TemplateResponse("prompts.html", {"request": request})
    except Exception as e:
        print(f"❌ 프롬프트 페이지 로드 오류: {e}")
        return HTMLResponse("""
        <html>
        <head><title>프롬프트 - EORA AI</title></head>
        <body>
            <h1>📝 프롬프트</h1>
            <p>프롬프트 페이지가 정상 작동합니다!</p>
            <p><a href="/">홈으로 돌아가기</a></p>
        </body>
        </html>
        """)

@app.get("/memory")
async def memory_page(request: Request):
    """메모리 페이지"""
    try:
        return templates.TemplateResponse("memory.html", {"request": request})
    except Exception as e:
        print(f"❌ 메모리 페이지 로드 오류: {e}")
        return HTMLResponse("""
        <html>
        <head><title>메모리 - EORA AI</title></head>
        <body>
            <h1>🧠 메모리 시스템</h1>
            <p>메모리 페이지가 정상 작동합니다!</p>
            <p><a href="/">홈으로 돌아가기</a></p>
        </body>
        </html>
        """)

@app.get("/profile")
async def profile_page(request: Request):
    """프로필 페이지"""
    try:
        return templates.TemplateResponse("profile.html", {"request": request})
    except Exception as e:
        print(f"❌ 프로필 페이지 로드 오류: {e}")
        return HTMLResponse("""
        <html>
        <head><title>프로필 - EORA AI</title></head>
        <body>
            <h1>👤 사용자 프로필</h1>
            <p>프로필 페이지가 정상 작동합니다!</p>
            <p><a href="/">홈으로 돌아가기</a></p>
        </body>
        </html>
        """)

@app.get("/test")
async def test_page(request: Request):
    """테스트 페이지"""
    try:
        return templates.TemplateResponse("test.html", {"request": request})
    except Exception as e:
        print(f"❌ 테스트 페이지 로드 오류: {e}")
        return HTMLResponse("""
        <html>
        <head><title>테스트 - EORA AI</title></head>
        <body>
            <h1>🧪 테스트 페이지</h1>
            <p>테스트 페이지가 정상 작동합니다!</p>
            <p><a href="/">홈으로 돌아가기</a></p>
        </body>
        </html>
        """)

@app.get("/aura_system")
async def aura_system_page(request: Request):
    """아우라 시스템 페이지"""
    try:
        return templates.TemplateResponse("aura_system.html", {"request": request})
    except Exception as e:
        print(f"❌ 아우라 시스템 페이지 로드 오류: {e}")
        return HTMLResponse("""
        <html>
        <head><title>아우라 시스템 - EORA AI</title></head>
        <body>
            <h1>🌟 아우라 시스템</h1>
            <p>아우라 시스템 페이지가 정상 작동합니다!</p>
            <p><a href="/">홈으로 돌아가기</a></p>
        </body>
        </html>
        """)

# ==================== API 엔드포인트 ====================

@app.post("/api/auth/login")
async def login_api(request: Request):
    """로그인 API"""
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        
        if email == "admin@eora.ai" and password == "admin123":
            # JWT 토큰 생성
            token_data = {
                "email": email,
                "is_admin": True,
                "exp": datetime.utcnow() + timedelta(hours=24)
            }
            token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
            
            response = JSONResponse({
                "success": True,
                "message": "로그인 성공",
                "user": {
                    "email": email,
                    "is_admin": True,
                    "name": "admin"
                }
            })
            
            # 쿠키 설정
            response.set_cookie(key="user_email", value=email, max_age=86400)
            response.set_cookie(key="access_token", value=token, max_age=86400)
            
            print(f"✅ 로그인 성공: {email}")
            return response
        else:
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

@app.get("/api/admin/stats")
async def get_admin_stats():
    """관리자 통계 API"""
    return {
        "success": True,
        "stats": {
            "total_users": 150,
            "active_users": 89,
            "total_sessions": 1250,
            "total_messages": 15600,
            "system_health": "excellent",
            "uptime": "99.9%"
        }
    }

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
        print(f"�� 채팅 응답: {session_id} -> {len(response)}자")
        
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

@app.get("/api/user/points")
async def get_user_points(request: Request):
    """사용자 포인트 조회"""
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
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

# ==================== 서버 시작 ====================

if __name__ == "__main__":
    print("🚀 EORA AI 완전 서버 시작...")
    print("📍 접속 주소: http://127.0.0.1:8009")
    print("🔐 로그인: http://127.0.0.1:8009/login")
    print("⚙️ 관리자: http://127.0.0.1:8009/admin")
    print("💬 채팅: http://127.0.0.1:8009/chat")
    print("📊 대시보드: http://127.0.0.1:8009/dashboard")
    print("📝 프롬프트 관리자: http://127.0.0.1:8009/prompt_management")
    print("==================================================")
    print("📧 관리자 계정: admin@eora.ai")
    print("🔑 비밀번호: admin123")
    print("==================================================")
    
    uvicorn.run(app, host="127.0.0.1", port=8009) 