#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 디버그 서버
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="EORA AI Debug Server")

@app.get("/")
async def root(request: Request):
    """기본 라우트 핸들러"""
    return {"message": "EORA AI 디버그 서버가 정상 작동 중입니다.", "status": "ok"}

@app.get("/health")
async def health():
    """헬스 체크"""
    return {"status": "healthy", "message": "서버가 정상 작동 중입니다."}

if __name__ == "__main__":
    print("🚀 EORA AI 디버그 서버 시작...")
    print("📍 접속 주소: http://127.0.0.1:8011")
    print("=" * 50)
    
    try:
        uvicorn.run(app, host="127.0.0.1", port=8011, log_level="info")
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        import traceback
        traceback.print_exc() 