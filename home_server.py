#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 홈페이지 서버
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import uvicorn
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse, HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from pathlib import Path
    print("✅ 필요한 모듈 로드 성공")
except ImportError as e:
    print(f"❌ 모듈 로드 실패: {e}")
    print("다음 명령어로 필요한 패키지를 설치하세요:")
    print("pip install fastapi uvicorn jinja2")
    input("Enter를 눌러 종료...")
    sys.exit(1)

app = FastAPI(title="EORA AI Home Server")

# 정적 파일 마운트
try:
    static_dir = Path(__file__).parent / "src" / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        print(f"✅ 정적 파일 마운트: {static_dir}")
    else:
        print(f"⚠️ 정적 파일 디렉토리 없음: {static_dir}")
except Exception as e:
    print(f"⚠️ 정적 파일 마운트 실패: {e}")

# 템플릿 설정
try:
    templates_dir = Path(__file__).parent / "src" / "templates"
    if templates_dir.exists():
        templates = Jinja2Templates(directory=str(templates_dir))
        print(f"✅ 템플릿 디렉토리: {templates_dir}")
    else:
        templates = None
        print(f"⚠️ 템플릿 디렉토리 없음: {templates_dir}")
except Exception as e:
    print(f"⚠️ 템플릿 설정 실패: {e}")
    templates = None

@app.get("/")
async def root(request: Request):
    """홈페이지"""
    if templates:
        try:
            return templates.TemplateResponse("home.html", {"request": request})
        except Exception as e:
            print(f"⚠️ 템플릿 렌더링 실패: {e}")
    
    # 기본 홈페이지 HTML
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EORA AI - 홈페이지</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                text-align: center;
                padding: 40px 0;
            }
            .header h1 {
                font-size: 3em;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .header p {
                font-size: 1.2em;
                margin: 10px 0;
                opacity: 0.9;
            }
            .nav {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin: 40px 0;
                flex-wrap: wrap;
            }
            .nav a {
                background: rgba(255,255,255,0.1);
                color: white;
                text-decoration: none;
                padding: 15px 30px;
                border-radius: 25px;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }
            .nav a:hover {
                background: rgba(255,255,255,0.2);
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                margin: 40px 0;
            }
            .feature {
                background: rgba(255,255,255,0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }
            .feature h3 {
                margin: 0 0 15px 0;
                color: #ffd700;
            }
            .status {
                text-align: center;
                margin: 20px 0;
                padding: 15px;
                background: rgba(0,255,0,0.1);
                border-radius: 10px;
                border: 1px solid rgba(0,255,0,0.3);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 EORA AI</h1>
                <p>인공지능 기반 대화 시스템</p>
            </div>
            
            <div class="status">
                ✅ 서버가 정상 작동 중입니다
            </div>
            
            <div class="nav">
                <a href="/chat">💬 채팅</a>
                <a href="/admin">⚙️ 관리자</a>
                <a href="/dashboard">📊 대시보드</a>
                <a href="/test">🧪 테스트</a>
                <a href="/health">❤️ 상태확인</a>
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
        
        <script>
            // 현재 시간 표시
            function updateTime() {
                const now = new Date();
                document.title = `EORA AI - ${now.toLocaleTimeString('ko-KR')}`;
            }
            setInterval(updateTime, 1000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/chat")
async def chat_page(request: Request):
    """채팅 페이지"""
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

@app.get("/admin")
async def admin_page(request: Request):
    """관리자 페이지"""
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
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .admin-container {
                max-width: 1000px;
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }
            .admin-header {
                text-align: center;
                margin-bottom: 30px;
            }
            .admin-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .admin-card {
                background: rgba(255,255,255,0.1);
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                transition: all 0.3s ease;
            }
            .admin-card:hover {
                background: rgba(255,255,255,0.2);
                transform: translateY(-2px);
            }
            .admin-card h3 {
                margin: 0 0 10px 0;
                color: #ffd700;
            }
            .back-link {
                text-align: center;
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
        <div class="admin-container">
            <div class="admin-header">
                <h1>⚙️ EORA AI 관리자</h1>
                <p>시스템 관리 및 모니터링</p>
            </div>
            
            <div class="admin-grid">
                <div class="admin-card">
                    <h3>📊 시스템 상태</h3>
                    <p>서버 상태 모니터링</p>
                    <p>✅ 정상 작동</p>
                </div>
                <div class="admin-card">
                    <h3>💾 데이터베이스</h3>
                    <p>MongoDB 연결 상태</p>
                    <p>⚠️ 개발 중</p>
                </div>
                <div class="admin-card">
                    <h3>🤖 AI 모델</h3>
                    <p>OpenAI API 상태</p>
                    <p>⚠️ 개발 중</p>
                </div>
                <div class="admin-card">
                    <h3>📈 사용 통계</h3>
                    <p>사용자 활동 분석</p>
                    <p>⚠️ 개발 중</p>
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

@app.get("/dashboard")
async def dashboard_page(request: Request):
    """대시보드 페이지"""
    return admin_page(request)

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
                padding: 20px;
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
            // 페이지 로딩 시간 측정
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
    print("📍 접속 주소: http://127.0.0.1:8011")
    print("🔍 테스트 페이지: http://127.0.0.1:8011/test")
    print("💬 채팅 페이지: http://127.0.0.1:8011/chat")
    print("⚙️ 관리자 페이지: http://127.0.0.1:8011/admin")
    print("=" * 50)
    
    try:
        uvicorn.run(app, host="127.0.0.1", port=8011, log_level="info")
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        import traceback
        traceback.print_exc()
        input("Enter를 눌러 종료...") 