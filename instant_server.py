#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI 즉시 실행 서버
- 홈페이지 즉시 접속 가능
- 모든 페이지 연결
- 관리자 로그인 정상 작동
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List

try:
    import uvicorn
    from fastapi import FastAPI, Request, Response, HTTPException, Depends, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    import jwt
    print("✅ 모든 모듈 로드 성공")
except ImportError as e:
    print(f"❌ 모듈 로드 실패: {e}")
    print("필요한 패키지 설치: pip install fastapi uvicorn jinja2 python-multipart PyJWT")
    sys.exit(1)

# FastAPI 앱 생성
app = FastAPI(title="EORA AI 즉시 서버")

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

# JWT 설정
SECRET_KEY = "your-secret-key-for-jwt-encoding"
ALGORITHM = "HS256"

# 메모리 저장소
users_db = {
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
}

sessions_db = {}
messages_db = {}

# 프롬프트 데이터 로드
prompts_data = {}
prompts_file_path = os.path.join(os.path.dirname(__file__), "src", "ai_prompts.json")
backup_prompts_path = os.path.join(os.path.dirname(__file__), "ai_prompts.json")

def load_prompts():
    """프롬프트 데이터 로드"""
    global prompts_data
    try:
        # src 폴더에서 먼저 찾기
        if os.path.exists(prompts_file_path):
            with open(prompts_file_path, "r", encoding="utf-8") as f:
                prompts_data = json.load(f)
                print(f"✅ 프롬프트 데이터 로드 (src): {len(prompts_data)}개 AI")
        # 루트 폴더에서 찾기
        elif os.path.exists(backup_prompts_path):
            with open(backup_prompts_path, "r", encoding="utf-8") as f:
                prompts_data = json.load(f)
                print(f"✅ 프롬프트 데이터 로드 (root): {len(prompts_data)}개 AI")
        else:
            print(f"⚠️ 프롬프트 파일을 찾을 수 없습니다")
            prompts_data = {}
    except Exception as e:
        print(f"❌ 프롬프트 로드 오류: {e}")
        prompts_data = {}

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
            user["is_admin"] = (email == "admin@eora.ai")
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

@app.get("/prompt-management", response_class=HTMLResponse)
async def prompt_management_alt(request: Request):
    """프롬프트 관리 페이지 (대체 URL)"""
    return await prompt_management_page(request)

@app.get("/memory", response_class=HTMLResponse)
async def memory_page(request: Request):
    """메모리 페이지"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("memory.html", {
        "request": request,
        "user": user
    })

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """프로필 페이지"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user
    })

@app.get("/test", response_class=HTMLResponse)
async def test_page(request: Request):
    """테스트 페이지"""
    return templates.TemplateResponse("test.html", {"request": request})

@app.get("/aura_system", response_class=HTMLResponse)
async def aura_system_page(request: Request):
    """아우라 시스템 페이지"""
    user = get_current_user(request)
    return templates.TemplateResponse("aura_system.html", {
        "request": request,
        "user": user
    })

@app.get("/learning", response_class=HTMLResponse)
async def learning_page(request: Request):
    """학습 페이지"""
    user = get_current_user(request)
    return templates.TemplateResponse("learning.html", {
        "request": request,
        "user": user
    })

