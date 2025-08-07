#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 포트 8001 서버
"""

import sys
import os
import json
from datetime import datetime

# FastAPI 및 관련 모듈 임포트
try:
    import uvicorn
    from fastapi import FastAPI, Request, Response, HTTPException
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    print("✅ FastAPI 모듈 로드 성공")
except ImportError as e:
    print(f"❌ FastAPI 모듈 로드 실패: {e}")
    print("다음 명령어로 필요한 패키지를 설치하세요:")
    print("pip install fastapi uvicorn")
    input("Enter를 눌러 종료...")
    sys.exit(1)

app = FastAPI(title="EORA AI Port 8001 Server")

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """홈페이지"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EORA AI - 포트 8001</title>
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
                max-width: 1000px;
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
            .status {{
                text-align: center;
                margin: 20px 0;
                padding: 15px;
                background: rgba(0,255,0,0.2);
                border-radius: 10px;
                color: #90EE90;
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
            .info {{
                margin: 20px 0;
                padding: 15px;
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
            }}
            .info h3 {{
                margin: 0 0 10px 0;
                color: #ffd700;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 EORA AI</h1>
                <p>포트 8001 서버</p>
            </div>
            
            <div class="status">
                ✅ 서버가 정상적으로 실행 중입니다!
            </div>
            
            <div class="nav">
                <a href="/api/status">📊 API 상태</a>
                <a href="/test">🧪 테스트</a>
                <a href="/health">❤️ 헬스 체크</a>
                <a href="/info">ℹ️ 서버 정보</a>
            </div>
            
            <div class="info">
                <h3>📋 서버 정보</h3>
                <p>• 포트: 8001</p>
                <p>• 주소: http://127.0.0.1:8001</p>
                <p>• 시작 시간: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                <p>• 상태: 정상 작동</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/status")
async def api_status():
    """API 상태 확인"""
    return {
        "status": "success",
        "message": "포트 8001 서버가 정상 작동 중입니다",
        "timestamp": datetime.now().isoformat(),
        "port": 8001,
        "server": "EORA AI"
    }

@app.get("/test")
async def test_page():
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
            <h1>🧪 EORA AI 테스트</h1>
            
            <div class="test-section">
                <h3>📊 API 테스트</h3>
                <button class="test-button" onclick="testAPI()">API 상태 확인</button>
                <button class="test-button" onclick="testHealth()">헬스 체크</button>
                <div id="apiResult" class="result" style="display: none;"></div>
            </div>
            
            <div class="test-section">
                <h3>🔗 연결 테스트</h3>
                <button class="test-button" onclick="testConnection()">서버 연결 확인</button>
                <div id="connectionResult" class="result" style="display: none;"></div>
            </div>
            
            <div class="back-link">
                <a href="/">🏠 홈으로 돌아가기</a>
            </div>
        </div>
        
        <script>
            async function testAPI() {
                const resultDiv = document.getElementById('apiResult');
                
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    
                    resultDiv.className = 'result success';
                    resultDiv.textContent = `✅ API 정상: ${data.message}`;
                    resultDiv.style.display = 'block';
                    
                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.textContent = '❌ API 오류: ' + error.message;
                    resultDiv.style.display = 'block';
                }
            }
            
            async function testHealth() {
                const resultDiv = document.getElementById('apiResult');
                
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    
                    resultDiv.className = 'result success';
                    resultDiv.textContent = `✅ 헬스 체크 정상: ${data.message}`;
                    resultDiv.style.display = 'block';
                    
                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.textContent = '❌ 헬스 체크 오류: ' + error.message;
                    resultDiv.style.display = 'block';
                }
            }
            
            async function testConnection() {
                const resultDiv = document.getElementById('connectionResult');
                
                try {
                    const response = await fetch('/');
                    const html = await response.text();
                    
                    resultDiv.className = 'result success';
                    resultDiv.textContent = '✅ 서버 연결 정상';
                    resultDiv.style.display = 'block';
                    
                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.textContent = '❌ 서버 연결 실패: ' + error.message;
                    resultDiv.style.display = 'block';
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health():
    """헬스 체크"""
    return {
        "status": "healthy",
        "message": "포트 8001 서버가 정상 작동 중입니다",
        "timestamp": datetime.now().isoformat(),
        "port": 8001
    }

@app.get("/info")
async def server_info():
    """서버 정보"""
    return {
        "server_name": "EORA AI",
        "port": 8001,
        "host": "127.0.0.1",
        "start_time": datetime.now().isoformat(),
        "status": "running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    print("🚀 EORA AI 포트 8001 서버 시작...")
    print("📍 접속 주소: http://127.0.0.1:8001")
    print("📊 API 상태: http://127.0.0.1:8001/api/status")
    print("🧪 테스트: http://127.0.0.1:8001/test")
    print("❤️ 헬스 체크: http://127.0.0.1:8001/health")
    print("=" * 50)
    
    try:
        uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        import traceback
        traceback.print_exc()
        input("Enter를 눌러 종료...") 