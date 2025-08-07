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

# MongoDB 연결 정보 (레일웨이 환경변수 우선순위)
def get_mongodb_url():
    """레일웨이 환경에 맞는 MongoDB URL 반환"""
    # 레일웨이 환경 감지
    is_railway = any([
        os.getenv("RAILWAY_ENVIRONMENT"),
        os.getenv("RAILWAY_PROJECT_ID"),
        os.getenv("RAILWAY_SERVICE_ID")
    ])
    
    if is_railway:
        # 레일웨이 환경에서 우선순위대로 확인
        mongodb_urls = [
            os.getenv("MONGODB_URL"),  # 레일웨이에서 설정한 URL
            os.getenv("MONGO_URL"),    # 레일웨이 템플릿 변수
            # 개별 변수로 구성
            f"mongodb://{os.getenv('MONGOUSER')}:{os.getenv('MONGOPASSWORD')}@{os.getenv('MONGOHOST')}:{os.getenv('MONGOPORT')}" if all([
                os.getenv('MONGOUSER'), os.getenv('MONGOPASSWORD'), 
                os.getenv('MONGOHOST'), os.getenv('MONGOPORT')
            ]) else None,
            os.getenv("MONGODB_URI"),  # 백업 URI
        ]
        
        for url in mongodb_urls:
            if url and url.strip():
                logger.info(f"🚂 레일웨이 MongoDB URL 사용: {url[:50]}...")
                return url.strip()
        
        # Railway 환경에서 URL을 찾을 수 없는 경우
        logger.warning("⚠️ Railway 환경에서 MongoDB URL을 찾을 수 없습니다. 기본값 사용.")
    
    # 로컬 환경 또는 Railway에서 URL을 찾지 못한 경우
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    logger.info(f"💻 MongoDB URL 사용: {mongodb_uri}")
    return mongodb_uri

