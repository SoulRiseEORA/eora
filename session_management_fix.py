#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 세션 관리 기능 수정 스크립트
채팅 세션 관련 기능 문제를 해결합니다.
"""

import os
import sys
import json
import logging
import uuid
from datetime import datetime
import pymongo
from pymongo import MongoClient
from bson import ObjectId

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB 연결 정보
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "eora_ai")

def generate_session_id():
    """고유한 세션 ID를 생성합니다."""
    return f"session_{uuid.uuid4().hex}"

def init_mongodb():
    """MongoDB 연결 및 컬렉션 초기화"""
    try:
        # MongoDB 연결
        client = MongoClient(MONGODB_URL)
        client.admin.command('ping')  # 연결 테스트
        logger.info("✅ MongoDB 연결 성공")
        
        # 데이터베이스 및 컬렉션 설정
        db = client[DATABASE_NAME]
        sessions_collection = db["sessions"]
        chat_logs_collection = db["chat_logs"]
        
        # 인덱스 생성 (필요한 경우)
        try:
            sessions_collection.create_index([("user_id", 1)])
            sessions_collection.create_index([("created_at", -1)])
            chat_logs_collection.create_index([("session_id", 1)])
            chat_logs_collection.create_index([("timestamp", -1)])
            logger.info("✅ MongoDB 인덱스 생성 완료")
        except Exception as e:
            logger.warning(f"⚠️ MongoDB 인덱스 생성 실패: {e}")
        
        return client, db, sessions_collection, chat_logs_collection
    
    except Exception as e:
        logger.error(f"❌ MongoDB 연결 실패: {e}")
        return None, None, None, None

def fix_sessions():
    """세션 관련 문제를 진단하고 수정합니다."""
    logger.info("🔧 세션 관리 기능 진단 및 수정 시작")
    
    # MongoDB 연결
    client, db, sessions_collection, chat_logs_collection = init_mongodb()
    
    if not client:
        logger.error("❌ MongoDB 연결 실패로 작업을 중단합니다.")
        return False
    
    try:
        # 1. 비정상 세션 찾기 및 정리
        logger.info("🔍 비정상 세션 검사 중...")
        invalid_sessions = list(sessions_collection.find({
            "$or": [
                {"name": {"$exists": False}},
                {"name": None},
                {"name": ""},
                {"name": "undefined"},
                {"name": "null"}
            ]
        }))
        
        if invalid_sessions:
            logger.warning(f"⚠️ {len(invalid_sessions)}개의 비정상 세션을 찾았습니다.")
            
            for session in invalid_sessions:
                # 비정상 세션 수정
                sessions_collection.update_one(
                    {"_id": session["_id"]},
                    {"$set": {"name": f"복구된 세션 {datetime.now().strftime('%Y-%m-%d %H:%M')}"}}
                )
            logger.info(f"✅ {len(invalid_sessions)}개의 비정상 세션을 수정했습니다.")
        else:
            logger.info("✅ 비정상 세션이 없습니다.")
        
        # 2. 메시지 없는 세션 확인
        sessions = list(sessions_collection.find({}))
        empty_sessions = []
        
        for session in sessions:
            session_id = session.get("_id")
            if not session_id:
                continue
                
            # 해당 세션의 메시지 수 확인
            message_count = chat_logs_collection.count_documents({"session_id": str(session_id)})
            
            if message_count == 0:
                empty_sessions.append(session)
        
        logger.info(f"ℹ️ {len(empty_sessions)}개의 빈 세션이 있습니다.")
        
        # 3. 테스트 세션 생성
        logger.info("🔧 테스트 세션 생성 중...")
        
        test_session_id = generate_session_id()
        test_session = {
            "_id": test_session_id,
            "session_id": test_session_id,
            "name": f"테스트 세션 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "user_id": "test_user",
            "message_count": 0
        }
        
        result = sessions_collection.insert_one(test_session)
        logger.info(f"✅ 테스트 세션 생성 완료: {test_session_id}")
        
        # 4. 테스트 메시지 생성
        test_message = {
            "session_id": test_session_id,
            "content": "이것은 테스트 메시지입니다.",
            "role": "user",
            "user_id": "test_user",
            "timestamp": datetime.now()
        }
        
        result = chat_logs_collection.insert_one(test_message)
        logger.info(f"✅ 테스트 메시지 생성 완료: {result.inserted_id}")
        
        # 5. 세션 목록 확인
        updated_sessions = list(sessions_collection.find({}))
        logger.info(f"ℹ️ 현재 총 {len(updated_sessions)}개의 세션이 있습니다.")
        
        # 정상 동작 확인
        logger.info("🔍 세션 시스템 정상 작동 확인 중...")
        
        test_messages = list(chat_logs_collection.find({"session_id": test_session_id}))
        if test_messages:
            logger.info(f"✅ 메시지 조회 성공: {len(test_messages)}개의 메시지가 있습니다.")
            return True
        else:
            logger.error("❌ 메시지 조회 실패: 테스트 메시지를 찾을 수 없습니다.")
            return False
    
    except Exception as e:
        logger.error(f"❌ 세션 수정 중 오류 발생: {e}")
        return False
    finally:
        # MongoDB 연결 종료
        if client:
            client.close()
            logger.info("✅ MongoDB 연결 종료")

if __name__ == "__main__":
    result = fix_sessions()
    if result:
        logger.info("✅ 세션 관리 기능 수정 완료")
    else:
        logger.error("❌ 세션 관리 기능 수정 실패") 