#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 초간단 서버
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import uvicorn
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse, HTMLResponse
    print("✅ 필요한 모듈 로드 성공")
except ImportError as e:
    print(f"❌ 모듈 로드 실패: {e}")
    print("다음 명령어로 필요한 패키지를 설치하세요:")
    print("pip install fastapi uvicorn")
    input("Enter를 눌러 종료...")
    sys.exit(1)

app = FastAPI(title="EORA AI Simple Server")

@app.get("/")
async def root(request: Request):
    """기본 라우트 핸들러"""
    return {"message": "EORA AI 서버가 정상 작동 중입니다.", "status": "ok"}

@app.get("/health")
async def health():
    """헬스 체크"""
    return {"status": "healthy", "message": "서버가 정상 작동 중입니다."}

@app.get("/test")
async def test():
    """테스트 페이지"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EORA AI 서버 테스트</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .success { color: green; }
            .info { color: blue; }
        </style>
    </head>
    <body>
        <h1>🚀 EORA AI 서버</h1>
        <p class="success">✅ 서버가 정상 작동 중입니다!</p>
        <p class="info">📍 접속 주소: http://127.0.0.1:8011</p>
        <p>현재 시간: <span id="time"></span></p>
        <script>
            document.getElementById('time').textContent = new Date().toLocaleString('ko-KR');
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    print("🚀 EORA AI 서버 시작...")
    print("📍 접속 주소: http://127.0.0.1:8011")
    print("🔍 테스트 페이지: http://127.0.0.1:8011/test")
    print("=" * 50)
    
    try:
        uvicorn.run(app, host="127.0.0.1", port=8011, log_level="info")
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        import traceback
        traceback.print_exc()
        input("Enter를 눌러 종료...") 