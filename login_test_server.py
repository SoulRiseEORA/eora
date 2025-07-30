#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 로그인 테스트 서버
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
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.sessions import SessionMiddleware
    import jwt
    print("✅ FastAPI 모듈 로드 성공")
except ImportError as e:
    print(f"❌ FastAPI 모듈 로드 실패: {e}")
    print("다음 명령어로 필요한 패키지를 설치하세요:")
    print("pip install fastapi uvicorn python-multipart PyJWT")
    input("Enter를 눌러 종료...")
    sys.exit(1)

app = FastAPI(title="EORA AI Login Test Server")

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

# 세션 미들웨어
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="eora_session",
    max_age=60 * 60 * 24 * 30,  # 30일
    same_site="lax",
    https_only=False
)

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

def get_current_user(request: Request):
    """현재 사용자 정보 가져오기"""
    user = None
    
    # 세션에서 사용자 정보 확인
    if hasattr(request, "session"):
        try:
            user = request.session.get("user")
            print(f"세션에서 사용자: {user}")
        except Exception as e:
            print(f"세션 읽기 오류: {e}")
    
    # 쿠키에서 사용자 정보 확인
    if not user:
        try:
            user_cookie = request.cookies.get("user")
            if user_cookie:
                user = json.loads(user_cookie)
                print(f"쿠키에서 사용자: {user}")
        except Exception as e:
            print(f"쿠키 읽기 오류: {e}")
    
    return user

@app.get("/")
async def root(request: Request):
    """홈페이지"""
    user = get_current_user(request)
    is_admin = user.get("is_admin", False) if user else False
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EORA AI - 로그인 테스트</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 30px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
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
                margin: 30px 0;
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
            .debug-info {{
                margin: 20px 0;
                padding: 15px;
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
            }}
            .debug-info h3 {{
                margin: 0 0 10px 0;
                color: #ffd700;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 EORA AI</h1>
                <p>로그인 테스트 서버</p>
            </div>
            
            <div class="user-info">
                {'✅ 관리자로 로그인됨' if is_admin else '👤 게스트 모드'}
                {' - ' + user.get("email", "") if user else ""}
            </div>
            
            <div class="nav">
                <a href="/login">🔐 로그인</a>
                <a href="/admin">⚙️ 관리자</a>
                <a href="/test-login">🧪 로그인 테스트</a>
                <a href="/logout">🚪 로그아웃</a>
            </div>
            
            <div class="debug-info">
                <h3>📋 디버그 정보</h3>
                <p>• 현재 사용자: {user.get("email", "없음") if user else "없음"}</p>
                <p>• 관리자 권한: {'예' if is_admin else '아니오'}</p>
                <p>• 세션 상태: {'활성' if user else '비활성'}</p>
                <p>• 서버 시간: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/login")
async def login_page(request: Request):
    """로그인 페이지"""
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
            .result {
                margin-top: 20px;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                font-weight: bold;
            }
            .success {
                background: rgba(0, 255, 0, 0.1);
                color: #28a745;
            }
            .error {
                background: rgba(255, 0, 0, 0.1);
                color: #dc3545;
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
                <strong>📋 테스트 계정:</strong><br>
                <strong>관리자:</strong> admin@eora.ai / admin123<br>
                <strong>일반 사용자:</strong> test@eora.ai / test123
            </div>
            
            <div id="result" class="result" style="display: none;"></div>
        </div>
        
        <script>
            document.getElementById('loginForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                const resultDiv = document.getElementById('result');
                
                try {
                    console.log('로그인 시도:', email);
                    
                    const response = await fetch('/api/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ email, password })
                    });
                    
                    const data = await response.json();
                    console.log('서버 응답:', data);
                    
                    if (data.success) {
                        resultDiv.className = 'result success';
                        resultDiv.textContent = '✅ 로그인 성공! 관리자 페이지로 이동합니다...';
                        resultDiv.style.display = 'block';
                        
                        setTimeout(() => {
                            window.location.href = '/admin';
                        }, 2000);
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.textContent = '❌ 로그인 실패: ' + data.message;
                        resultDiv.style.display = 'block';
                    }
                } catch (error) {
                    console.error('로그인 오류:', error);
                    resultDiv.className = 'result error';
                    resultDiv.textContent = '❌ 로그인 중 오류가 발생했습니다.';
                    resultDiv.style.display = 'block';
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
        
        print(f"로그인 시도: {email}")
        
        if not email or not password:
            print("이메일 또는 비밀번호 누락")
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "이메일과 비밀번호를 입력하세요."}
            )
        
        # 사용자 확인
        user = users_db.get(email)
        if not user:
            print(f"존재하지 않는 계정: {email}")
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "존재하지 않는 계정입니다."}
            )
        
        # 비밀번호 확인
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        print(f"입력된 비밀번호 해시: {password_hash}")
        print(f"저장된 비밀번호 해시: {user['password_hash']}")
        
        if user["password_hash"] != password_hash:
            print("비밀번호 불일치")
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "비밀번호가 올바르지 않습니다."}
            )
        
        print(f"로그인 성공: {email}")
        
        # 세션에 사용자 정보 저장
        if hasattr(request, "session"):
            request.session["user"] = user
            print(f"세션에 사용자 저장: {user['email']}")
        
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
        
        print(f"쿠키 설정 완료: {user['email']}")
        return response
        
    except Exception as e:
        print(f"로그인 API 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"로그인 중 오류가 발생했습니다: {str(e)}"}
        )