MONGODB_URL = get_mongodb_url()
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
        def __init__(self):
            """DBManager 초기화"""
            self.mongo_client = mongo_client
            self.db = db
            self.sessions_collection = sessions_collection
            self.chat_logs_collection = chat_logs_collection
            self.memories_collection = memories_collection
            self.users_collection = users_collection
            self.system_logs_collection = system_logs_collection
            self.points_collection = points_collection
            
        def is_connected(self):
            """데이터베이스 연결 상태를 확인합니다."""
            return self.mongo_client is not None and verify_connection()
            
        async def get_user_sessions(self, user_id):
            """사용자의 세션 목록을 조회합니다."""
            try:
                if self.sessions_collection is None:
                    return []
                
                sessions = list(self.sessions_collection.find({"user_id": user_id}))
                
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
                if self.sessions_collection is None:
                    return None
                
                # session_id가 없으면 생성
                if 'session_id' not in session_data or session_data['session_id'] is None:
                    import uuid
                    session_data['session_id'] = f"session_{uuid.uuid4().hex}"
                
                # ObjectId 직렬화를 위한 데이터 정리
                clean_session_data = {}
                for key, value in session_data.items():
                    if hasattr(value, 'isoformat'):  # datetime 객체
                        clean_session_data[key] = value.isoformat() if hasattr(value, 'isoformat') else str(value)
                    elif isinstance(value, ObjectId):  # ObjectId 객체
                        clean_session_data[key] = str(value)
                    else:
                        clean_session_data[key] = value
                
                result = self.sessions_collection.insert_one(clean_session_data)
                logger.info(f"✅ 세션 생성 성공: {result.inserted_id}")
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
                    "timestamp": datetime.now().isoformat(),
                    "created_at": datetime.now()  # MongoDB용 datetime 객체
                }
                
                result = chat_logs_collection.insert_one(message_data)
                logger.info(f"✅ 메시지 저장 성공: {session_id} - {sender}")
                return str(result.inserted_id)
            except Exception as e:
                logger.error(f"❌ 메시지 저장 실패: {e}")
                return None
        
        def initialize_user_points(self, user_id, initial_points=100000):
            """새 사용자의 포인트를 초기화합니다."""
            try:
                if points_collection is None:
                    logger.warning("⚠️ 포인트 컬렉션이 없어 메모리에서만 초기화")
                    return True
                
                # 이미 포인트가 있는지 확인
                existing_points = points_collection.find_one({"user_id": user_id})
                if existing_points:
                    logger.info(f"✅ 사용자 {user_id}의 포인트가 이미 존재함")
                    return True
                
                # 새 포인트 데이터 생성
                points_data = {
                    "user_id": user_id,
                    "current_points": initial_points,
                    "total_earned": initial_points,
                    "total_spent": 0,
                    "last_updated": datetime.now().isoformat(),
                    "history": [{
                        "type": "signup_bonus",
                        "amount": initial_points,
                        "description": f"신규 회원가입 보너스 ({initial_points:,}포인트)",
                        "timestamp": datetime.now().isoformat()
                    }]
                }
                
                result = points_collection.insert_one(points_data)
                logger.info(f"✅ 사용자 {user_id} 포인트 초기화 완료: {initial_points:,}포인트")
                return True
                
            except Exception as e:
                logger.error(f"❌ 포인트 초기화 실패: {e}")
                return False
    
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
        is_railway = any([
            os.getenv("RAILWAY_ENVIRONMENT"),
            os.getenv("RAILWAY_PROJECT_ID"),
            os.getenv("RAILWAY_SERVICE_ID"),
            os.getenv("RAILWAY", "false").lower() == "true"
        ])
        is_production = os.getenv("PRODUCTION", "false").lower() == "true"
        
        if is_railway:
            logger.info("🚂 Railway 클라우드 환경 감지")
        elif is_production:
            logger.info("☁️ 프로덕션 환경 감지")
        else:
            logger.info("💻 로컬 환경 감지")
        
        # 연결 URLs 목록 준비 (우선순위 순서)
        urls = []
        
        # 레일웨이 환경에서는 레일웨이 URL만 시도
        if is_railway:
            railway_urls = [
                os.getenv("MONGODB_URL"),
                os.getenv("MONGO_URL"),
                # 개별 변수로 구성된 URL
                f"mongodb://{os.getenv('MONGOUSER')}:{os.getenv('MONGOPASSWORD')}@{os.getenv('MONGOHOST')}:{os.getenv('MONGOPORT')}" if all([
                    os.getenv('MONGOUSER'), os.getenv('MONGOPASSWORD'), 
                    os.getenv('MONGOHOST'), os.getenv('MONGOPORT')
                ]) else None,
                os.getenv("MONGODB_URI")
            ]
            
            for url in railway_urls:
                if url and url.strip():
                    urls.append(url.strip())
                    
            if not urls:
                logger.error("❌ 레일웨이 환경에서 MongoDB URL을 찾을 수 없습니다")
                return False
        else:
            # 로컬 환경
            if MONGODB_URL and MONGODB_URL != "mongodb://localhost:27017":
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
                logger.info(f"🧹 정리된 URL: {cleaned_url[:50]}...")
                
                # 레일웨이 환경에 맞는 연결 옵션
                connect_options = {
                    "serverSelectionTimeoutMS": 10000,  # 10초
                    "connectTimeoutMS": 10000,           # 10초
                    "socketTimeoutMS": 20000,            # 20초
                }
                
                if is_railway:
                    connect_options.update({
                        "retryWrites": True,
                        "w": "majority",
                        "readPreference": "primary",
                        "maxPoolSize": 10,
                        "minPoolSize": 1
                    })
                
                mongo_client = pymongo.MongoClient(cleaned_url, **connect_options)
                
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
            global sessions_collection, chat_logs_collection, memories_collection, users_collection, system_logs_collection, points_collection
            
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

# 자동 연결을 비활성화하고 지연 초기화 사용
# init_mongodb_connection()  # 주석 처리

# 연결 상태 확인 (지연 초기화)
is_connected = False

def ensure_connection():
    """필요할 때만 MongoDB 연결을 초기화"""
    global is_connected
    if mongo_client is None:
        init_mongodb_connection()
        is_connected = verify_connection()
    return is_connected

