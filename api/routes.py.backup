#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - API 라우트
이 파일은 app.py에서 분리된 API 라우트 정의를 포함합니다.
"""

import os
import sys
import logging
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 상위 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from fastapi import APIRouter, Request, HTTPException, Depends, WebSocket, WebSocketDisconnect, Form, File, UploadFile
from fastapi.responses import JSONResponse

# 로깅 설정
logger = logging.getLogger(__name__)

# 라우터 정의
router = APIRouter()

# 인증 관련 라우트
@router.post("/api/register")
async def register(request: Request):
    """사용자 등록"""
    from database import db_manager
    import hashlib
    
    try:
        data = await request.json()
        username = data.get("name")
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "이메일과 비밀번호가 필요합니다."}
            )
        
        # 기존 사용자 확인
        existing_user = await db_manager.get_user_by_email(email)
        if existing_user:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "이미 등록된 이메일입니다."}
            )
        
        # 비밀번호 해시화
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # 사용자 정보 생성
        user_data = {
            "username": username or email.split('@')[0],
            "email": email,
            "password_hash": password_hash,
            "is_admin": email == "admin@eora.ai",  # 관리자 계정
            "created_at": datetime.now(),
            "last_login": None,
            "session_count": 0,
            "total_interactions": 0
        }
        
        # 데이터베이스에 저장
        user_id = await db_manager.create_user(user_data)
        
        return {
            "success": True,
            "message": "회원가입이 완료되었습니다.",
            "user": {
                "id": user_id,
                "name": username or email.split('@')[0],
                "email": email
            }
        }
    except Exception as e:
        logger.error(f"회원가입 오류: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"회원가입 중 오류가 발생했습니다: {str(e)}"}
        )

@router.post("/api/login")
async def login(request: Request):
    """사용자 로그인"""
    from database import db_manager
    from auth_system import auth_system
    import hashlib
    
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "이메일과 비밀번호가 필요합니다."}
            )
        
        # 사용자 정보 조회
        user = await db_manager.get_user_by_email(email)
        if not user:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "이메일 또는 비밀번호가 잘못되었습니다."}
            )
        
        # 디버깅을 위해 사용자 정보 로그 출력
        logger.info(f"사용자 정보: {email}, 필드: {list(user.keys())}")
        
        # 비밀번호 검증 - password_hash 필드가 없는 경우 대비
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if "password_hash" not in user:
            logger.error(f"사용자 {email}의 password_hash 필드가 없습니다.")
            
            # 비밀번호 해시 필드 자동 추가
            await db_manager.collections[db_manager.USERS_COLLECTION].update_one(
                {"email": email},
                {"$set": {"password_hash": password_hash}}
            )
            logger.info(f"사용자 {email}에 password_hash 필드 자동 추가 완료")
            
            # 업데이트된 사용자 정보 다시 조회
            user = await db_manager.get_user_by_email(email)
            if not user or "password_hash" not in user:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "message": "계정 정보에 오류가 있습니다. 관리자에게 문의하세요."}
                )
        
        if user["password_hash"] != password_hash:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "이메일 또는 비밀번호가 잘못되었습니다."}
            )
        
        # JWT 토큰 생성
        token = auth_system.create_jwt_token(str(user["_id"]), user.get("is_admin", False))
        
        # 세션 ID 생성
        session_id = auth_system.generate_session_id()
        
        # 세션 정보 저장
        session_data = {
            "user_id": str(user["_id"]),
            "session_id": session_id,
            "token": token,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "ip_address": None,
            "user_agent": None
        }
        await db_manager.create_session(session_data)
        
        # 마지막 로그인 시간 업데이트
        await db_manager.update_user_last_login(str(user["_id"]))
        
        return {
            "success": True,
            "message": "로그인이 완료되었습니다.",
            "session_id": session_id,
            "token": token,
            "user": {
                "user_id": str(user["_id"]),
                "username": user.get("username"),
                "email": user.get("email"),
                "is_admin": user.get("is_admin", False),
                "role": "admin" if user.get("is_admin", False) else "user"
            }
        }
    except Exception as e:
        logger.error(f"로그인 오류: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"로그인 중 오류가 발생했습니다: {str(e)}"}
        )

@router.post("/api/admin/login")
async def admin_login(request: Request):
    """관리자 로그인"""
    from database import db_manager
    from auth_system import auth_system
    import hashlib
    
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "이메일과 비밀번호가 필요합니다."}
            )
        
        # 사용자 정보 조회
        user = await db_manager.get_user_by_email(email)
        if not user:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "이메일 또는 비밀번호가 잘못되었습니다."}
            )
        
        # 디버깅을 위해 사용자 정보 로그 출력
        logger.info(f"관리자 정보: {email}, 필드: {list(user.keys())}")
        
        # 관리자 권한 확인
        if not user.get("is_admin", False):
            # 관리자 권한 자동 부여 (admin@eora.ai 이메일인 경우)
            if email == "admin@eora.ai":
                await db_manager.collections[db_manager.USERS_COLLECTION].update_one(
                    {"email": email},
                    {"$set": {"is_admin": True}}
                )
                logger.info(f"사용자 {email}에 관리자 권한 자동 부여 완료")
                user["is_admin"] = True
            else:
                return JSONResponse(
                    status_code=403,
                    content={"success": False, "message": "관리자 권한이 없습니다."}
                )
        
        # 비밀번호 검증 - password_hash 필드가 없는 경우 대비
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if "password_hash" not in user:
            logger.error(f"사용자 {email}의 password_hash 필드가 없습니다.")
            
            # 비밀번호 해시 필드 자동 추가
            await db_manager.collections[db_manager.USERS_COLLECTION].update_one(
                {"email": email},
                {"$set": {"password_hash": password_hash}}
            )
            logger.info(f"사용자 {email}에 password_hash 필드 자동 추가 완료")
            
            # 업데이트된 사용자 정보 다시 조회
            user = await db_manager.get_user_by_email(email)
            if not user or "password_hash" not in user:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "message": "계정 정보에 오류가 있습니다. 관리자에게 문의하세요."}
                )
        
        if user["password_hash"] != password_hash:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "이메일 또는 비밀번호가 잘못되었습니다."}
            )
        
        # JWT 토큰 생성
        token = auth_system.create_jwt_token(str(user["_id"]), True)
        
        # 세션 ID 생성
        session_id = auth_system.generate_session_id()
        
        # 세션 정보 저장
        session_data = {
            "user_id": str(user["_id"]),
            "session_id": session_id,
            "token": token,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "ip_address": None,
            "user_agent": None,
            "is_admin_session": True
        }
        await db_manager.create_session(session_data)
        
        # 마지막 로그인 시간 업데이트
        await db_manager.update_user_last_login(str(user["_id"]))
        
        return {
            "success": True,
            "message": "관리자 로그인이 완료되었습니다.",
            "session_id": session_id,
            "token": token,
            "user": {
                "user_id": str(user["_id"]),
                "username": user.get("username"),
                "email": user.get("email"),
                "is_admin": True,
                "role": "admin"
            }
        }
    except Exception as e:
        logger.error(f"관리자 로그인 오류: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"관리자 로그인 중 오류가 발생했습니다: {str(e)}"}
        )

@router.post("/api/logout")
async def logout(request: Request):
    """로그아웃"""
    from auth_system import auth_system
    
    try:
        data = await request.json()
        session_id = data.get("session_id")
        
        if not session_id:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "세션 ID가 필요합니다."}
            )
        
        # 세션 제거
        await auth_system.logout_user(session_id)
        
        return {
            "success": True,
            "message": "로그아웃이 완료되었습니다."
        }
    except Exception as e:
        logger.error(f"로그아웃 오류: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"로그아웃 중 오류가 발생했습니다: {str(e)}"}
        )

# 세션 관련 라우트
@router.get("/api/sessions")
async def get_sessions(request: Request):
    """사용자 세션 목록 조회"""
    from database import db_manager
    from auth_system import get_current_user
    
    try:
        user = get_current_user(request)
        if not user:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "인증이 필요합니다."}
            )
        
        user_id = user.get("user_id")
        
        # 사용자 세션 목록 조회
        sessions = await db_manager().get_user_sessions(user_id)
        
        return JSONResponse({
            "success": True,
            "sessions": sessions
        })
    except Exception as e:
        logger.error(f"세션 목록 조회 오류: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"세션 목록 조회 중 오류가 발생했습니다: {str(e)}"}
        )

@router.post("/api/sessions")
async def create_session(request: Request):
    """새 세션 생성"""
    from database import db_manager, generate_session_id
    from auth_system import get_current_user
    
    try:
        user = get_current_user(request)
        if not user:
            raise HTTPException(status_code=401, detail="인증이 필요합니다.")
        
        data = await request.json()
        session_name = data.get("name", f"세션 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        user_id = user.get("user_id")
        session_id = generate_session_id()
        
        # 세션 데이터 생성
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "name": session_name,
            "created_at": time.time(),
            "updated_at": time.time(),
            "message_count": 0
        }
        
        # 세션 저장
        await db_manager().create_session(session_data)
        
        return {
            "success": True,
            "session_id": session_id,
            "name": session_name
        }
    except Exception as e:
        logger.error(f"세션 생성 오류: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"세션 생성 중 오류가 발생했습니다: {str(e)}"}
        )

@router.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, request: Request):
    """세션의 메시지 목록 조회"""
    from database import db_manager
    from auth_system import get_current_user
    
    try:
        user = get_current_user(request)
        if not user:
            raise HTTPException(status_code=401, detail="인증이 필요합니다.")
        
        # 세션 존재 확인
        session = await db_manager().get_session(session_id)
        if not session:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "세션을 찾을 수 없습니다."}
            )
        
        # 세션 소유자 확인
        if session.get("user_id") != user.get("user_id"):
            return JSONResponse(
                status_code=403,
                content={"success": False, "message": "이 세션에 접근할 권한이 없습니다."}
            )
        
        # 메시지 조회
        messages = await db_manager().get_session_messages(session_id)
        
        # 메시지 포맷팅
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "id": str(msg.get("_id")),
                "user_message": msg.get("content") if msg.get("sender") == "user" else "",
                "ai_response": msg.get("content") if msg.get("sender") == "ai" else "",
                "timestamp": msg.get("timestamp")
            })
        
        return {
            "success": True,
            "messages": formatted_messages
        }
    except Exception as e:
        logger.error(f"세션 메시지 조회 오류: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"세션 메시지 조회 중 오류가 발생했습니다: {str(e)}"}
        )

@router.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, request: Request):
    """세션 삭제"""
    from database import db_manager
    from auth_system import get_current_user
    
    try:
        user = get_current_user(request)
        if not user:
            raise HTTPException(status_code=401, detail="인증이 필요합니다.")
        
        # 세션 존재 확인
        session = await db_manager().get_session(session_id)
        if not session:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "세션을 찾을 수 없습니다."}
            )
        
        # 세션 소유자 확인
        if session.get("user_id") != user.get("user_id"):
            return JSONResponse(
                status_code=403,
                content={"success": False, "message": "이 세션에 접근할 권한이 없습니다."}
            )
        
        # 세션 삭제
        await db_manager().remove_session(session_id)
        
        return {
            "success": True,
            "message": "세션이 삭제되었습니다."
        }
    except Exception as e:
        logger.error(f"세션 삭제 오류: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"세션 삭제 중 오류가 발생했습니다: {str(e)}"}
        )

@router.put("/api/sessions/{session_id}/rename")
async def rename_session(session_id: str, request: Request):
    """세션 이름 변경"""
    from database import db_manager
    from auth_system import get_current_user
    
    try:
        user = get_current_user(request)
        if not user:
            raise HTTPException(status_code=401, detail="인증이 필요합니다.")
        
        # 세션 존재 확인
        session = await db_manager().get_session(session_id)
        if not session:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "세션을 찾을 수 없습니다."}
            )
        
        # 세션 소유자 확인
        if session.get("user_id") != user.get("user_id"):
            return JSONResponse(
                status_code=403,
                content={"success": False, "message": "이 세션에 접근할 권한이 없습니다."}
            )
        
        # 새 이름 가져오기
        data = await request.json()
        new_name = data.get("name")
        if not new_name:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "새 이름이 필요합니다."}
            )
        
        # 세션 업데이트
        await db_manager().update_session(session_id, {"name": new_name})
        
        return {
            "success": True,
            "message": "세션 이름이 변경되었습니다."
        }
    except Exception as e:
        logger.error(f"세션 이름 변경 오류: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"세션 이름 변경 중 오류가 발생했습니다: {str(e)}"}
        )

# 채팅 관련 라우트
@router.post("/api/chat")
async def chat_endpoint(request: Request):
    """채팅 API"""
    from database import db_manager
    from auth_system import get_current_user
    from services.openai_service import generate_response
    
    try:
        user = get_current_user(request)
        if not user:
            raise HTTPException(status_code=401, detail="인증이 필요합니다.")
        
        data = await request.json()
        message = data.get("message")
        session_id = data.get("session_id")
        
        if not message:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "메시지가 필요합니다."}
            )
        
        if not session_id:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "세션 ID가 필요합니다."}
            )
        
        # 세션 존재 확인
        session = await db_manager().get_session(session_id)
        if not session:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "세션을 찾을 수 없습니다."}
            )
        
        # 세션 소유자 확인
        if session.get("user_id") != user.get("user_id"):
            return JSONResponse(
                status_code=403,
                content={"success": False, "message": "이 세션에 접근할 권한이 없습니다."}
            )
        
        # 사용자 메시지 저장
        await db_manager().save_message(session_id, "user", message)
        
        # AI 응답 생성
        response = await generate_response(message, session_id, user.get("user_id"))
        
        # AI 응답 저장
        await db_manager().save_message(session_id, "ai", response)
        
        # 세션 메시지 수 업데이트
        await db_manager().update_session(session_id, {
            "message_count": session.get("message_count", 0) + 2,
            "updated_at": time.time()
        })
        
        return {
            "success": True,
            "response": response
        }
    except Exception as e:
        logger.error(f"채팅 API 오류: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"채팅 처리 중 오류가 발생했습니다: {str(e)}"}
        )

# 상태 확인 라우트
@router.get("/health")
async def health():
    """서버 상태 확인"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@router.get("/api/status")
async def api_status():
    """API 상태 확인"""
    from database import db_manager
    
    try:
        # 데이터베이스 연결 확인
        db_connected = db_manager().is_connected()
        
        return {
            "success": True,
            "status": "operational",
            "database_connected": db_connected,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"API 상태 확인 오류: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"API 상태 확인 중 오류가 발생했습니다: {str(e)}"}
        ) 