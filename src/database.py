#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 데이터베이스 관리 모듈
MongoDB 연결 및 컬렉션 관리를 담당합니다.
"""

import os
import sys
import json
import time
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any

import pymongo
from bson import ObjectId
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# .env 파일 로드 시도
try:
    load_dotenv()
    logger.info("✅ dotenv 로드 성공")
except Exception as e:
    logger.warning(f"⚠️ dotenv 로드 실패: {e}")

# MongoDB 연결 정보
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "eora_ai")

# 전역 변수
mongo_client = None
db = None
sessions_collection = None
chat_logs_collection = None
memories_collection = None
users_collection = None
system_logs_collection = None
points_collection = None

def generate_session_id():
    """고유한 세션 ID를 생성합니다."""
    return f"session_{uuid.uuid4().hex}"

# 데이터베이스 매니저 추가
def db_manager():
    """데이터베이스 관리 객체를 반환합니다."""
    global mongo_client, db, sessions_collection, chat_logs_collection, users_collection, points_collection
    
    if mongo_client is None:
        init_mongodb_connection()
    
    class DBManager:
        def is_connected(self):
            """데이터베이스 연결 상태를 확인합니다."""
            return mongo_client is not None and verify_connection()
            
        async def get_user_sessions(self, user_id):
            """사용자의 세션 목록을 조회합니다."""
            try:
                if sessions_collection is None:
                    return []
                
                sessions = list(sessions_collection.find({"user_id": user_id}))
                
                # ObjectId와 datetime 직렬화
                for session in sessions:
                    # ObjectId를 문자열로 변환
                    session["_id"] = str(session["_id"])
                    
                    # 모든 필드를 검사하여 datetime 객체 및 기타 직렬화 불가능한 타입 처리
                    for key, value in list(session.items()):
                        if isinstance(value, datetime):
                            session[key] = value.isoformat()
                        elif hasattr(value, 'isoformat'):  # datetime과 유사한 객체
                            session[key] = value.isoformat()
                        elif key in ["created_at", "updated_at", "timestamp"] and isinstance(value, (int, float)):
                            # UNIX 타임스탬프(초 단위) 처리
                            session[key] = str(value)
                
                return sessions
            except Exception as e:
                logger.error(f"❌ 세션 목록 조회 실패: {e}")
                return []
        
        async def create_session(self, session_data):
            """새 세션을 생성합니다."""
            try:
                if sessions_collection is None:
                    return None
                
                result = sessions_collection.insert_one(session_data)
                return str(result.inserted_id)
            except Exception as e:
                logger.error(f"❌ 세션 생성 실패: {e}")
                return None
        
        async def get_session(self, session_id):
            """특정 세션 정보를 조회합니다."""
            try:
                if sessions_collection is None:
                    return None
                
                session = sessions_collection.find_one({"session_id": session_id})
                if session:
                    # ObjectId를 문자열로 변환
                    session["_id"] = str(session["_id"])
                    
                    # 모든 필드를 검사하여 datetime 객체 및 기타 직렬화 불가능한 타입 처리
                    for key, value in list(session.items()):
                        if isinstance(value, datetime):
                            session[key] = value.isoformat()
                        elif hasattr(value, 'isoformat'):  # datetime과 유사한 객체
                            session[key] = value.isoformat()
                        elif key in ["created_at", "updated_at", "timestamp"] and isinstance(value, (int, float)):
                            # UNIX 타임스탬프(초 단위) 처리
                            session[key] = str(value)
                
                return session
            except Exception as e:
                logger.error(f"❌ 세션 조회 실패: {e}")
                return None
        
        async def get_session_messages(self, session_id):
            """세션의 메시지 목록을 조회합니다."""
            try:
                if chat_logs_collection is None:
                    return []
                
                # timestamp 기준으로 오름차순 정렬 (시간 순서대로)
                messages = list(chat_logs_collection.find({"session_id": session_id}).sort([("timestamp", 1), ("_id", 1)]))
                
                # ObjectId와 datetime 직렬화
                for message in messages:
                    # ObjectId를 문자열로 변환
                    message["_id"] = str(message["_id"])
                    
                    # 모든 필드를 검사하여 datetime 객체 및 기타 직렬화 불가능한 타입 처리
                    for key, value in list(message.items()):
                        if isinstance(value, datetime):
                            message[key] = value.isoformat()
                        elif hasattr(value, 'isoformat'):  # datetime과 유사한 객체
                            message[key] = value.isoformat()
                        elif key in ["created_at", "updated_at", "timestamp"] and isinstance(value, (int, float)):
                            # UNIX 타임스탬프(초 단위) 처리
                            message[key] = str(value)
                
                return messages
            except Exception as e:
                logger.error(f"❌ 세션 메시지 조회 실패: {e}")
                return []
                
        async def get_user_points(self, user_id):
            """사용자의 포인트 정보를 조회합니다."""
            try:
                if users_collection is None:
                    return {"points": 100000, "max_points": 100000}
                
                user = users_collection.find_one({"user_id": user_id})
                if user and "points" in user:
                    return {"points": user.get("points", 100000), "max_points": user.get("max_points", 100000)}
                
                # 기본값
                return {"points": 100000, "max_points": 100000}
            except Exception as e:
                logger.error(f"❌ 포인트 조회 실패: {e}")
                return {"points": 100000, "max_points": 100000}
                
        async def remove_session(self, session_id):
            """세션을 삭제합니다."""
            try:
                if sessions_collection is None:
                    return False
                
                result = sessions_collection.delete_one({"session_id": session_id})
                
                # 관련 메시지도 삭제
                if chat_logs_collection is not None:
                    chat_logs_collection.delete_many({"session_id": session_id})
                
                return result.deleted_count > 0
            except Exception as e:
                logger.error(f"❌ 세션 삭제 실패: {e}")
                return False
    
        async def update_session(self, session_id, update_data):
            """세션 정보를 업데이트합니다."""
            try:
                if sessions_collection is None:
                    return False
                
                result = sessions_collection.update_one(
                    {"session_id": session_id},
                    {"$set": update_data}
                )
                
                return result.modified_count > 0
            except Exception as e:
                logger.error(f"❌ 세션 업데이트 실패: {e}")
                return False
                
        async def save_message(self, session_id, sender, content):
            """메시지를 저장합니다."""
            try:
                if chat_logs_collection is None:
                    return None
                
                message_data = {
                    "session_id": session_id,
                    "role": sender,  # "user" 또는 "assistant"
                    "sender": sender,  # 호환성을 위해 유지
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                }
                
                result = chat_logs_collection.insert_one(message_data)
                return str(result.inserted_id)
            except Exception as e:
                logger.error(f"❌ 메시지 저장 실패: {e}")
                return None
    
    return DBManager()

def init_mongodb_connection():
    """MongoDB 연결 및 컬렉션 초기화"""
    global mongo_client, db, sessions_collection, chat_logs_collection, memories_collection, users_collection, system_logs_collection, points_collection
    
    # 연결이 이미 존재하면 재사용
    if mongo_client is not None:
        return True
        
    try:
        # MongoDB 연결
        logger.info("🔌 MongoDB 라이브러리 로드 성공")
        
        # 환경 감지
        is_railway = os.getenv("RAILWAY", "false").lower() == "true"
        is_production = os.getenv("PRODUCTION", "false").lower() == "true"
        
        if is_railway or is_production:
            logger.info("☁️ 클라우드 환경 감지")
        else:
            logger.info("💻 로컬 환경 감지")
        
        # 연결 URLs 목록 준비
        urls = []
        if MONGODB_URL:
            urls.append(MONGODB_URL)
        urls.append("mongodb://localhost:27017")
        
        logger.info(f"🔗 연결 시도할 URL 수: {len(urls)}")
        
        # 연결 시도
        connected = False
        for idx, url in enumerate(urls, 1):
            try:
                logger.info(f"🔗 MongoDB 연결 시도 {idx}/{len(urls)}: {url}")
                
                # URL 정리 (특수문자 등 처리)
                cleaned_url = url.strip()
                logger.info(f"🧹 정리된 URL: {cleaned_url}")
                
                mongo_client = pymongo.MongoClient(cleaned_url, serverSelectionTimeoutMS=5000)
                
                # 연결 확인
                mongo_client.admin.command('ping')
                connected = True
                logger.info("✅ MongoDB 연결 성공!")
                break
                
            except Exception as e:
                logger.error(f"❌ MongoDB 연결 실패 ({url}): {str(e)}")
                continue
        
        if not connected:
            logger.error("❌ 모든 MongoDB 연결 시도 실패")
            return False
            
        # 데이터베이스 및 컬렉션 초기화
        try:
            db = mongo_client[DATABASE_NAME]
            sessions_collection = db["sessions"]
            chat_logs_collection = db["chat_logs"]
            memories_collection = db["memories"]
            users_collection = db["users"]
            system_logs_collection = db["system_logs"]
            points_collection = db["points"]
            
            # 인덱스 생성
            sessions_collection.create_index([("user_id", pymongo.ASCENDING)])
            chat_logs_collection.create_index([("session_id", pymongo.ASCENDING)])
            memories_collection.create_index([("timestamp", pymongo.DESCENDING)])
            
            logger.info("✅ 컬렉션 초기화 성공")
            return True
            
        except Exception as e:
            logger.error(f"❌ 컬렉션 초기화 실패: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"❌ MongoDB 연결 초기화 중 오류: {str(e)}")
        return False

def verify_connection():
    """데이터베이스 연결 상태를 확인합니다."""
    global mongo_client
    
    if mongo_client is None:
        return False
        
    try:
        # 연결 확인
        mongo_client.admin.command('ping')
        return True
    except:
        return False

# 자동으로 연결 시도
init_mongodb_connection()

# 연결 상태 확인
is_connected = verify_connection()
logger.info(f"🔌 MongoDB 연결 상태: {'✅ 연결됨' if is_connected else '❌ 연결 안됨'}")

def get_cached_mongodb_connection():
    """캐시된 MongoDB 연결을 반환합니다."""
    global mongo_client
    return mongo_client 