@app.get("/points", response_class=HTMLResponse)
async def points_page(request: Request):
    """포인트 페이지"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("points.html", {
        "request": request,
        "user": user
    })

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """회원가입 페이지"""
    return templates.TemplateResponse("register.html", {"request": request})

# ==================== API 엔드포인트 ====================

@app.post("/api/auth/register")
async def register_api(request: Request):
    """회원가입 API"""
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        name = data.get("name")
        
        # 입력값 검증
        if not email or not password or not name:
            return JSONResponse(
                {"success": False, "message": "모든 필드를 입력해주세요."},
                status_code=400
            )
        
        # 이메일 중복 확인
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
        
        print(f"✅ 회원가입 성공: {email}")
        
        # 자동 로그인 처리
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
                
                return JSONResponse({
                    "success": True,
                    "user": {
                        "email": user["email"],
                        "name": user["name"],
                        "role": user["role"],
                        "is_admin": user.get("is_admin", False)
                    },
                    "access_token": access_token
                })
        
        print(f"❌ 로그인 실패: {email}")
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

# 호환성을 위한 다른 로그인 엔드포인트
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
            role_text = prompt_data.get("role", "")
            guide_text = prompt_data.get("guide", "")
            format_text = prompt_data.get("format", "")
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
        role_text = prompt_data.get("role", "")
        guide_text = prompt_data.get("guide", "")
        format_text = prompt_data.get("format", "")
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
        save_path = prompts_file_path if os.path.exists(os.path.dirname(prompts_file_path)) else backup_prompts_path
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(prompts_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 프롬프트 업데이트: {ai_id}")
        
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

@app.get("/api/sessions")
async def get_sessions(request: Request):
    """세션 목록 조회"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({"sessions": []})
    
    user_email = user["email"]
    user_sessions = [
        {
            "id": session_id,
            "name": session_data.get("name", f"세션 {idx + 1}"),
            "created_at": session_data.get("created_at", datetime.now().isoformat()),
            "message_count": len(messages_db.get(session_id, []))
        }
        for idx, (session_id, session_data) in enumerate(sessions_db.items())
        if session_data.get("user_email") == user_email
    ]
    
    print(f"📂 사용자 {user_email}의 세션 목록: {len(user_sessions)}개")
    return JSONResponse({"sessions": user_sessions})

@app.post("/api/sessions")
async def create_session(request: Request):
    """새 세션 생성"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    user_email = user["email"]
    timestamp = int(datetime.now().timestamp() * 1000)
    session_id = f"session_{user_email.replace('@', '_').replace('.', '_')}_{timestamp}"
    
    sessions_db[session_id] = {
        "user_email": user_email,
        "created_at": datetime.now().isoformat(),
        "name": f"새 대화 {len([s for s in sessions_db.values() if s.get('user_email') == user_email]) + 1}"
    }
    messages_db[session_id] = []
    
    print(f"🆕 새 세션 생성: {user_email} -> {session_id}")
    print(f"📂 사용자 {user_email}의 총 세션 수: {len([s for s in sessions_db.values() if s.get('user_email') == user_email])}")
    
    return JSONResponse({
        "id": session_id,
        "name": sessions_db[session_id]["name"],
        "created_at": sessions_db[session_id]["created_at"]
    })

@app.get("/api/user/points")
async def get_user_points(request: Request):
    """사용자 포인트 조회"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({"points": 0})
    
    return JSONResponse({"points": 1000})

@app.post("/api/set-language")
async def set_language(request: Request):
    """언어 설정"""
    return JSONResponse({"success": True})

@app.get("/api/user/stats")
async def user_stats(request: Request):
    """사용자 통계"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    return JSONResponse({
        "total_chats": 10,
        "total_messages": 50,
        "points": 1000,
        "level": 3
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

# WebSocket 연결
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    print(f"✅ WebSocket 연결: {client_id}")
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print(f"❌ WebSocket 연결 종료: {client_id}")

# 메인 실행
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 EORA AI 즉시 실행 서버")
    print("="*50)
    print(f"📍 홈페이지: http://127.0.0.1:8013")
    print(f"🔐 로그인: http://127.0.0.1:8013/login")
    print(f"📝 회원가입: http://127.0.0.1:8013/register")
    print(f"⚙️ 관리자: http://127.0.0.1:8013/admin")
    print(f"📋 프롬프트 관리: http://127.0.0.1:8013/prompt_management")
    print("="*50)
    print("📧 관리자: admin@eora.ai / 비밀번호: admin123")
    print("📧 테스트: test@eora.ai / 비밀번호: test123")
    print("="*50)
    print(f"📄 프롬프트 파일: {len(prompts_data)}개 AI 로드됨")
    print("="*50)
    
    uvicorn.run(app, host="127.0.0.1", port=8013, log_level="info") 