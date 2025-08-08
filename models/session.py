#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 세션 모델
이 파일은 세션 관련 Pydantic 모델을 정의합니다.
"""

import sys
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

# 상위 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

class SessionCreate(BaseModel):
    """세션 생성 모델"""
    name: str = Field(default="새 세션")
    user_id: Optional[str] = None

class SessionResponse(BaseModel):
    """세션 응답 모델"""
    id: str
    name: str
    created_at: datetime
    last_activity: datetime
    message_count: int = 0
    user_id: str

class MessageCreate(BaseModel):
    """메시지 생성 모델"""
    session_id: str
    content: str
    role: str = "user"  # "user" 또는 "ai"
    user_id: Optional[str] = None

class MessageResponse(BaseModel):
    """메시지 응답 모델"""
    id: str
    session_id: str
    content: str
    role: str
    timestamp: datetime
    user_id: Optional[str] = None

class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    message: str
    session_id: str
    recall_type: Optional[str] = "normal"

class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    response: str
    message_id: Optional[str] = None
    timestamp: str
    token_info: Optional[Dict[str, Any]] = None

class SessionListResponse(BaseModel):
    """세션 목록 응답 모델"""
    sessions: List[SessionResponse]
    success: bool = True

class MessageListResponse(BaseModel):
    """메시지 목록 응답 모델"""
    messages: List[MessageResponse]
    success: bool = True

class SessionUpdateRequest(BaseModel):
    """세션 업데이트 요청 모델"""
    name: Optional[str] = None 