def get_cached_mongodb_connection():
    """캐시된 MongoDB 연결을 반환합니다."""
    global mongo_client
    return mongo_client

# ========== 데이터베이스 관리자 클래스 ==========

class DatabaseManager:
    """데이터베이스 관리 클래스"""
    
    def __init__(self):
        # 지연 초기화: 실제 사용할 때까지 연결하지 않음
        self.mongo_client = None
        self.db = None
        self.sessions_collection = None
        self.chat_logs_collection = None
        self.memories_collection = None
        self.users_collection = None
        self.points_collection = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """필요할 때만 MongoDB 연결 및 컬렉션 초기화"""
        if not self._initialized:
            global mongo_client, db, sessions_collection, chat_logs_collection, memories_collection, users_collection, points_collection
            
            # 연결이 없으면 초기화
            if mongo_client is None:
                init_mongodb_connection()
            
            self.mongo_client = mongo_client
            self.db = mongo_client[DATABASE_NAME] if mongo_client else None
            self.sessions_collection = sessions_collection
            self.chat_logs_collection = chat_logs_collection
            self.memories_collection = memories_collection
            self.users_collection = users_collection
            self.points_collection = points_collection
            self._initialized = True
    
    def is_connected(self):
        """MongoDB 연결 상태 확인"""
        self._ensure_initialized()
        return verify_connection()
    
    def create_session(self, user_id: str, session_name: str = None) -> str:
        """MongoDB에 새 세션을 생성합니다"""
        self._ensure_initialized()
        if not self.is_connected() or self.sessions_collection is None:
            raise Exception("MongoDB가 연결되지 않았습니다")
        
        try:
            session_id = f"session_{user_id.replace('@', '_').replace('.', '_')}_{int(time.time() * 1000)}"
            
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "session_name": session_name or "새 대화",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "messages": []
            }
            
            # MongoDB에 삽입
            result = self.sessions_collection.insert_one(session_data)
            
            if result.inserted_id:
                # ObjectId를 문자열로 변환하여 반환
                session_id_str = str(result.inserted_id)
                logger.info(f"✅ 세션 생성 성공: {session_id_str}")
                return session_id_str
            else:
                raise Exception("세션 삽입 실패")
                
        except Exception as e:
            logger.error(f"❌ 세션 생성 오류: {str(e)}")
            raise e
    
    def save_message(self, session_id: str, user_message: str, ai_response: str, user_id: str = None):
        """MongoDB에 메시지를 저장합니다"""
        if not self.is_connected() or self.chat_logs_collection is None:
            logger.warning("MongoDB가 연결되지 않아 메시지 저장을 건너뜁니다")
            return False
        
        try:
            message_data = {
                "session_id": session_id,
                "user_id": user_id,
                "user_message": user_message,
                "ai_response": ai_response,
                "timestamp": datetime.now().isoformat(),
                "created_at": datetime.now()
            }
            
            self.chat_logs_collection.insert_one(message_data)
            logger.info(f"✅ 메시지 저장 성공: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 메시지 저장 오류: {str(e)}")
            return False
    
    def update_session(self, session_id: str, updates: Dict[str, Any]):
        """세션 정보를 업데이트합니다"""
        if not self.is_connected() or self.sessions_collection is None:
            return False
        
        try:
            updates["updated_at"] = datetime.now().isoformat()
            self.sessions_collection.update_one(
                {"session_id": session_id},
                {"$set": updates}
            )
            return True
        except Exception as e:
            logger.error(f"❌ 세션 업데이트 오류: {str(e)}")
            return False
    
    # ===== 포인트 시스템 관련 메서드 =====
    
    def initialize_user_points(self, user_id: str, initial_points: int = 100000):
        """새 사용자에게 초기 포인트를 부여합니다"""
        if not self.is_connected() or self.points_collection is None:
            logger.warning("MongoDB가 연결되지 않아 포인트 초기화를 건너뜁니다")
            return False
        
        try:
            # 이미 포인트 데이터가 있는지 확인
            existing_points = self.points_collection.find_one({"user_id": user_id})
            if existing_points:
                logger.info(f"💰 사용자 {user_id}는 이미 포인트가 있습니다")
                return True
            
            # 새 포인트 데이터 생성
            points_data = {
                "user_id": user_id,
                "points": initial_points,
                "total_earned": initial_points,
                "total_spent": 0,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "transactions": [{
                    "type": "initial",
                    "amount": initial_points,
                    "description": "회원가입 보너스",
                    "timestamp": datetime.now().isoformat()
                }]
            }
            
            self.points_collection.insert_one(points_data)
            logger.info(f"💰 사용자 {user_id}에게 초기 포인트 {initial_points} 지급")
            return True
            
        except Exception as e:
            logger.error(f"❌ 포인트 초기화 오류: {str(e)}")
            return False
    
    def get_user_points(self, user_id: str) -> int:
        """사용자의 현재 포인트를 조회합니다"""
        if not self.is_connected() or self.points_collection is None:
            return 0
        
        try:
            points_data = self.points_collection.find_one({"user_id": user_id})
            if points_data:
                return points_data.get("points", 0)
            else:
                # 포인트 데이터가 없으면 초기화
                self.initialize_user_points(user_id)
                return 100000  # 초기 포인트
                
        except Exception as e:
            logger.error(f"❌ 포인트 조회 오류: {str(e)}")
            return 0
    
    def deduct_points(self, user_id: str, amount: int, description: str = "채팅 사용") -> bool:
        """사용자의 포인트를 차감합니다"""
        if not self.is_connected() or self.points_collection is None:
            return False
        
        try:
            current_points = self.get_user_points(user_id)
            if current_points < amount:
                logger.warning(f"⚠️ 포인트 부족: {user_id} (현재: {current_points}, 필요: {amount})")
                return False
            
            new_points = current_points - amount
            transaction = {
                "type": "deduction",
                "amount": -amount,
                "description": description,
                "timestamp": datetime.now().isoformat()
            }
            
            self.points_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "points": new_points,
                        "updated_at": datetime.now().isoformat()
                    },
                    "$inc": {"total_spent": amount},
                    "$push": {"transactions": transaction}
                }
            )
            
            logger.info(f"💰 포인트 차감: {user_id} -{amount} (잔액: {new_points})")
            return True
            
        except Exception as e:
            logger.error(f"❌ 포인트 차감 오류: {str(e)}")
            return False
    
    def add_points(self, user_id: str, amount: int, description: str = "포인트 지급") -> bool:
        """사용자에게 포인트를 추가합니다"""
        if not self.is_connected() or self.points_collection is None:
            return False
        
        try:
            current_points = self.get_user_points(user_id)
            new_points = current_points + amount
            
            transaction = {
                "type": "addition",
                "amount": amount,
                "description": description,
                "timestamp": datetime.now().isoformat()
            }
            
            self.points_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "points": new_points,
                        "updated_at": datetime.now().isoformat()
                    },
                    "$inc": {"total_earned": amount},
                    "$push": {"transactions": transaction}
                }
            )
            
            logger.info(f"💰 포인트 추가: {user_id} +{amount} (잔액: {new_points})")
            return True
            
        except Exception as e:
            logger.error(f"❌ 포인트 추가 오류: {str(e)}")
            return False
    
    def get_points_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """사용자의 포인트 거래 내역을 조회합니다"""
        if not self.is_connected() or self.points_collection is None:
            return []
        
        try:
            points_data = self.points_collection.find_one({"user_id": user_id})
            if points_data and "transactions" in points_data:
                # 최신 거래 내역부터 반환
                transactions = points_data["transactions"][-limit:]
                transactions.reverse()
                return transactions
            return []
            
        except Exception as e:
            logger.error(f"❌ 포인트 내역 조회 오류: {str(e)}")
            return []

# 전역 데이터베이스 관리자 인스턴스 (지연 초기화)
db_mgr = None

def get_database_manager():
    """데이터베이스 관리자 인스턴스를 반환 (지연 초기화)"""
    global db_mgr
    if db_mgr is None:
        db_mgr = DatabaseManager()
    return db_mgr 