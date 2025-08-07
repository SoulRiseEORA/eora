#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 테스트 서버
"""

import os
import sys

# Python 경로 확인
print(f"Python 경로: {sys.executable}")
print(f"현재 디렉토리: {os.getcwd()}")

try:
    import uvicorn
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    print("✅ FastAPI 모듈 로드 성공")
    
    app = FastAPI()
    
    @app.get("/")
    async def root():
        return HTMLResponse("""
        <html>
        <head><title>테스트 서버</title></head>
        <body>
            <h1>✅ 서버가 정상 작동합니다!</h1>
            <p>포트 8008에서 실행 중입니다.</p>
            <a href="/prompt_management">프롬프트 관리자</a>
        </body>
        </html>
        """)
    
    @app.get("/prompt_management")
    async def prompt_management():
        return HTMLResponse("""
        <html>
        <head><title>프롬프트 관리자</title></head>
        <body>
            <h1>📝 프롬프트 관리자</h1>
            <p>프롬프트 관리자 페이지가 정상 작동합니다!</p>
            <a href="/">홈으로 돌아가기</a>
        </body>
        </html>
        """)
    
    if __name__ == "__main__":
        print("🚀 테스트 서버 시작...")
        print("📍 접속 주소: http://127.0.0.1:8008")
        print("📝 프롬프트 관리자: http://127.0.0.1:8008/prompt_management")
        uvicorn.run(app, host="127.0.0.1", port=8008)
        
except ImportError as e:
    print(f"❌ FastAPI 모듈 로드 실패: {e}")
    print("다음 명령어로 필요한 패키지를 설치하세요:")
    print("pip install fastapi uvicorn")
except Exception as e:
    print(f"❌ 오류 발생: {e}") 