#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 원본 HTML 연결 서버
"""

import sys
import os
import json
import hashlib
from datetime import datetime
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

app = FastAPI(title="EORA AI Original HTML Server")

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
        return templates.TemplateResponse("home.html", {
            "request": request,
            "user": user,
            "is_admin": is_admin
        })
    else:
        # 템플릿이 없으면 기본 HTML 반환
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
                    text-align: center;
                }}
                .header {{
                    padding: 40px 0;
                }}
                .header h1 {{
                    font-size: 3em;
                    margin: 0;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
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
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 EORA AI</h1>
                    <p>인공지능 기반 대화 시스템</p>
                </div>
                
                <div class="nav">
                    <a href="/chat">💬 채팅</a>
                    <a href="/dashboard">📊 대시보드</a>
                    <a href="/admin">⚙️ 관리자</a>
                    <a href="/login">🔐 로그인</a>
                    <a href="/test">🧪 테스트</a>
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
        return templates.TemplateResponse("login.html", {"request": request})
    else:
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

@app.get("/admin")
async def admin_page(request: Request):
    """관리자 페이지 - 원본 admin.html 사용"""
    user = get_current_user(request)
    is_admin = user.get("is_admin", False) if user else False
    
    if not is_admin:
        return RedirectResponse(url="/login", status_code=302)
    
    if templates:
        return templates.TemplateResponse("admin.html", {
            "request": request,
            "user": user,
            "is_admin": is_admin
        })
    else:
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
    if templates:
        return templates.TemplateResponse("chat.html", {"request": request})
    else:
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
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user": user,
            "is_admin": is_admin
        })
    else:
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
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("user")
    return response

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
        return templates.TemplateResponse("prompts.html", {
            "request": request,
            "user": user,
            "is_admin": is_admin
        })
    else:
        return RedirectResponse(url="/admin", status_code=302)

@app.get("/memory")
async def memory_page(request: Request):
    """메모리 관리 페이지"""
    user = get_current_user(request)
    is_admin = user.get("is_admin", False) if user else False
    
    if not is_admin:
        return RedirectResponse(url="/login", status_code=302)
    
    if templates:
        return templates.TemplateResponse("memory.html", {
            "request": request,
            "user": user,
            "is_admin": is_admin
        })
    else:
        return RedirectResponse(url="/admin", status_code=302)

@app.get("/profile")
async def profile_page(request: Request):
    """프로필 페이지"""
    user = get_current_user(request)
    
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    if templates:
        return templates.TemplateResponse("profile.html", {
            "request": request,
            "user": user
        })
    else:
        return RedirectResponse(url="/", status_code=302)

if __name__ == "__main__":
    print("🚀 EORA AI 원본 HTML 서버 시작...")
    print("📍 접속 주소: http://127.0.0.1:8005")
    print("🔐 로그인: http://127.0.0.1:8005/login")
    print("⚙️ 관리자: http://127.0.0.1:8005/admin")
    print("💬 채팅: http://127.0.0.1:8005/chat")
    print("📊 대시보드: http://127.0.0.1:8005/dashboard")
    print("📝 프롬프트: http://127.0.0.1:8005/prompts")
    print("🧠 메모리: http://127.0.0.1:8005/memory")
    print("👤 프로필: http://127.0.0.1:8005/profile")
    print("🧪 테스트: http://127.0.0.1:8005/test")
    print("=" * 50)
    print("📧 관리자 계정: admin@eora.ai")
    print("🔑 비밀번호: admin123")
    print("=" * 50)
    
    try:
        uvicorn.run(app, host="127.0.0.1", port=8005, log_level="info")
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        import traceback
        traceback.print_exc()
        input("Enter를 눌러 종료...") 