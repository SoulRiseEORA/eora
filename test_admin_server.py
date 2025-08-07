#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
관리자 로그인 테스트 서버
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timedelta

try:
    import uvicorn
    from fastapi import FastAPI, Request, Response, HTTPException
    from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
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

app = FastAPI(title="관리자 테스트 서버")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 템플릿 설정
templates_dir = os.path.join(os.path.dirname(__file__), "src", "templates")
if os.path.exists(templates_dir):
    templates = Jinja2Templates(directory=templates_dir)
    print(f"✅ 템플릿 디렉토리: {os.path.relpath(templates_dir)}")
else:
    templates = None
    print(f"❌ 템플릿 디렉토리를 찾을 수 없습니다: {templates_dir}")

# 정적 파일 설정
static_dir = os.path.join(os.path.dirname(__file__), "src", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    print(f"✅ 정적 파일 마운트: {os.path.relpath(static_dir)}")

# 인증 설정
SECRET_KEY = "eora_super_secret_key_2024_07_11_!@#"
ALGORITHM = "HS256"

# 사용자 데이터베이스 (메모리)
users_db = {
    "admin@eora.ai": {
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "is_admin": True,
        "name": "관리자"
    },
    "test@eora.ai": {
        "password_hash": hashlib.sha256("test123".encode()).hexdigest(),
        "is_admin": False,
        "name": "테스트 사용자"
    }
}

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
        
        return None
    except Exception as e:
        print(f"❌ 사용자 정보 확인 오류: {e}")
        return None

# ==================== 페이지 라우트 ====================

@app.get("/")
async def root(request: Request):
    """홈페이지"""
    user = get_current_user(request)
    if templates:
        return templates.TemplateResponse("home.html", {
            "request": request,
            "user": user
        })
    return HTMLResponse("<h1>홈페이지</h1><a href='/login'>로그인</a>")

@app.get("/login")
async def login_page(request: Request):
    """로그인 페이지"""
    if templates:
        return templates.TemplateResponse("login.html", {"request": request})
    return HTMLResponse("""
        <h1>로그인</h1>
        <form action="/api/login" method="post">
            <input type="email" name="email" placeholder="이메일" value="admin@eora.ai"><br>
            <input type="password" name="password" placeholder="비밀번호" value="admin123"><br>
            <button type="submit">로그인</button>
        </form>
    """)

@app.get("/admin")
async def admin_page(request: Request):
    """관리자 페이지"""
    user = get_current_user(request)
    is_admin = user.get("is_admin", False) if user else False
    
    if not is_admin:
        return RedirectResponse(url="/login", status_code=302)
    
    if templates:
        return templates.TemplateResponse("admin.html", {
            "request": request,
            "user": user
        })
    return HTMLResponse(f"<h1>관리자 페이지</h1><p>환영합니다, {user['email']}!</p>")

# ==================== 인증 API ====================

# 모든 로그인 엔드포인트 지원
@app.post("/api/login")
@app.post("/api/admin/login")
@app.post("/api/auth/login")
async def login_api(request: Request):
    """로그인 API"""
    try:
        # Content-Type 확인
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            data = await request.json()
        elif "application/x-www-form-urlencoded" in content_type:
            form_data = await request.form()
            data = dict(form_data)
        else:
            # 기본적으로 JSON으로 시도
            data = await request.json()
        
        email = data.get("email")
        password = data.get("password")
        
        print(f"🔐 로그인 시도: {email}")
        print(f"📋 사용 가능한 사용자: {list(users_db.keys())}")
        
        if not email or not password:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "이메일과 비밀번호를 입력하세요."}
            )
        
        # 사용자 확인
        user = users_db.get(email)
        if not user:
            print(f"❌ 사용자를 찾을 수 없음: {email}")
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "존재하지 않는 계정입니다."}
            )
        
        # 비밀번호 확인
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user["password_hash"] != password_hash:
            print(f"❌ 비밀번호 불일치")
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "비밀번호가 올바르지 않습니다."}
            )
        
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
                "name": user.get("name", email.split("@")[0])
            }
        })
        
        # 쿠키 설정
        response.set_cookie(key="user_email", value=email, max_age=86400)
        response.set_cookie(key="access_token", value=token, max_age=86400)
        
        print(f"✅ 로그인 성공: {email}")
        return response
        
    except Exception as e:
        print(f"❌ 로그인 오류: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"서버 오류: {str(e)}"}
        )

@app.post("/api/logout")
async def logout_api(response: Response):
    """로그아웃 API"""
    response = JSONResponse({"success": True, "message": "로그아웃 성공"})
    response.delete_cookie("user_email")
    response.delete_cookie("access_token")
    return response

# ==================== 관리자 API ====================

@app.get("/api/admin/stats")
async def admin_stats(request: Request):
    """관리자 통계"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    return {
        "total_users": len(users_db),
        "admin_users": sum(1 for u in users_db.values() if u.get("is_admin")),
        "active_sessions": 0,
        "server_status": "정상"
    }

if __name__ == "__main__":
    print("🚀 관리자 로그인 테스트 서버 시작...")
    print("📍 접속 주소: http://127.0.0.1:8012")
    print("🔐 로그인: http://127.0.0.1:8012/login")
    print("⚙️ 관리자: http://127.0.0.1:8012/admin")
    print("==================================================")
    print("📧 관리자 계정: admin@eora.ai")
    print("🔑 비밀번호: admin123")
    print("==================================================")
    uvicorn.run(app, host="127.0.0.1", port=8012, reload=False) 