@app.get("/logout")
async def logout(request: Request):
    """로그아웃"""
    print("로그아웃 요청")
    
    # 세션에서 사용자 정보 제거
    if hasattr(request, "session"):
        request.session.clear()
        print("세션 클리어 완료")
    
    # 쿠키에서 사용자 정보 제거
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("user")
    print("쿠키 삭제 완료")
    
    return response

@app.get("/admin")
async def admin_page(request: Request):
    """관리자 페이지"""
    user = get_current_user(request)
    is_admin = user.get("is_admin", False) if user else False
    
    if not is_admin:
        return RedirectResponse(url="/login", status_code=302)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EORA AI - 관리자</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                text-align: center;
            }}
            .title {{
                font-size: 2.5em;
                color: #333;
                margin-bottom: 10px;
            }}
            .admin-panel {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                margin-bottom: 30px;
            }}
            .admin-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                margin-bottom: 40px;
            }}
            .admin-card {{
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-radius: 15px;
                padding: 30px;
                text-align: center;
                transition: all 0.3s ease;
                border: 2px solid transparent;
                cursor: pointer;
            }}
            .admin-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
                border-color: #667eea;
            }}
            .card-icon {{
                font-size: 3em;
                margin-bottom: 20px;
                color: #667eea;
            }}
            .card-title {{
                font-size: 1.5em;
                font-weight: 600;
                margin-bottom: 15px;
                color: #333;
            }}
            .card-description {{
                color: #666;
                margin-bottom: 25px;
                line-height: 1.6;
            }}
            .btn {{
                padding: 12px 24px;
                border: none;
                border-radius: 25px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s ease;
                display: inline-block;
            }}
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }}
            .back-link {{
                text-align: center;
                margin-top: 30px;
            }}
            .back-link a {{
                color: white;
                text-decoration: none;
                padding: 15px 30px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 25px;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .back-link a:hover {{
                background: rgba(255, 255, 255, 0.2);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 class="title">⚙️ EORA AI 관리자</h1>
                <p class="subtitle">시스템 관리 및 모니터링</p>
                <p>로그인된 사용자: {user.get("email", "")}</p>
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

@app.get("/test-login")
async def test_login_page(request: Request):
    """로그인 테스트 페이지"""
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EORA AI - 로그인 테스트</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 30px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
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
            .test-button {
                background: rgba(255,255,255,0.2);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 10px;
                cursor: pointer;
                margin: 5px;
                transition: all 0.3s ease;
            }
            .test-button:hover {
                background: rgba(255,255,255,0.3);
            }
            .result {
                margin-top: 10px;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            .success {
                background: rgba(0,255,0,0.2);
                color: #90EE90;
            }
            .error {
                background: rgba(255,0,0,0.2);
                color: #FFB6C1;
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
                border-radius: 20px;
                transition: all 0.3s ease;
            }
            .back-link a:hover {
                background: rgba(255,255,255,0.2);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧪 로그인 테스트</h1>
            
            <div class="test-section">
                <h3>📋 테스트 계정</h3>
                <p>• 관리자: admin@eora.ai / admin123</p>
                <p>• 일반 사용자: test@eora.ai / test123</p>
            </div>
            
            <div class="test-section">
                <h3>🔐 로그인 테스트</h3>
                <button class="test-button" onclick="testLogin('admin@eora.ai', 'admin123')">관리자 로그인 테스트</button>
                <button class="test-button" onclick="testLogin('test@eora.ai', 'test123')">일반 사용자 로그인 테스트</button>
                <button class="test-button" onclick="testLogin('wrong@eora.ai', 'wrong123')">잘못된 계정 테스트</button>
                <div id="loginResult" class="result" style="display: none;"></div>
            </div>
            
            <div class="test-section">
                <h3>📊 현재 상태</h3>
                <div id="currentStatus">로딩 중...</div>
            </div>
            
            <div class="back-link">
                <a href="/">🏠 홈으로 돌아가기</a>
            </div>
        </div>
        
        <script>
            async function testLogin(email, password) {
                const resultDiv = document.getElementById('loginResult');
                
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
                        resultDiv.className = 'result success';
                        resultDiv.textContent = `✅ 로그인 성공: ${email}`;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.textContent = `❌ 로그인 실패: ${data.message}`;
                    }
                    
                    resultDiv.style.display = 'block';
                    updateStatus();
                    
                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.textContent = '❌ 테스트 중 오류 발생';
                    resultDiv.style.display = 'block';
                }
            }
            
            async function updateStatus() {
                const statusDiv = document.getElementById('currentStatus');
                try {
                    const response = await fetch('/');
                    const html = await response.text();
                    statusDiv.innerHTML = '✅ 서버 연결 정상<br>✅ 로그인 API 정상';
                } catch (error) {
                    statusDiv.innerHTML = '❌ 서버 연결 실패';
                }
            }
            
            updateStatus();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health():
    """헬스 체크"""
    return {"status": "healthy", "message": "로그인 테스트 서버가 정상 작동 중입니다."}

if __name__ == "__main__":
    print("🚀 EORA AI 로그인 테스트 서버 시작...")
    print("📍 접속 주소: http://127.0.0.1:8011")
    print("🔐 로그인: http://127.0.0.1:8011/login")
    print("🧪 테스트: http://127.0.0.1:8011/test-login")
    print("=" * 50)
    print("📧 관리자 계정: admin@eora.ai")
    print("🔑 비밀번호: admin123")
    print("📧 테스트 계정: test@eora.ai")
    print("🔑 비밀번호: test123")
    print("=" * 50)
    
    try:
        uvicorn.run(app, host="127.0.0.1", port=8011, log_level="info")
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        import traceback
        traceback.print_exc()
        input("Enter를 눌러 종료...") 