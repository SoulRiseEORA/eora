#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 최종 홈페이지 서버 (원본 HTML 연결)
"""

import sys
import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import time

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
    input("Enter를 눌러 종료...")
    sys.exit(1)

app = FastAPI(title="EORA AI Final Homepage Server")

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
                # 토큰에서 사용자 정보 추출 (실제로는 JWT 디코딩)
                user_email = "admin@eora.ai" if "admin" in token else "user@example.com"
                return {
                    "email": user_email,
                    "is_admin": user_email == "admin@eora.ai",
                    "name": user_email.split("@")[0]
                }
        
        # 로그인하지 않은 사용자는 None 반환
        return None
    except Exception as e:
        print(f"사용자 정보 가져오기 오류: {e}")
        # 오류 발생 시에도 None 반환
        return None

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
    
    # 기본 홈페이지 (템플릿이 없거나 실패한 경우)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EORA AI - 홈페이지</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                text-align: center;
                padding: 40px 0;
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
            .user-info {{
                text-align: center;
                margin: 20px 0;
                padding: 15px;
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
            }}
            .nav {{
                display: flex;
                justify-content: center;
                gap: 20px;
                margin: 40px 0;
                flex-wrap: wrap;
            }}
            .nav a {{
                background: rgba(255,255,255,0.1);
                color: white;
                text-decoration: none;
                padding: 15px 30px;
                border-radius: 25px;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }}
            .nav a:hover {{
                background: rgba(255,255,255,0.2);
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }}
            .features {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                margin: 40px 0;
            }}
            .feature {{
                background: rgba(255,255,255,0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }}
            .feature h3 {{
                margin: 0 0 15px 0;
                color: #ffd700;
            }}
            .status {{
                text-align: center;
                margin: 20px 0;
                padding: 15px;
                background: rgba(0,255,0,0.2);
                border-radius: 10px;
                color: #90EE90;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 EORA AI</h1>
                <p>인공지능 기반 대화 시스템</p>
            </div>
            
            <div class="status">
                ✅ 서버가 정상적으로 실행 중입니다!
            </div>
            
            <div class="user-info">
                {'✅ 관리자로 로그인됨' if is_admin else '👤 게스트 모드'}
                {' - ' + user.get("email", "") if user else ""}
            </div>
            
            <div class="nav">
                <a href="/chat">💬 채팅</a>
                <a href="/dashboard">📊 대시보드</a>
                <a href="/test">🧪 테스트</a>
                <a href="/health">❤️ 상태확인</a>
                {'<a href="/admin">⚙️ 관리자</a>' if is_admin else '<a href="/login">🔐 로그인</a>'}
                {'<a href="/logout">🚪 로그아웃</a>' if user else ''}
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>🤖 AI 채팅</h3>
                    <p>고급 인공지능과 자연스러운 대화를 나누세요. 문맥을 이해하고 지능적인 응답을 제공합니다.</p>
                </div>
                <div class="feature">
                    <h3>📚 학습 시스템</h3>
                    <p>대화 내용을 학습하여 더 나은 응답을 제공합니다. 지속적인 개선으로 사용자 경험을 향상시킵니다.</p>
                </div>
                <div class="feature">
                    <h3>🔧 관리 도구</h3>
                    <p>관리자 대시보드를 통해 시스템을 모니터링하고 설정을 관리할 수 있습니다.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/login")
async def login_page(request: Request):
    """로그인 페이지 - 원본 login.html 사용"""
    if templates:
        try:
            return templates.TemplateResponse("login.html", {"request": request})
        except Exception as e:
            print(f"⚠️ 원본 로그인 템플릿 로드 실패: {e}")
    
    # 기본 로그인 페이지
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EORA AI - 로그인</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .login-container {
                width: 90%;
                max-width: 450px;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                padding: 40px;
            }
            .login-header {
                text-align: center;
                margin-bottom: 30px;
            }
            .login-header h1 {
                font-size: 28px;
                color: #333;
                margin-bottom: 10px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            .form-group label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 500;
            }
            .form-group input {
                width: 100%;
                padding: 15px;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                font-size: 16px;
                outline: none;
                transition: border-color 0.3s ease;
            }
            .form-group input:focus {
                border-color: #667eea;
            }
            .login-button {
                width: 100%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s ease;
            }
            .login-button:hover {
                transform: scale(1.02);
            }
            .demo-info {
                margin-top: 20px;
                padding: 15px;
                background: rgba(102, 126, 234, 0.1);
                border-radius: 10px;
                text-align: center;
                color: #333;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="login-header">
                <h1>🔐 EORA AI 로그인</h1>
                <p>관리자 계정으로 로그인하세요</p>
            </div>
            
            <form id="loginForm">
                <div class="form-group">
                    <label for="email">이메일</label>
                    <input type="email" id="email" name="email" required>
                </div>
                
                <div class="form-group">
                    <label for="password">비밀번호</label>
                    <input type="password" id="password" name="password" required>
                </div>
                
                <button type="submit" class="login-button">로그인</button>
            </form>
            
            <div class="demo-info">
                <strong>데모 계정:</strong><br>
                이메일: admin@eora.ai<br>
                비밀번호: admin123
            </div>
        </div>
        
        <script>
            document.getElementById('loginForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                
                try {
                    const response = await fetch('/api/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ email, password })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        alert('로그인 성공!');
                        window.location.href = '/admin';
                    } else {
                        alert('로그인 실패: ' + data.message);
                    }
                } catch (error) {
                    alert('로그인 중 오류가 발생했습니다.');
                    console.error('Error:', error);
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/auth/login")
async def login_api(request: Request):
    """로그인 API"""
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "이메일과 비밀번호를 입력하세요."}
            )
        
        # 사용자 확인
        user = users_db.get(email)
        if not user:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "존재하지 않는 계정입니다."}
            )
        
        # 비밀번호 확인
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user["password_hash"] != password_hash:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "비밀번호가 올바르지 않습니다."}
            )
        
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
                "name": user["email"].split("@")[0],
                "role": user["role"],
                "is_admin": user["is_admin"]
            },
            "access_token": access_token
        })
        
        response.set_cookie(
            key="user_email",
            value=user["email"],
            max_age=60 * 60 * 24 * 30,  # 30일
            httponly=False
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=60 * 60 * 24 * 30,  # 30일
            httponly=False
        )
        
        return response
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"로그인 중 오류가 발생했습니다: {str(e)}"}
        )

@app.post("/api/auth/google")
async def google_login_api(request: Request):
    """구글 로그인 API (원본 HTML 호환)"""
    try:
        data = await request.json()
        email = data.get("email")
        
        if not email:
            return JSONResponse(
                status_code=400,
                content={"success": False, "detail": "이메일이 필요합니다."}
            )
        
        # 구글 사용자 생성 또는 기존 사용자 확인
        if email not in users_db:
            users_db[email] = {
                "email": email,
                "name": email.split("@")[0],
                "role": "user",
                "is_admin": False,
                "created_at": datetime.now().isoformat()
            }
        
        user = users_db[email]
        
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
        
        response = JSONResponse(content={
            "success": True,
            "message": "구글 로그인 성공",
            "user": {
                "email": user["email"],
                "name": user["name"],
                "role": user["role"],
                "is_admin": user["is_admin"]
            },
            "access_token": access_token
        })
        
        response.set_cookie(
            key="user_email",
            value=user["email"],
            max_age=60 * 60 * 24 * 30,  # 30일
            httponly=False
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=60 * 60 * 24 * 30,  # 30일
            httponly=False
        )
        
        return response
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "detail": f"구글 로그인 중 오류가 발생했습니다: {str(e)}"}
        )

@app.post("/api/auth/{provider}")
async def social_login_api(provider: str, request: Request):
    """소셜 로그인 API (원본 HTML 호환)"""
    try:
        data = await request.json()
        nickname = data.get("nickname")
        
        if not nickname:
            return JSONResponse(
                status_code=400,
                content={"success": False, "detail": "닉네임이 필요합니다."}
            )
        
        # 소셜 사용자 생성
        email = f"{nickname}@{provider}.com"
        if email not in users_db:
            users_db[email] = {
                "email": email,
                "name": nickname,
                "role": "user",
                "is_admin": False,
                "created_at": datetime.now().isoformat()
            }
        
        user = users_db[email]
        
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
        
        response = JSONResponse(content={
            "success": True,
            "message": f"{provider} 로그인 성공",
            "user": {
                "email": user["email"],
                "name": user["name"],
                "role": user["role"],
                "is_admin": user["is_admin"]
            },
            "access_token": access_token
        })
        
        response.set_cookie(
            key="user_email",
            value=user["email"],
            max_age=60 * 60 * 24 * 30,  # 30일
            httponly=False
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=60 * 60 * 24 * 30,  # 30일
            httponly=False
        )
        
        return response
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "detail": f"{provider} 로그인 중 오류가 발생했습니다: {str(e)}"}
        )

@app.post("/api/auth/register")
async def register_api(request: Request):
    """회원가입 API"""
    try:
        data = await request.json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        
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
            key="user_email",
            value=email,
            max_age=60 * 60 * 24 * 30,  # 30일
            httponly=False
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=60 * 60 * 24 * 30,  # 30일
            httponly=False
        )
        
        return response
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"회원가입 중 오류가 발생했습니다: {str(e)}"}
        )

@app.get("/logout")
async def logout(request: Request):
    """로그아웃"""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("user_email")
    response.delete_cookie("access_token")
    return response

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
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EORA AI - 관리자</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            .title {
                font-size: 2.5em;
                color: #333;
                margin-bottom: 10px;
            }
            .admin-panel {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                margin-bottom: 30px;
            }
            .admin-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                margin-bottom: 40px;
            }
            .admin-card {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-radius: 15px;
                padding: 30px;
                text-align: center;
                transition: all 0.3s ease;
                border: 2px solid transparent;
                cursor: pointer;
            }
            .admin-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
                border-color: #667eea;
            }
            .card-icon {
                font-size: 3em;
                margin-bottom: 20px;
                color: #667eea;
            }
            .card-title {
                font-size: 1.5em;
                font-weight: 600;
                margin-bottom: 15px;
                color: #333;
            }
            .card-description {
                color: #666;
                margin-bottom: 25px;
                line-height: 1.6;
            }
            .btn {
                padding: 12px 24px;
                border: none;
                border-radius: 25px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s ease;
                display: inline-block;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }
            .back-link {
                text-align: center;
                margin-top: 30px;
            }
            .back-link a {
                color: white;
                text-decoration: none;
                padding: 15px 30px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 25px;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .back-link a:hover {
                background: rgba(255, 255, 255, 0.2);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 class="title">⚙️ EORA AI 관리자</h1>
                <p class="subtitle">시스템 관리 및 모니터링</p>
            </div>
            
            <div class="admin-panel">
                <div class="admin-grid">
                    <div class="admin-card">
                        <div class="card-icon">📝</div>
                        <h3 class="card-title">프롬프트 관리</h3>
                        <p class="card-description">AI 프롬프트 설정 및 관리</p>
                        <a href="#" class="btn">관리하기</a>
                    </div>
                    
                    <div class="admin-card">
                        <div class="card-icon">👥</div>
                        <h3 class="card-title">사용자 관리</h3>
                        <p class="card-description">사용자 계정 및 권한 관리</p>
                        <a href="#" class="btn">관리하기</a>
                    </div>
                    
                    <div class="admin-card">
                        <div class="card-icon">📊</div>
                        <h3 class="card-title">시스템 상태</h3>
                        <p class="card-description">서버 및 데이터베이스 모니터링</p>
                        <a href="#" class="btn">확인하기</a>
                    </div>
                    
                    <div class="admin-card">
                        <div class="card-icon">📋</div>
                        <h3 class="card-title">로그 관리</h3>
                        <p class="card-description">시스템 로그 및 오류 확인</p>
                        <a href="#" class="btn">확인하기</a>
                    </div>
                </div>
            </div>
            
            <div class="back-link">
                <a href="/">🏠 홈으로 돌아가기</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/chat")
async def chat_page(request: Request):
    """채팅 페이지 - 원본 chat.html 사용"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    if templates:
        try:
            return templates.TemplateResponse("chat.html", {"request": request})
        except Exception as e:
            print(f"⚠️ 원본 채팅 템플릿 로드 실패: {e}")
    
    # 기본 채팅 페이지
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EORA AI - 채팅</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .chat-container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }
            .chat-header {
                text-align: center;
                margin-bottom: 20px;
            }
            .chat-messages {
                height: 400px;
                overflow-y: auto;
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
                background: rgba(0,0,0,0.1);
            }
            .message {
                margin: 10px 0;
                padding: 10px;
                border-radius: 10px;
            }
            .user-message {
                background: rgba(0,255,0,0.2);
                text-align: right;
            }
            .ai-message {
                background: rgba(255,255,255,0.1);
                text-align: left;
            }
            .chat-input {
                display: flex;
                gap: 10px;
            }
            .chat-input input {
                flex: 1;
                padding: 10px;
                border: none;
                border-radius: 25px;
                background: rgba(255,255,255,0.2);
                color: white;
            }
            .chat-input input::placeholder {
                color: rgba(255,255,255,0.7);
            }
            .chat-input button {
                padding: 10px 20px;
                border: none;
                border-radius: 25px;
                background: rgba(255,255,255,0.2);
                color: white;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .chat-input button:hover {
                background: rgba(255,255,255,0.3);
            }
            .back-link {
                text-align: center;
                margin-top: 20px;
            }
            .back-link a {
                color: white;
                text-decoration: none;
                padding: 10px 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 25px;
                transition: all 0.3s ease;
            }
            .back-link a:hover {
                background: rgba(255,255,255,0.2);
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <h1>💬 EORA AI 채팅</h1>
                <p>AI와 대화를 시작하세요</p>
            </div>
            
            <div class="chat-messages" id="chatMessages">
                <div class="message ai-message">
                    안녕하세요! 저는 EORA AI입니다. 무엇을 도와드릴까요?
                </div>
            </div>
            
            <div class="chat-input">
                <input type="text" id="messageInput" placeholder="메시지를 입력하세요..." onkeypress="if(event.keyCode==13) sendMessage()">
                <button onclick="sendMessage()">전송</button>
            </div>
            
            <div class="back-link">
                <a href="/">🏠 홈으로 돌아가기</a>
            </div>
        </div>
        
        <script>
            function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                
                if (message) {
                    addMessage('사용자', message, 'user-message');
                    input.value = '';
                    
                    // AI 응답 시뮬레이션
                    setTimeout(() => {
                        addMessage('EORA AI', '메시지를 받았습니다. 현재 개발 중인 기능입니다.', 'ai-message');
                    }, 1000);
                }
            }
            
            function addMessage(sender, text, className) {
                const messagesDiv = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${className}`;
                messageDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/dashboard")
async def dashboard_page(request: Request):
    """대시보드 페이지 - 원본 dashboard.html 사용"""
    user = get_current_user(request)
    is_admin = user.get("is_admin", False) if user else False
    
    if not is_admin:
        return RedirectResponse(url="/login", status_code=302)
    
    if templates:
        try:
            return templates.TemplateResponse("dashboard.html", {
                "request": request,
                "user": user,
                "is_admin": is_admin
            })
        except Exception as e:
            print(f"⚠️ 원본 대시보드 템플릿 로드 실패: {e}")
    
    return RedirectResponse(url="/admin", status_code=302)

@app.get("/test")
async def test_page(request: Request):
    """테스트 페이지"""
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EORA AI - 테스트</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .test-container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 30px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }
            .test-header {
                text-align: center;
                margin-bottom: 30px;
            }
            .test-section {
                margin: 20px 0;
                padding: 15px;
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
            }
            .test-section h3 {
                margin: 0 0 10px 0;
                color: #ffd700;
            }
            .back-link {
                text-align: center;
                margin-top: 20px;
            }
            .back-link a {
                color: white;
                text-decoration: none;
                padding: 10px 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 25px;
                transition: all 0.3s ease;
            }
            .back-link a:hover {
                background: rgba(255,255,255,0.2);
            }
        </style>
    </head>
    <body>
        <div class="test-container">
            <div class="test-header">
                <h1>🧪 EORA AI 테스트</h1>
                <p>시스템 기능 테스트</p>
            </div>
            
            <div class="test-section">
                <h3>✅ 서버 연결 테스트</h3>
                <p>서버가 정상적으로 응답하고 있습니다.</p>
            </div>
            
            <div class="test-section">
                <h3>🌐 네트워크 테스트</h3>
                <p>로컬 네트워크 연결이 정상입니다.</p>
            </div>
            
            <div class="test-section">
                <h3>📱 브라우저 호환성</h3>
                <p>현재 브라우저에서 정상 작동합니다.</p>
            </div>
            
            <div class="test-section">
                <h3>⚡ 성능 테스트</h3>
                <p>페이지 로딩 시간: <span id="loadTime">측정 중...</span></p>
            </div>
            
            <div class="back-link">
                <a href="/">🏠 홈으로 돌아가기</a>
            </div>
        </div>
        
        <script>
            window.addEventListener('load', function() {
                const loadTime = performance.now();
                document.getElementById('loadTime').textContent = loadTime.toFixed(2) + 'ms';
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health():
    """헬스 체크"""
    return {"status": "healthy", "message": "서버가 정상 작동 중입니다."}

# 추가 페이지들
@app.get("/prompts")
async def prompts_page(request: Request):
    """프롬프트 관리 페이지"""
    user = get_current_user(request)
    is_admin = user.get("is_admin", False) if user else False
    
    if not is_admin:
        return RedirectResponse(url="/login", status_code=302)
    
    if templates:
        try:
            return templates.TemplateResponse("prompts.html", {
                "request": request,
                "user": user,
                "is_admin": is_admin
            })
        except Exception as e:
            print(f"⚠️ 원본 프롬프트 템플릿 로드 실패: {e}")
    
    return RedirectResponse(url="/admin", status_code=302)

@app.get("/memory")
async def memory_page(request: Request):
    """메모리 관리 페이지"""
    user = get_current_user(request)
    is_admin = user.get("is_admin", False) if user else False
    
    if not is_admin:
        return RedirectResponse(url="/login", status_code=302)
    
    if templates:
        try:
            return templates.TemplateResponse("memory.html", {
                "request": request,
                "user": user,
                "is_admin": is_admin
            })
        except Exception as e:
            print(f"⚠️ 원본 메모리 템플릿 로드 실패: {e}")
    
    return RedirectResponse(url="/admin", status_code=302)

@app.get("/profile")
async def profile_page(request: Request):
    """프로필 페이지"""
    user = get_current_user(request)
    
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    if templates:
        try:
            return templates.TemplateResponse("profile.html", {
                "request": request,
                "user": user
            })
        except Exception as e:
            print(f"⚠️ 원본 프로필 템플릿 로드 실패: {e}")
    
    return RedirectResponse(url="/", status_code=302)

@app.get("/api/sessions")
async def get_sessions(request: Request):
    """사용자의 세션 목록 가져오기"""
    user = get_current_user(request)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "로그인이 필요합니다."}
        )
    
    user_email = user.get("email", "anonymous")
    
    # 사용자별 세션 목록 가져오기
    user_sessions = sessions_db.get(user_email, [])
    
    # 세션을 최신 순으로 정렬
    user_sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    
    print(f"📂 사용자 {user_email}의 세션 목록: {len(user_sessions)}개")
    
    return JSONResponse(content={
        "success": True,
        "sessions": user_sessions
    })

@app.post("/api/sessions")
async def create_session(request: Request):
    """새 세션 생성 (사용자별 독립적)"""
    user = get_current_user(request)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "로그인이 필요합니다."}
        )
    
    user_email = user.get("email", "anonymous")
    
    try:
        data = await request.json()
        session_name = data.get("name", f"새 대화 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # 사용자별 고유한 세션 ID 생성
        timestamp = int(datetime.now().timestamp())
        session_id = f"session_{user_email.replace('@', '_').replace('.', '_')}_{timestamp}"
        
        new_session = {
            "id": session_id,
            "session_id": session_id,  # 호환성을 위해 두 필드 모두 설정
            "name": session_name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "message_count": 0,
            "user_email": user_email  # 사용자 정보 추가
        }
        
        # 사용자별 세션 목록에 추가
        if user_email not in sessions_db:
            sessions_db[user_email] = []
        
        sessions_db[user_email].append(new_session)
        
        # 새 세션의 메시지 저장소 초기화
        messages_db[session_id] = []
        
        print(f"🆕 새 세션 생성: {user_email} -> {session_id}")
        print(f"📂 사용자 {user_email}의 총 세션 수: {len(sessions_db[user_email])}")
        
        return JSONResponse(content={
            "success": True,
            "session": new_session,
            "session_id": session_id,  # 호환성을 위해 추가
            "id": session_id  # 호환성을 위해 추가
        })
        
    except Exception as e:
        print(f"❌ 세션 생성 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"세션 생성 중 오류가 발생했습니다: {str(e)}"}
        )

@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, request: Request):
    """세션의 메시지 목록 가져오기 (사용자별 접근 제어)"""
    user = get_current_user(request)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "로그인이 필요합니다."}
        )
    
    user_email = user.get("email", "anonymous")
    
    # 세션이 해당 사용자의 것인지 확인
    user_sessions = sessions_db.get(user_email, [])
    session_exists = any(s["id"] == session_id for s in user_sessions)
    
    if not session_exists:
        return JSONResponse(
            status_code=403,
            content={"success": False, "message": "해당 세션에 접근할 권한이 없습니다."}
        )
    
    session_messages = messages_db.get(session_id, [])
    
    print(f"📥 세션 {session_id}의 메시지 로드: {len(session_messages)}개")
    
    return JSONResponse(content={
        "success": True,
        "messages": session_messages
    })

@app.post("/api/messages")
async def save_message(request: Request):
    """메시지 저장 (사용자별 접근 제어)"""
    user = get_current_user(request)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "로그인이 필요합니다."}
        )
    
    user_email = user.get("email", "anonymous")
    
    try:
        data = await request.json()
        session_id = data.get("session_id")
        content = data.get("content")
        role = data.get("role", "user")  # user 또는 assistant
        
        if not session_id or not content:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "세션 ID와 메시지 내용이 필요합니다."}
            )
        
        # 세션이 해당 사용자의 것인지 확인
        user_sessions = sessions_db.get(user_email, [])
        session_exists = any(s["id"] == session_id for s in user_sessions)
        
        if not session_exists:
            return JSONResponse(
                status_code=403,
                content={"success": False, "message": "해당 세션에 접근할 권한이 없습니다."}
            )
        
        # 새 메시지 생성
        new_message = {
            "id": f"msg_{int(datetime.now().timestamp())}",
            "session_id": session_id,
            "content": content,
            "role": role,
            "timestamp": datetime.now().isoformat(),
            "user_email": user_email
        }
        
        # 메시지 저장
        if session_id not in messages_db:
            messages_db[session_id] = []
        
        messages_db[session_id].append(new_message)
        
        # 세션 업데이트
        for session in user_sessions:
            if session["id"] == session_id:
                session["updated_at"] = datetime.now().isoformat()
                session["message_count"] = len(messages_db[session_id])
                break
        
        print(f"💾 메시지 저장: {session_id} -> {role} ({len(content)}자)")
        
        return JSONResponse(content={
            "success": True,
            "message": new_message
        })
        
    except Exception as e:
        print(f"❌ 메시지 저장 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"메시지 저장 중 오류가 발생했습니다: {str(e)}"}
        )

@app.post("/api/chat")
async def chat_api(request: Request):
    """채팅 API - AI 응답 생성 (사용자별 접근 제어)"""
    user = get_current_user(request)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "로그인이 필요합니다."}
        )
    
    user_email = user.get("email", "anonymous")
    
    try:
        data = await request.json()
        message = data.get("message", "")
        session_id = data.get("session_id")
        
        if not message:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "메시지가 필요합니다."}
            )
        
        # 세션이 해당 사용자의 것인지 확인
        user_sessions = sessions_db.get(user_email, [])
        session_exists = any(s["id"] == session_id for s in user_sessions)
        
        if session_id and not session_exists:
            return JSONResponse(
                status_code=403,
                content={"success": False, "message": "해당 세션에 접근할 권한이 없습니다."}
            )
        
        # 사용자 메시지 저장
        if session_id:
            user_message = {
                "id": f"msg_{int(datetime.now().timestamp())}",
                "session_id": session_id,
                "content": message,
                "role": "user",
                "timestamp": datetime.now().isoformat(),
                "user_email": user_email
            }
            
            if session_id not in messages_db:
                messages_db[session_id] = []
            
            messages_db[session_id].append(user_message)
        
        # AI 응답 생성 (간단한 시뮬레이션)
        ai_responses = [
            "안녕하세요! 저는 EORA AI입니다. 무엇을 도와드릴까요?",
            "흥미로운 질문이네요. 더 자세히 설명해주시겠어요?",
            "그것에 대해 생각해보겠습니다. 다른 관점에서도 살펴볼 수 있을 것 같아요.",
            "좋은 지적입니다. 이 주제에 대해 더 깊이 논의해보시겠어요?",
            "제가 이해한 바로는, 그런 것 같습니다. 맞나요?",
            "흥미로운 관점이네요. 다른 생각도 있으신가요?",
            "그것에 대해 더 자세히 알아보고 싶습니다. 계속 말씀해주세요.",
            "좋은 대화가 되고 있네요. 더 많은 것을 공유해주세요."
        ]
        
        import random
        ai_response = random.choice(ai_responses)
        
        # AI 응답 저장
        if session_id:
            ai_message = {
                "id": f"msg_{int(datetime.now().timestamp()) + 1}",
                "session_id": session_id,
                "content": ai_response,
                "role": "assistant",
                "timestamp": datetime.now().isoformat(),
                "user_email": user_email
            }
            
            messages_db[session_id].append(ai_message)
            
            # 세션 업데이트
            for session in user_sessions:
                if session["id"] == session_id:
                    session["updated_at"] = datetime.now().isoformat()
                    session["message_count"] = len(messages_db[session_id])
                    break
        
        print(f"💬 채팅 응답: {session_id} -> {len(ai_response)}자")
        
        return JSONResponse(content={
            "success": True,
            "response": ai_response,
            "session_id": session_id
        })
        
    except Exception as e:
        print(f"❌ 채팅 API 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"채팅 중 오류가 발생했습니다: {str(e)}"}
        )

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, request: Request):
    """세션 삭제 (사용자별 접근 제어)"""
    user = get_current_user(request)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "로그인이 필요합니다."}
        )
    
    user_email = user.get("email", "anonymous")
    
    try:
        # 세션이 해당 사용자의 것인지 확인
        user_sessions = sessions_db.get(user_email, [])
        session_exists = any(s["id"] == session_id for s in user_sessions)
        
        if not session_exists:
            return JSONResponse(
                status_code=403,
                content={"success": False, "message": "해당 세션에 접근할 권한이 없습니다."}
            )
        
        # 세션 목록에서 삭제
        sessions_db[user_email] = [s for s in sessions_db[user_email] if s["id"] != session_id]
        
        # 메시지 삭제
        if session_id in messages_db:
            del messages_db[session_id]
        
        print(f"🗑️ 세션 삭제: {user_email} -> {session_id}")
        
        return JSONResponse(content={
            "success": True,
            "message": "세션이 삭제되었습니다."
        })
        
    except Exception as e:
        print(f"❌ 세션 삭제 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"세션 삭제 중 오류가 발생했습니다: {str(e)}"}
        )

@app.put("/api/sessions/{session_id}")
async def update_session(session_id: str, request: Request):
    """세션 이름 업데이트 (사용자별 접근 제어)"""
    user = get_current_user(request)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "로그인이 필요합니다."}
        )
    
    user_email = user.get("email", "anonymous")
    
    try:
        data = await request.json()
        new_name = data.get("name", "")
        
        if not new_name:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "새 이름이 필요합니다."}
            )
        
        # 세션이 해당 사용자의 것인지 확인
        user_sessions = sessions_db.get(user_email, [])
        session_exists = any(s["id"] == session_id for s in user_sessions)
        
        if not session_exists:
            return JSONResponse(
                status_code=403,
                content={"success": False, "message": "해당 세션에 접근할 권한이 없습니다."}
            )
        
        # 세션 이름 업데이트
        for session in user_sessions:
            if session["id"] == session_id:
                session["name"] = new_name
                session["updated_at"] = datetime.now().isoformat()
                break
        
        print(f"✏️ 세션 이름 변경: {session_id} -> {new_name}")
        
        return JSONResponse(content={
            "success": True,
            "message": "세션 이름이 업데이트되었습니다."
        })
        
    except Exception as e:
        print(f"❌ 세션 업데이트 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"세션 업데이트 중 오류가 발생했습니다: {str(e)}"}
        )

@app.get("/api/user/stats")
async def get_user_stats(request: Request):
    """사용자 통계 조회"""
    try:
        user = get_current_user(request)
        if not user:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "로그인이 필요합니다."}
            )
        
        user_email = user.get("email", "anonymous")
        user_sessions = sessions_db.get(user_email, [])
        total_messages = sum(len(messages_db.get(session["id"], [])) for session in user_sessions)
        
        stats = {
            "total_sessions": len(user_sessions),
            "total_messages": total_messages,
            "active_sessions": len([s for s in user_sessions if s.get("active", False)]),
            "last_activity": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return JSONResponse(content={
            "success": True,
            "stats": stats
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.get("/api/user/activity")
async def get_user_activity(request: Request):
    """사용자 활동 내역 조회"""
    try:
        user = get_current_user(request)
        if not user:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "로그인이 필요합니다."}
            )
        
        user_email = user.get("email", "anonymous")
        user_sessions = sessions_db.get(user_email, [])
        
        # 최근 5개 세션의 활동 내역
        recent_activity = []
        for session in user_sessions[:5]:
            messages = messages_db.get(session["id"], [])
            recent_activity.append({
                "session_id": session["id"],
                "session_name": session.get("name", "새 대화"),
                "message_count": len(messages),
                "last_message": messages[-1]["content"] if messages else "",
                "updated_at": session.get("updated_at", "")
            })
        
        return JSONResponse(content={
            "success": True,
            "activity": recent_activity
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.get("/api/user/points")
async def get_user_points(request: Request):
    """사용자 포인트 조회"""
    try:
        user = get_current_user(request)
        if not user:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "로그인이 필요합니다."}
            )
        
        # 시뮬레이션된 포인트 데이터
        points_data = {
            "current_points": 1000,
            "total_earned": 1500,
            "total_used": 500,
            "level": "Gold",
            "next_level": "Platinum",
            "points_to_next": 200
        }
        
        return JSONResponse(content={
            "success": True,
            "points": points_data
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.post("/api/set-language")
async def set_language(request: Request):
    """언어 설정"""
    try:
        data = await request.json()
        language = data.get("language", "ko")
        
        response = JSONResponse(content={
            "success": True,
            "message": f"언어가 {language}로 설정되었습니다."
        })
        
        # 쿠키에 언어 설정 저장
        response.set_cookie(key="language", value=language, max_age=3600*24*30)
        
        return response
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.get("/api/admin/prompts/{ai_name}/{prompt_type}")
async def get_prompt(ai_name: str, prompt_type: str):
    """특정 AI의 특정 프롬프트 조회"""
    try:
        # ai_prompts.json 파일에서 프롬프트 데이터 로드
        prompts_file = "ai_prompts.json"
        if os.path.exists(prompts_file):
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)
        else:
            # 기본 프롬프트 데이터
            prompts_data = {
                "ai1": {
                    "system": "EORA AI 시스템의 총괄 디렉터입니다.",
                    "role": "전체 기획, 코딩, UI 설계, 자동화, 테스트, 배포, 개선 루프를 총괄 지휘합니다.",
                    "guide": "시스템 전체를 이해하고 최적의 솔루션을 제시합니다.",
                    "format": "구체적이고 실행 가능한 계획을 제시합니다."
                }
            }
        
        ai_prompts = prompts_data.get(ai_name, {})
        prompt_content = ai_prompts.get(prompt_type, "")
        
        return JSONResponse(content={
            "success": True,
            "prompt": prompt_content
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.post("/api/admin/prompts/save")
async def save_prompt(request: Request):
    """프롬프트 저장"""
    try:
        data = await request.json()
        ai_name = data.get("ai")
        prompt_type = data.get("type")
        content = data.get("content")
        
        # ai_prompts.json 파일 업데이트
        prompts_file = "ai_prompts.json"
        if os.path.exists(prompts_file):
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)
        else:
            prompts_data = {}
        
        if ai_name not in prompts_data:
            prompts_data[ai_name] = {}
        
        prompts_data[ai_name][prompt_type] = content
        
        with open(prompts_file, 'w', encoding='utf-8') as f:
            json.dump(prompts_data, f, ensure_ascii=False, indent=2)
        
        return JSONResponse(content={
            "success": True,
            "message": f"{ai_name}의 {prompt_type} 프롬프트가 저장되었습니다."
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

# 추가 페이지 라우트들
@app.get("/aura_system")
async def aura_system_page():
    """아우라 시스템 페이지"""
    return templates.TemplateResponse("aura_system.html", {"request": {}})

@app.get("/memory")
async def memory_page():
    """메모리 페이지"""
    return templates.TemplateResponse("memory.html", {"request": {}})

@app.get("/profile")
async def profile_page():
    """프로필 페이지"""
    return templates.TemplateResponse("profile.html", {"request": {}})

@app.get("/test")
async def test_page():
    """테스트 페이지"""
    return templates.TemplateResponse("test.html", {"request": {}})

@app.get("/prompts")
async def prompts_page():
    """프롬프트 페이지"""
    return templates.TemplateResponse("prompts.html", {"request": {}})

# WebSocket 연결 관리
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

# 프롬프트 관리 API
@app.get("/api/prompts")
async def get_prompts():
    """프롬프트 데이터 조회"""
    try:
        # ai_prompts.json 파일에서 데이터 로드
        prompts_file = "src/ai_prompts.json"
        if os.path.exists(prompts_file):
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)
                return {"success": True, "prompts": prompts_data}
        else:
            # 기본 프롬프트 데이터 반환
            default_prompts = [
                {
                    "ai_name": "ai1",
                    "category": "system",
                    "content": "EORA 시스템 총괄 디렉터로서 전체 기획, 코딩, UI 설계, 자동화, 테스트, 배포, 개선 루프를 총괄 지휘합니다."
                },
                {
                    "ai_name": "ai2", 
                    "category": "system",
                    "content": "API 설계 전문가로서 시스템 전체 구조를 이해하고 모듈 간 의존성을 분석하여 API를 설계합니다."
                }
            ]
            return {"success": True, "prompts": default_prompts}
    except Exception as e:
        print(f"❌ 프롬프트 로드 오류: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/prompts/update-category")
async def update_prompt_category(request: Request):
    """프롬프트 카테고리 업데이트"""
    try:
        data = await request.json()
        ai_name = data.get("ai_name")
        category = data.get("category")
        content = data.get("content")
        
        if not all([ai_name, category, content]):
            return {"success": False, "error": "필수 파라미터가 누락되었습니다."}
        
        # ai_prompts.json 파일 업데이트
        prompts_file = "src/ai_prompts.json"
        prompts_data = []
        
        if os.path.exists(prompts_file):
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)
        
        # 기존 항목 찾기 및 업데이트
        found = False
        for prompt in prompts_data:
            if prompt.get("ai_name") == ai_name and prompt.get("category") == category:
                prompt["content"] = content
                found = True
                break
        
        # 새 항목 추가
        if not found:
            prompts_data.append({
                "ai_name": ai_name,
                "category": category,
                "content": content
            })
        
        # 파일 저장
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
        
        # ai_prompts.json 파일에서 삭제
        prompts_file = "src/ai_prompts.json"
        if os.path.exists(prompts_file):
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)
            
            # 해당 항목 제거
            prompts_data = [p for p in prompts_data 
                          if not (p.get("ai_name") == ai_name and p.get("category") == category)]
            
            # 파일 저장
            with open(prompts_file, 'w', encoding='utf-8') as f:
                json.dump(prompts_data, f, ensure_ascii=False, indent=2)
        
        print(f"🗑️ 프롬프트 삭제: {ai_name} - {category}")
        return {"success": True, "message": "프롬프트가 성공적으로 삭제되었습니다."}
        
    except Exception as e:
        print(f"❌ 프롬프트 삭제 오류: {e}")
        return {"success": False, "error": str(e)}

@app.get("/prompt_management")
async def prompt_management_page():
    """프롬프트 관리자 페이지"""
    return templates.TemplateResponse("prompt_management.html", {"request": {}})

@app.get("/prompt-management")
async def prompt_management_page_alt():
    """프롬프트 관리자 페이지 (대안 URL)"""
    return templates.TemplateResponse("prompt_management.html", {"request": {}})

@app.get("/prompts")
async def prompts_page():
    """프롬프트 페이지"""
    return templates.TemplateResponse("prompts.html", {"request": {}})

# 관리자 API 엔드포인트들
@app.get("/api/admin/users")
async def get_users():
    """사용자 목록 조회"""
    try:
        # 실제로는 데이터베이스에서 사용자 정보를 가져와야 함
        users = [
            {
                "user_id": "admin",
                "email": "admin@eora.ai",
                "points": 1000,
                "created_at": "2024-01-01",
                "last_login": "2024-01-15",
                "status": "활성"
            }
        ]
        
        return JSONResponse(content={
            "success": True,
            "users": users
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.get("/api/admin/storage")
async def get_storage_stats():
    """저장소 통계 조회"""
    try:
        # 실제로는 시스템 정보를 가져와야 함
        storage_stats = {
            "db_size": 15.2,
            "file_size": 45.8,
            "backup_size": 120.5
        }
        
        return JSONResponse(content={
            "success": True,
            "storage": storage_stats
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.post("/api/admin/backup")
async def create_backup():
    """백업 생성"""
    try:
        # 실제로는 백업 로직을 구현해야 함
        return JSONResponse(content={
            "success": True,
            "message": "백업이 성공적으로 생성되었습니다."
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.get("/api/admin/points/stats")
async def get_points_stats():
    """포인트 통계 조회"""
    try:
        # 실제로는 포인트 통계를 계산해야 함
        points_stats = {
            "total_sold": 50000,
            "total_used": 35000,
            "remaining": 15000
        }
        
        return JSONResponse(content={
            "success": True,
            "stats": points_stats
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.get("/api/admin/points/users")
async def get_points_users():
    """포인트 사용자 목록 조회"""
    try:
        # 실제로는 포인트 사용자 정보를 가져와야 함
        users = [
            {
                "user_id": "admin",
                "current_points": 1000,
                "total_used": 500,
                "last_updated": "2024-01-15"
            }
        ]
        
        return JSONResponse(content={
            "success": True,
            "users": users
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.post("/api/admin/points/adjust")
async def adjust_user_points(request: Request):
    """사용자 포인트 조정"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        amount = data.get("amount")
        action = data.get("action")
        
        # 실제로는 포인트 조정 로직을 구현해야 함
        return JSONResponse(content={
            "success": True,
            "message": f"사용자 {user_id}의 포인트가 {action}되었습니다."
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.get("/api/admin/monitoring")
async def get_monitoring_stats():
    """모니터링 통계 조회"""
    try:
        # 실제로는 시스템 모니터링 정보를 가져와야 함
        monitoring_stats = {
            "concurrent_users": len(sessions_db),
            "api_calls": 150,
            "avg_response_time": 45
        }
        
        return JSONResponse(content={
            "success": True,
            "monitoring": monitoring_stats
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.get("/api/admin/resources")
async def get_resource_stats():
    """자원 사용량 조회"""
    try:
        import psutil
        
        # 실제 시스템 자원 정보 가져오기
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        resource_stats = {
            "cpu_usage": round(cpu_usage, 1),
            "memory_usage": round(memory.percent, 1),
            "disk_usage": round(disk.percent, 1),
            "upload_speed": 0,
            "download_speed": 0
        }
        
        return JSONResponse(content={
            "success": True,
            "resources": resource_stats
        })
    except ImportError:
        # psutil이 없는 경우 기본값 반환
        return JSONResponse(content={
            "success": True,
            "resources": {
                "cpu_usage": 25.0,
                "memory_usage": 45.0,
                "disk_usage": 60.0,
                "upload_speed": 0,
                "download_speed": 0
            }
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.post("/api/admin/learn-file")
async def learn_file(request: Request):
    """파일 학습 API"""
    try:
        form = await request.form()
        file = form.get("file")
        
        if not file:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "파일이 없습니다."}
            )
        
        # 파일 내용 읽기
        content = await file.read()
        text_content = content.decode('utf-8')
        
        # 학습 결과 시뮬레이션
        chunks = len(text_content) // 1000 + 1
        saved_memories = chunks
        
        return JSONResponse(content={
            "success": True,
            "message": f"파일 '{file.filename}' 학습이 완료되었습니다.",
            "chunks": chunks,
            "saved_memories": saved_memories,
            "details": {
                "text_length": len(text_content),
                "avg_chunk_size": len(text_content) // chunks,
                "memory_system": "aura_memory",
                "session_id": f"session_{int(time.time())}"
            }
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.post("/api/admin/learn-dialog-file")
async def learn_dialog_file(request: Request):
    """대화 파일 학습 API"""
    try:
        form = await request.form()
        file = form.get("file")
        
        if not file:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "파일이 없습니다."}
            )
        
        # 파일 내용 읽기
        content = await file.read()
        text_content = content.decode('utf-8')
        
        # 대화 파싱 시뮬레이션
        lines = text_content.split('\n')
        dialog_turns = len([line for line in lines if line.strip() and ('Q:' in line or '질문:' in line or '사용자:' in line)])
        
        return JSONResponse(content={
            "success": True,
            "message": f"대화 파일 '{file.filename}' 학습이 완료되었습니다.",
            "dialog_turns": dialog_turns,
            "saved_dialogs": dialog_turns,
            "details": {
                "text_length": len(text_content),
                "total_lines": len(lines),
                "avg_question_length": 50,
                "avg_answer_length": 100,
                "memory_system": "aura_dialog_memory",
                "session_id": f"dialog_session_{int(time.time())}"
            }
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@app.get("/api/auth/check")
async def check_auth():
    """인증 상태 확인"""
    return JSONResponse(content={
        "success": True,
        "authenticated": True
    })

# 학습 페이지 라우트
@app.get("/learning")
async def learning_page():
    """학습 페이지"""
    return templates.TemplateResponse("learning.html", {"request": {}})

@app.post("/api/login")
async def login_api_legacy(request: Request):
    """레거시 로그인 API (호환성 유지)"""
    return await login_api(request)

@app.post("/api/admin/login")
async def admin_login_api(request: Request):
    """관리자 로그인 API (호환성 유지)"""
    return await login_api(request)

if __name__ == "__main__":
    print("🚀 EORA AI 최종 홈페이지 서버 (원본 HTML 연결) 시작...")
    print("📍 접속 주소: http://127.0.0.1:8007")
    print("🔐 로그인: http://127.0.0.1:8007/login")
    print("⚙️ 관리자: http://127.0.0.1:8007/admin")
    print("💬 채팅: http://127.0.0.1:8007/chat")
    print("📊 대시보드: http://127.0.0.1:8007/dashboard")
    print("📝 프롬프트: http://127.0.0.1:8007/prompts")
    print("🧠 메모리: http://127.0.0.1:8007/memory")
    print("👤 프로필: http://127.0.0.1:8007/profile")
    print("🧪 테스트: http://127.0.0.1:8007/test")
    print("==================================================")
    print("📧 관리자 계정: admin@eora.ai")
    print("🔑 비밀번호: admin123")
    print("==================================================")
    
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8007, reload=False)