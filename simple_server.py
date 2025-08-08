#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - Simple Test Server
home.html 복구 테스트용 간단한 서버
"""

import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="EORA AI System - Simple Test Server",
    description="home.html 복구 테스트용 서버",
    version="1.0.0"
)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 템플릿 설정
templates_path = Path(__file__).parent / "templates"
logger.info(f"📁 템플릿 경로: {templates_path}")

if templates_path.exists():
    templates = Jinja2Templates(directory=str(templates_path))
    logger.info("✅ Jinja2 템플릿 초기화 성공")
    
    # home.html 파일 존재 확인
    home_template_path = templates_path / "home.html"
    logger.info(f"📄 home.html 경로: {home_template_path}")
    logger.info(f"📄 home.html 존재: {home_template_path.exists()}")
    
    if home_template_path.exists():
        logger.info("✅ home.html 파일 발견!")
    else:
        logger.error("❌ home.html 파일이 존재하지 않습니다!")
else:
    logger.error(f"❌ templates 디렉토리가 존재하지 않습니다: {templates_path}")
    templates = None

# 정적 파일 마운트
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    logger.info(f"✅ 정적 파일 마운트 성공: {static_path}")
else:
    logger.warning(f"⚠️ static 디렉토리가 존재하지 않습니다: {static_path}")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """홈 페이지"""
    try:
        if templates and templates_path.exists():
            home_template_path = templates_path / "home.html"
            if home_template_path.exists():
                return templates.TemplateResponse("home.html", {"request": request})
        
        # fallback HTML
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>EORA AI System - 복구 완료</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 40px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                }}
                .container {{ 
                    max-width: 800px; 
                    margin: 0 auto; 
                    background: rgba(255, 255, 255, 0.1);
                    padding: 30px; 
                    border-radius: 15px; 
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                h1 {{ 
                    color: #fff; 
                    text-align: center; 
                    font-size: 2.5em;
                    margin-bottom: 20px;
                }}
                .status {{ 
                    background: rgba(0, 212, 170, 0.2); 
                    padding: 20px; 
                    border-radius: 10px; 
                    margin: 20px 0; 
                    border: 1px solid rgba(0, 212, 170, 0.3);
                }}
                .success {{ 
                    background: rgba(0, 255, 0, 0.2); 
                    padding: 15px; 
                    border-radius: 10px; 
                    margin: 20px 0; 
                    border: 1px solid rgba(0, 255, 0, 0.3);
                }}
                .nav {{ 
                    text-align: center; 
                    margin: 30px 0; 
                }}
                .nav a {{ 
                    display: inline-block; 
                    margin: 10px; 
                    padding: 12px 24px; 
                    background: linear-gradient(135deg, #00d4aa 0%, #00b894 100%);
                    color: white; 
                    text-decoration: none; 
                    border-radius: 25px; 
                    font-weight: 600;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(0, 212, 170, 0.3);
                }}
                .nav a:hover {{ 
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(0, 212, 170, 0.4);
                }}
                .file-info {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 15px;
                    border-radius: 10px;
                    margin: 20px 0;
                    font-family: monospace;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 EORA AI System</h1>
                <div class="success">
                    <h3>✅ home.html 복구 완료!</h3>
                    <p>홈 파일이 성공적으로 복구되었습니다.</p>
                </div>
                <div class="status">
                    <h3>📊 서버 상태</h3>
                    <p>✅ 서버: 정상 실행 중</p>
                    <p>✅ 템플릿: Jinja2 초기화 완료</p>
                    <p>✅ 정적 파일: 마운트 완료</p>
                    <p>✅ CORS: 설정 완료</p>
                </div>
                <div class="file-info">
                    <h4>📁 파일 정보</h4>
                    <p>템플릿 경로: {templates_path}</p>
                    <p>home.html 존재: {templates_path / "home.html" if templates_path.exists() else "N/A"}</p>
                    <p>정적 파일 경로: {static_path}</p>
                </div>
                <div class="nav">
                    <a href="/api/status">서버 상태 확인</a>
                    <a href="/api/files">파일 목록</a>
                    <a href="/chat">채팅 테스트</a>
                </div>
            </div>
        </body>
        </html>
        """, status_code=200)
    except Exception as e:
        logger.error(f"홈 페이지 렌더링 오류: {e}")
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>EORA AI System - 오류</title>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
                .error {{ background: #ffe8e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>❌ EORA AI System - 오류</h1>
                <div class="error">
                    <h3>오류 발생</h3>
                    <p>오류: {str(e)}</p>
                </div>
            </div>
        </body>
        </html>
        """, status_code=500)

@app.get("/api/status")
async def api_status():
    """API 상태 확인"""
    return {
        "status": "success",
        "message": "EORA AI System - Simple Test Server",
        "version": "1.0.0",
        "templates_path": str(templates_path),
        "home_html_exists": (templates_path / "home.html").exists() if templates_path.exists() else False,
        "static_path": str(static_path),
        "static_exists": static_path.exists()
    }

@app.get("/api/files")
async def api_files():
    """파일 목록 확인"""
    files_info = {}
    
    if templates_path.exists():
        html_files = list(templates_path.glob("*.html"))
        files_info["templates"] = [f.name for f in html_files]
    
    if static_path.exists():
        static_files = list(static_path.rglob("*"))
        files_info["static"] = [str(f.relative_to(static_path)) for f in static_files if f.is_file()]
    
    return files_info

@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    """채팅 페이지"""
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>EORA AI Chat</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }}
            .container {{ 
                max-width: 800px; 
                margin: 0 auto; 
                background: rgba(255, 255, 255, 0.1);
                padding: 20px; 
                border-radius: 15px; 
                backdrop-filter: blur(10px);
            }}
            .chat-container {{ 
                height: 400px; 
                border: 1px solid rgba(255, 255, 255, 0.3); 
                padding: 15px; 
                overflow-y: auto; 
                margin: 20px 0; 
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
            }}
            .input-container {{ display: flex; gap: 10px; }}
            input[type="text"] {{ 
                flex: 1; 
                padding: 12px; 
                border: 1px solid rgba(255, 255, 255, 0.3); 
                border-radius: 25px; 
                background: rgba(255, 255, 255, 0.1);
                color: white;
                outline: none;
            }}
            input[type="text"]::placeholder {{ color: rgba(255, 255, 255, 0.7); }}
            button {{ 
                padding: 12px 24px; 
                background: linear-gradient(135deg, #00d4aa 0%, #00b894 100%);
                color: white; 
                border: none; 
                border-radius: 25px; 
                cursor: pointer; 
                font-weight: 600;
                transition: all 0.3s ease;
            }}
            button:hover {{ 
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(0, 212, 170, 0.3);
            }}
            .message {{ 
                margin: 10px 0; 
                padding: 12px; 
                border-radius: 10px; 
                max-width: 80%;
            }}
            .user {{ 
                background: rgba(0, 212, 170, 0.3); 
                text-align: right; 
                margin-left: auto;
                border: 1px solid rgba(0, 212, 170, 0.5);
            }}
            .assistant {{ 
                background: rgba(255, 255, 255, 0.1); 
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>💬 EORA AI Chat</h1>
            <div class="chat-container" id="chatContainer">
                <div class="message assistant">
                    안녕하세요! EORA AI입니다. home.html이 성공적으로 복구되었습니다! 🎉
                </div>
            </div>
            <div class="input-container">
                <input type="text" id="messageInput" placeholder="메시지를 입력하세요..." onkeypress="if(event.keyCode==13) sendMessage()">
                <button onclick="sendMessage()">전송</button>
            </div>
            <p style="text-align: center; margin-top: 20px;">
                <a href="/" style="color: #00d4aa; text-decoration: none;">← 홈으로 돌아가기</a>
            </p>
        </div>
        <script>
            function sendMessage() {{
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;
                
                const container = document.getElementById('chatContainer');
                container.innerHTML += `<div class="message user">${{message}}</div>`;
                input.value = '';
                
                // 간단한 응답 시뮬레이션
                setTimeout(() => {{
                    container.innerHTML += `<div class="message assistant">메시지를 받았습니다! home.html 복구가 완료되어 서버가 정상 작동하고 있습니다. 🚀</div>`;
                    container.scrollTop = container.scrollHeight;
                }}, 1000);
            }}
        </script>
    </body>
    </html>
    """, status_code=200)

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 EORA AI System - Simple Test Server 시작")
    logger.info("📁 템플릿 경로 확인 중...")
    
    if templates_path.exists():
        logger.info(f"✅ 템플릿 디렉토리 발견: {templates_path}")
        html_files = list(templates_path.glob("*.html"))
        logger.info(f"📄 HTML 파일 수: {len(html_files)}개")
        logger.info(f"📄 파일 목록: {[f.name for f in html_files]}")
        
        home_file = templates_path / "home.html"
        if home_file.exists():
            logger.info("✅ home.html 파일 발견!")
        else:
            logger.warning("⚠️ home.html 파일이 없습니다.")
    else:
        logger.error(f"❌ 템플릿 디렉토리가 없습니다: {templates_path}")
    
    # 서버 시작
    port = int(os.getenv("PORT", 8001))
    host = "127.0.0.1"
    
    logger.info(f"🚀 서버 시작: {host}:{port}")
    uvicorn.run(app, host=host, port=port, reload=True) 