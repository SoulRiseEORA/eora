#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 인증 모델
이 파일은 인증 관련 Pydantic 모델을 정의합니다.
"""

import sys
import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr

# 상위 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

class UserRegister(BaseModel):
    """사용자 등록 모델"""
    name: Optional[str] = None
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    """사용자 로그인 모델"""
    email: EmailStr
    password: str

class AdminLogin(BaseModel):
    """관리자 로그인 모델"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """사용자 응답 모델"""
    user_id: str
    username: Optional[str] = None
    email: EmailStr
    is_admin: bool = False
    role: str = "user"

class TokenResponse(BaseModel):
    """토큰 응답 모델"""
    token: str
    session_id: str
    user: UserResponse
    success: bool = True
    message: str = "로그인이 완료되었습니다."

class LogoutRequest(BaseModel):
    """로그아웃 요청 모델"""
    session_id: str

class PasswordChangeRequest(BaseModel):
    """비밀번호 변경 요청 모델"""
    current_password: str
    new_password: str
    email: Optional[EmailStr] = None

class UserProfileUpdate(BaseModel):
    """사용자 프로필 업데이트 모델"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_image: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None 