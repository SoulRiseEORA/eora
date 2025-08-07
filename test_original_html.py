#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI - 원본 HTML 테스트 서버
"""

import sys
import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# FastAPI 및 관련 모듈 임포트
try:
    import uvicorn
    from fastapi import FastAPI, Request, Response, HTTPException
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
    input("Enter를 눌러 종료...")
    sys.exit(1)

app = FastAPI(title="EORA AI Original HTML Test Server")

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
        "name": "admin",
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "is_admin": True,
        "created_at": datetime.now().isoformat()
    }
}

def get_current_user(request: Request):
    """현재 사용자 정보 가져오기"""
    user = None
    
    # 쿠키에서 사용자 정보 확인
    try:
        user_cookie = request.cookies.get("user")
        if user_cookie:
            user = json.loads(user_cookie)
    except:
        pass
    
    return user

@app.get("/")
async def root(request: Request):
    """홈페이지 - 원본 home.html 사용"""
    user = get_current_user(request)
    is_admin = user.get("is_admin", False) if user else False
    
    if templates:
        try:
            return templates.TemplateResponse("home.html", {
                "request": request,
                "user": user,
                "is_admin": is_admin
            })
        except Exception as e:
            print(f"⚠️ 원본 템플릿 로드 실패: {e}")
    
    # 기본 홈페이지
    return HTMLResponse(content="<h1>EORA AI 홈페이지</h1><p>원본 HTML 로드 실패</p>")

@app.get("/login")
async def login_page(request: Request):
    """로그인 페이지 - 원본 login.html 사용"""
    if templates:
        try:
            return templates.TemplateResponse("login.html", {"request": request})
        except Exception as e:
            print(f"⚠️ 원본 로그인 템플릿 로드 실패: {e}")
    
    # 기본 로그인 페이지
    return HTMLResponse(content="<h1>로그인 페이지</h1><p>원본 HTML 로드 실패</p>")

@app.post("/api/auth/login")
async def login_api(request: Request):
    """로그인 API"""
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        
        print(f"로그인 시도: {email}")
        
        if not email or not password:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "이메일과 비밀번호를 입력하세요."}
            )
        
        # 사용자 확인
        user = users_db.get(email)
        if not user:
            print(f"사용자 없음: {email}")
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "존재하지 않는 계정입니다."}
            )
        
        # 비밀번호 확인
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user["password_hash"] != password_hash:
            print(f"비밀번호 오류: {email}")
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "비밀번호가 올바르지 않습니다."}
            )
        
        print(f"로그인 성공: {email}")
        
        # JWT 토큰 생성
        access_token = jwt.encode(
            {
                "sub": user["email"],
                "email": user["email"],
                "role": user["role"],
                "is_admin": user["is_admin"],
                "exp": datetime.utcnow() + timedelta(hours=24)
            },
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        
        # 쿠키에 사용자 정보 저장
        response = JSONResponse(content={
            "success": True,
            "message": "로그인 성공",
            "user": {
                "email": user["email"],
                "name": user["name"],
                "role": user["role"],
                "is_admin": user["is_admin"]
            },
            "access_token": access_token
        })
        
        response.set_cookie(
            key="user",
            value=json.dumps({
                "email": user["email"],
                "role": user["role"],
                "is_admin": user["is_admin"]
            }),
            max_age=60 * 60 * 24 * 30,  # 30일
            httponly=False
        )
        
        return response
        
    except Exception as e:
        print(f"로그인 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"로그인 중 오류가 발생했습니다: {str(e)}"}
        )

@app.post("/api/auth/register")
async def register_api(request: Request):
    """회원가입 API"""
    try:
        data = await request.json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        
        print(f"회원가입 시도: {email}")
        
        if not name or not email or not password:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "이름, 이메일, 비밀번호를 모두 입력하세요."}
            )
        
        # 이메일 중복 확인
        if email in users_db:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "이미 존재하는 이메일입니다."}
            )
        
        # 새 사용자 생성
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        users_db[email] = {
            "email": email,
            "name": name,
            "password_hash": password_hash,
            "role": "user",
            "is_admin": False,
            "created_at": datetime.now().isoformat()
        }
        
        print(f"회원가입 성공: {email}")
        
        # JWT 토큰 생성
        access_token = jwt.encode(
            {
                "sub": email,
                "email": email,
                "role": "user",
                "is_admin": False,
                "exp": datetime.utcnow() + timedelta(hours=24)
            },
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        
        response = JSONResponse(content={
            "success": True,
            "message": "회원가입 성공",
            "user": {
                "email": email,
                "name": name,
                "role": "user",
                "is_admin": False
            },
            "access_token": access_token
        })
        
        response.set_cookie(
            key="user",
            value=json.dumps({
                "email": email,
                "role": "user",
                "is_admin": False
            }),
            max_age=60 * 60 * 24 * 30,  # 30일
            httponly=False
        )
        
        return response
        
    except Exception as e:
        print(f"회원가입 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"회원가입 중 오류가 발생했습니다: {str(e)}"}
        )

@app.get("/admin")
async def admin_page(request: Request):
    """관리자 페이지 - 원본 admin.html 사용"""
    user = get_current_user(request)
    is_admin = user.get("is_admin", False) if user else False
    
    if not is_admin:
        return RedirectResponse(url="/login", status_code=302)
    
    if templates:
        try:
            return templates.TemplateResponse("admin.html", {
                "request": request,
                "user": user,
                "is_admin": is_admin
            })
        except Exception as e:
            print(f"⚠️ 원본 관리자 템플릿 로드 실패: {e}")
    
    # 기본 관리자 페이지
    return HTMLResponse(content="<h1>관리자 페이지</h1><p>원본 HTML 로드 실패</p>")

@app.get("/health")
async def health():
    """헬스 체크"""
    return {"status": "healthy", "message": "서버가 정상 작동 중입니다."}

if __name__ == "__main__":
    print("🚀 EORA AI 원본 HTML 테스트 서버 시작...")
    print("📍 접속 주소: http://127.0.0.1:8006")
    print("🔐 로그인: http://127.0.0.1:8006/login")
    print("⚙️ 관리자: http://127.0.0.1:8006/admin")
    print("=" * 50)
    print("📧 관리자 계정: admin@eora.ai")
    print("🔑 비밀번호: admin123")
    print("=" * 50)
    
    try:
        uvicorn.run(app, host="127.0.0.1", port=8006, log_level="info")
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        import traceback
        traceback.print_exc()
        input("Enter를 눌러 종료...") 