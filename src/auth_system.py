#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 인증 시스템
사용자 인증, 세션 관리, 토큰 생성 및 검증을 담당합니다.
"""

import os
import sys
import json
import logging
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import wraps
import logging
import json
import hashlib
import uuid
import jwt
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from bson import ObjectId

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경변수에서 시크릿 키 가져오기
SECRET_KEY = os.environ.get("SECRET_KEY", "eora_secret_key")
ALGORITHM = "HS256"

class AuthSystem:
    def __init__(self, secret_key="eora_secret_key", algorithm="HS256"):
        self.SECRET_KEY = secret_key
        self.ALGORITHM = algorithm
        self.active_sessions = {}  # 활성 세션 저장
        
    def hash_password(self, password):
        """비밀번호를 SHA-256으로 해싱"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_session_id(self):
        """고유한 세션 ID 생성"""
        return str(uuid.uuid4())
    
    def create_jwt_token(self, data: dict, expires_delta: timedelta = None):
        """JWT 토큰 생성"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt
    
    def verify_jwt_token(self, token: str):
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None
    
    def register_session(self, user_id, session_id):
        """사용자 세션 등록"""
        if user_id not in self.active_sessions:
            self.active_sessions[user_id] = []
        
        # 세션 추가 (최대 10개 유지)
        self.active_sessions[user_id].append(session_id)
        if len(self.active_sessions[user_id]) > 10:
            self.active_sessions[user_id] = self.active_sessions[user_id][-10:]
        
        return True
    
    def validate_session(self, user_id, session_id):
        """세션 유효성 검증"""
        return user_id in self.active_sessions and session_id in self.active_sessions[user_id]

# 현재 사용자 정보 가져오기
def get_current_user(request: Request):
    user = None
    session_user = None
    
    # 1. 세션에서 user 정보 시도 (세션 미들웨어가 있을 때만)
    if hasattr(request, 'session'):
        try:
            session_user = request.session.get('user')
            if session_user:
                logger.info(f"✅ 세션에서 user 조회 성공: {session_user.get('email', 'unknown')}")
        except Exception as e:
            logger.warning(f"⚠️ 세션 읽기 오류: {e}")
            session_user = None
    
    if session_user:
        user = session_user
    else:
        # 2. 쿠키에서 user 정보 시도
        try:
            user_cookie = request.cookies.get('user')
            if user_cookie:
                user = json.loads(user_cookie)
                logger.info(f"✅ 쿠키에서 user 조회 성공: {user.get('email', 'unknown')}")
        except Exception as e:
            logger.warning(f"⚠️ 쿠키 파싱 오류: {e}")
            user = None
        
        # 3. 개별 쿠키에서 정보 조합
        if not user:
            user_email = request.cookies.get('user_email')
            if user_email:
                user = {"email": user_email}
                logger.info(f"✅ 개별 쿠키에서 user 조회 성공: {user_email}")
    
    # 4. user 정보 보정 (관리자 판별 포함)
    if user:
        user['email'] = user.get('email', '')
        user['user_id'] = user.get('user_id') or user.get('email') or 'anonymous'
        user['role'] = 'admin' if user.get('email') == 'admin@eora.ai' else 'user'
        user['is_admin'] = user.get('email') == 'admin@eora.ai'
        
        # 필수 필드 보정
        if 'name' not in user:
            user['name'] = user['email'].split('@')[0] if '@' in user['email'] else 'User'
    else:
        logger.warning("⚠️ 모든 방법으로 user 정보 조회 실패")
    
    return user 