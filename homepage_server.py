#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 홈페이지 서버
"""

import sys
import os
import json
import hashlib
from datetime import datetime

# FastAPI 및 관련 모듈 임포트
try:
    import uvicorn
    from fastapi import FastAPI, Request, Response, HTTPException, Depends, Form, Cookie
    from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from fastapi.middleware.cors import CORSMiddleware
    import jwt
    print("✅ FastAPI 모듈 로드 성공")
except ImportError as e:
    print(f"❌ FastAPI 모듈 로드 실패: {e}")
    print("다음 명령어로 필요한 패키지를 설치하세요:")
    print("pip install fastapi uvicorn jinja2 python-multipart PyJWT")
    input("Enter를 눌러 종료...")
    sys.exit(1)

app = FastAPI(title="EORA AI Homepage Server")

# 환경 설정
SECRET_KEY = "eora_super_secret_key_2024_07_11_!@#"
ALGORITHM = "HS256"
DATABASE_NAME = "eora_ai"

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 세션 미들웨어 (선택적)
try:
    from fastapi.middleware.sessions import SessionMiddleware
    app.add_middleware(
        SessionMiddleware,
        secret_key=SECRET_KEY,
        session_cookie="eora_session",
        max_age=60 * 60 * 24 * 30,  # 30일
        same_site="lax",
        https_only=False
    )
    print("✅ 세션 미들웨어 활성화")
except ImportError:
    print("⚠️ 세션 미들웨어 사용 불가 - 쿠키 기반 인증 사용")

# 정적 파일 마운트
try:
    static_dir = os.path.join(os.path.dirname(__file__), "src", "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        print(f"✅ 정적 파일 마운트: {static_dir}")
    else:
        print(f"⚠️ 정적 파일 디렉토리 없음: {static_dir}")
except Exception as e:
    print(f"⚠️ 정적 파일 마운트 실패: {e}")

# 템플릿 설정
try:
    templates_dir = os.path.join(os.path.dirname(__file__), "src", "templates")
    if os.path.exists(templates_dir):
        templates = Jinja2Templates(directory=templates_dir)
        print(f"✅ 템플릿 디렉토리: {templates_dir}")
    else:
        templates = None
        print(f"⚠️ 템플릿 디렉토리 없음: {templates_dir}")
except Exception as e:
    print(f"⚠️ 템플릿 설정 실패: {e}")
    templates = None

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

def create_access_token(data: dict, expires_delta=None):
    """JWT 토큰 생성"""
    from datetime import timedelta
    if expires_delta is None:
        expires_delta = timedelta(hours=24)
    
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """JWT 토큰 검증"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None

def get_current_user(request: Request):
    """현재 사용자 정보 가져오기"""
    user = None
    
    # 세션에서 사용자 정보 확인
    if hasattr(request, "session"):
        try:
            user = request.session.get("user")
        except:
            pass
    
    # 쿠키에서 사용자 정보 확인
    if not user:
        try:
            user_cookie = request.cookies.get("user")
            if user_cookie:
                user = json.loads(user_cookie)
        except:
            pass
    
    # Authorization 헤더에서 토큰 확인
    if not user:
        try:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                payload = verify_token(token)
                if payload:
                    user = users_db.get(payload.get("email"))
        except:
            pass
    
    return user

def admin_required(func):
    """관리자 권한 데코레이터"""
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request')
        if request is None:
            for arg in args:
                if hasattr(arg, 'headers'):
                    request = arg
                    break
        
        user = get_current_user(request)
        if not user or not user.get('is_admin', False):
            return RedirectResponse(url="/login", status_code=302)
        
        return await func(*args, **kwargs)
    return wrapper

