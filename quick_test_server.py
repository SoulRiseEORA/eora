#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB 저장 기능 테스트용 간단한 서버
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

# 프로젝트 경로 설정
sys.path.append('src')

app = FastAPI(title="Quick Test Server")
app.add_middleware(SessionMiddleware, secret_key="test-secret-key")

# 사용자 데이터 (간단화)
USERS = {
    "admin@eora.ai": {
        "email": "admin@eora.ai",
        "name": "관리자",
        "is_admin": True,
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest()
    }
}

# MongoDB 연결
try:
    from database import (
        init_mongodb_connection, verify_connection, 
        db_mgr
    )
    
    # MongoDB 초기화
    mongo_init = init_mongodb_connection()
    mongo_ready = verify_connection() if mongo_init else False
    print(f"MongoDB 연결: {'✅ 성공' if mongo_ready else '❌ 실패'}")
except Exception as e:
    print(f"MongoDB 연결 실패: {e}")
    mongo_ready = False
    db_mgr = None

@app.get("/")
async def root():
    return {"message": "Quick Test Server", "mongodb": mongo_ready}

@app.post("/api/login")
async def login(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    
    if email in USERS:
        user = USERS[email]
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash == user["password_hash"]:
            request.session["user_email"] = email
            return JSONResponse({
                "success": True,
                "user": user
            })
    
    return JSONResponse({
        "success": False,
        "error": "로그인 실패"
    })

@app.post("/api/sessions")
async def create_session(request: Request):
    """세션 생성 테스트"""
    user_email = request.session.get("user_email")
    if not user_email:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "로그인이 필요합니다."}
        )
    
    try:
        data = await request.json()
        session_name = data.get("name", f"테스트 세션 {datetime.now().strftime('%H:%M:%S')}")
        
        # 세션 ID 생성
        timestamp = int(datetime.now().timestamp() * 1000)
        session_id = f"session_{user_email.replace('@', '_').replace('.', '_')}_{timestamp}"
        
        # 세션 데이터
        session_data = {
            "id": session_id,
            "session_id": session_id,
            "user_id": user_email,
            "user_email": user_email,
            "name": session_name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "message_count": 0
        }
        
        mongodb_id = None
        if mongo_ready and db_mgr:
            try:
                mongodb_id = await db_mgr.create_session(session_data)
                print(f"✅ MongoDB 세션 저장: {session_id} -> {mongodb_id}")
            except Exception as e:
                print(f"❌ MongoDB 세션 저장 실패: {e}")
        
        # 응답 데이터 (JSON 직렬화 안전)
        response_data = {
            "success": True,
            "session": {
                "id": session_id,
                "session_id": session_id,
                "user_id": user_email,
                "user_email": user_email,
                "name": session_name,
                "created_at": session_data["created_at"],
                "updated_at": session_data["updated_at"],
                "message_count": 0
            },
            "session_id": session_id  # 최상위에 session_id 포함
        }
        
        if mongodb_id:
            response_data["session"]["mongodb_id"] = mongodb_id
        
        return JSONResponse(response_data)
        
    except Exception as e:
        print(f"❌ 세션 생성 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"세션 생성 실패: {str(e)}"}
        )

@app.post("/api/chat")
async def chat(request: Request):
    """채팅 테스트"""
    user_email = request.session.get("user_email")
    if not user_email:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "로그인이 필요합니다."}
        )
    
    try:
        data = await request.json()
        message = data.get("message")
        session_id = data.get("session_id")
        
        if not message:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "메시지가 필요합니다."}
            )
        
        if not session_id:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "세션 ID가 필요합니다."}
            )
        
        # 간단한 AI 응답
        ai_response = f"테스트 응답: '{message}'를 받았습니다. 시간: {datetime.now().strftime('%H:%M:%S')}"
        
        # MongoDB에 메시지 저장
        if mongo_ready and db_mgr:
            try:
                # 사용자 메시지 저장
                user_msg_id = await db_mgr.save_message(session_id, "user", message)
                print(f"✅ 사용자 메시지 저장: {user_msg_id}")
                
                # AI 응답 저장
                ai_msg_id = await db_mgr.save_message(session_id, "assistant", ai_response)
                print(f"✅ AI 응답 저장: {ai_msg_id}")
                
                # 세션 업데이트
                await db_mgr.update_session(session_id, {
                    "updated_at": datetime.now().isoformat(),
                    "last_message": message[:50] + "..." if len(message) > 50 else message
                })
                print(f"✅ 세션 업데이트: {session_id}")
                
            except Exception as e:
                print(f"❌ MongoDB 메시지 저장 실패: {e}")
        
        return JSONResponse({
            "success": True,
            "response": ai_response,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ 채팅 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"채팅 실패: {str(e)}"}
        )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Quick Test Server 시작...")
    print("📍 주소: http://127.0.0.1:8300")
    print("📧 테스트 계정: admin@eora.ai / admin123")
    
    uvicorn.run(app, host="127.0.0.1", port=8300) 