@app.get("/")
async def root(request: Request):
    """홈페이지"""
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
            print(f"⚠️ 템플릿 렌더링 실패: {e}")
    
    # 기본 홈페이지 HTML
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
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 EORA AI</h1>
                <p>인공지능 기반 대화 시스템</p>
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
    """로그인 페이지"""
    if templates:
        try:
            return templates.TemplateResponse("login.html", {"request": request})
        except Exception as e:
            print(f"⚠️ 로그인 템플릿 렌더링 실패: {e}")
    
    # 기본 로그인 페이지 HTML
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
        
        # 세션에 사용자 정보 저장
        if hasattr(request, "session"):
            try:
                request.session["user"] = user
            except:
                pass
        
        # 쿠키에 사용자 정보 저장
        response = JSONResponse(content={
            "success": True,
            "message": "로그인 성공",
            "user": {
                "email": user["email"],
                "role": user["role"],
                "is_admin": user["is_admin"]
            }
        })
        
        # JWT 토큰 생성
        token = create_access_token(data={"email": user["email"]})
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
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"로그인 중 오류가 발생했습니다: {str(e)}"}
        )

@app.get("/logout")
async def logout(request: Request):
    """로그아웃"""
    # 세션에서 사용자 정보 제거
    if hasattr(request, "session"):
        try:
            request.session.clear()
        except:
            pass
    
    # 쿠키에서 사용자 정보 제거
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("user")
    
    return response

@app.get("/admin")
@admin_required
async def admin_page(request: Request):
    """관리자 페이지"""
    if templates:
        try:
            return templates.TemplateResponse("admin.html", {"request": request})
        except Exception as e:
            print(f"⚠️ 관리자 템플릿 렌더링 실패: {e}")
    
    # 기본 관리자 페이지 HTML
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
                    <div class="admin-card" onclick="location.href='/admin/prompt-management'">
                        <div class="card-icon">📝</div>
                        <h3 class="card-title">프롬프트 관리</h3>
                        <p class="card-description">AI 프롬프트 설정 및 관리</p>
                        <a href="/admin/prompt-management" class="btn">관리하기</a>
                    </div>
                    
                    <div class="admin-card" onclick="location.href='/admin/user-management'">
                        <div class="card-icon">👥</div>
                        <h3 class="card-title">사용자 관리</h3>
                        <p class="card-description">사용자 계정 및 권한 관리</p>
                        <a href="/admin/user-management" class="btn">관리하기</a>
                    </div>
                    
                    <div class="admin-card" onclick="location.href='/admin/system-status'">
                        <div class="card-icon">📊</div>
                        <h3 class="card-title">시스템 상태</h3>
                        <p class="card-description">서버 및 데이터베이스 모니터링</p>
                        <a href="/admin/system-status" class="btn">확인하기</a>
                    </div>
                    
                    <div class="admin-card" onclick="location.href='/admin/logs'">
                        <div class="card-icon">📋</div>
                        <h3 class="card-title">로그 관리</h3>
                        <p class="card-description">시스템 로그 및 오류 확인</p>
                        <a href="/admin/logs" class="btn">확인하기</a>
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
    """채팅 페이지"""
    if templates:
        try:
            return templates.TemplateResponse("chat.html", {"request": request})
        except Exception as e:
            print(f"⚠️ 채팅 템플릿 렌더링 실패: {e}")
    
    # 기본 채팅 페이지 HTML
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
    """대시보드 페이지"""
    user = get_current_user(request)
    is_admin = user.get("is_admin", False) if user else False
    
    if is_admin:
        return admin_page(request)
    else:
        return RedirectResponse(url="/login", status_code=302)

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

if __name__ == "__main__":
    print("🚀 EORA AI 홈페이지 서버 시작...")
    print("📍 접속 주소: http://127.0.0.1:8002")
    print("🔐 로그인: http://127.0.0.1:8002/login")
    print("⚙️ 관리자: http://127.0.0.1:8002/admin")
    print("💬 채팅: http://127.0.0.1:8002/chat")
    print("🧪 테스트: http://127.0.0.1:8002/test")
    print("=" * 50)
    print("📧 관리자 계정: admin@eora.ai")
    print("🔑 비밀번호: admin123")
    print("=" * 50)
    
    try:
        uvicorn.run(app, host="127.0.0.1", port=8002, log_level="info")
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        import traceback
        traceback.print_exc()
        input("Enter를 눌러 종료...") 