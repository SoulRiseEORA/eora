import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from bson import ObjectId
from typing import Optional, Dict, List
import asyncio

logger = logging.getLogger(__name__)

class DatabaseManager:
    """MongoDB 데이터베이스 관리 클래스"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.is_connected = False
        
        # 환경변수에서 가져오고, 없으면 기본값 사용
        self.mongodb_url = os.environ.get('MONGODB_URL')
        if not self.mongodb_url:
            # 로컬 MongoDB 기본 연결 문자열
            self.mongodb_url = "mongodb://localhost:27017/eora_ai"
            logger.warning("⚠️ MONGODB_URL 환경변수가 설정되지 않아 로컬 기본값을 사용합니다.")
            logger.warning("💡 환경 변수 MONGODB_URL을 설정하세요.")
        else:
            logger.info("✅ MONGODB_URL 환경변수 확인됨")
        
    async def connect(self):
        """MongoDB 연결"""
        try:
            self.client = AsyncIOMotorClient(self.mongodb_url)
            self.db = self.client.eora_database
            
            # 연결 테스트
            await self.client.admin.command('ping')
            self.is_connected = True
            logger.info("MongoDB 연결 성공")
            
            # 컬렉션 초기화
            await self._initialize_collections()
            
        except Exception as e:
            logger.error(f"MongoDB 연결 실패: {str(e)}")
            self.is_connected = False
            self.client = None
            self.db = None
            raise
    
    async def disconnect(self):
        """MongoDB 연결 해제"""
        if self.client:
            self.client.close()
            logger.info("MongoDB 연결 해제")
    
    async def _initialize_collections(self):
        """필요한 컬렉션들 초기화"""
        collections = [
            'user_interactions',
            'consciousness_events', 
            'memory_patterns',
            'system_logs',
            'user_profiles',
            'users',
            'sessions',
            'messages'
        ]
        
        for collection_name in collections:
            if collection_name not in await self.db.list_collection_names():
                await self.db.create_collection(collection_name)
                logger.info(f"컬렉션 생성: {collection_name}")
    
    def _convert_objectid_to_str(self, data):
        """ObjectId를 문자열로 변환하는 헬퍼 메서드"""
        if isinstance(data, dict):
            return {k: self._convert_objectid_to_str(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_objectid_to_str(item) for item in data]
        elif isinstance(data, ObjectId):
            return str(data)
        else:
            return data
    
    async def store_interaction(self, user_id: str, user_input: str, ai_response: str, 
                               consciousness_level: float = 0.0, metadata: Dict = None):
        if not self.is_connected or self.db is None:
            logger.error("DB 연결이 되어 있지 않습니다.")
            return None
        """사용자 상호작용 저장"""
        try:
            interaction_data = {
                "user_id": user_id,
                "user_input": user_input,
                "ai_response": ai_response,
                "consciousness_level": consciousness_level,
                "metadata": metadata or {},
                "timestamp": asyncio.get_event_loop().time()
            }
            
            result = await self.db.user_interactions.insert_one(interaction_data)
            logger.info(f"상호작용 저장 완료: {result.inserted_id}")
            # ObjectId를 문자열로 변환하여 반환
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"상호작용 저장 실패: {str(e)}")
            return None
    
    async def get_user_interactions(self, user_id: str, limit: int = 50) -> List[Dict]:
        if self.db is None:
            raise RuntimeError('DB 연결이 되어 있지 않습니다.')
        """사용자 상호작용 조회"""
        try:
            cursor = self.db.user_interactions.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit)
            
            interactions = await cursor.to_list(length=limit)
            return interactions
            
        except Exception as e:
            logger.error(f"사용자 상호작용 조회 실패: {str(e)}")
            return []
    
    async def search_interactions(self, query: str, user_id: Optional[str] = None, 
                                 limit: int = 20) -> List[Dict]:
        """상호작용 검색"""
        try:
            search_filter = {
                "$or": [
                    {"user_input": {"$regex": query, "$options": "i"}},
                    {"ai_response": {"$regex": query, "$options": "i"}}
                ]
            }
            
            if user_id:
                search_filter["user_id"] = user_id
            
            cursor = self.db.user_interactions.find(search_filter).sort("timestamp", -1).limit(limit)
            interactions = await cursor.to_list(length=limit)
            return interactions
            
        except Exception as e:
            logger.error(f"상호작용 검색 실패: {str(e)}")
            return []
    
    async def store_consciousness_event(self, user_id: str, event_type: str, 
                                       consciousness_level: float, metadata: Dict = None):
        """의식 이벤트 저장"""
        try:
            event_data = {
                "user_id": user_id,
                "event_type": event_type,
                "consciousness_level": consciousness_level,
                "metadata": metadata or {},
                "timestamp": asyncio.get_event_loop().time()
            }
            
            result = await self.db.consciousness_events.insert_one(event_data)
            logger.info(f"의식 이벤트 저장 완료: {result.inserted_id}")
            # ObjectId를 문자열로 변환하여 반환
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"의식 이벤트 저장 실패: {str(e)}")
            return None
    
    async def get_consciousness_stats(self, user_id: Optional[str] = None) -> Dict:
        """의식 통계 조회"""
        try:
            pipeline = []
            
            if user_id:
                pipeline.append({"$match": {"user_id": user_id}})
            
            pipeline.extend([
                {
                    "$group": {
                        "_id": None,
                        "total_events": {"$sum": 1},
                        "avg_consciousness": {"$avg": "$consciousness_level"},
                        "max_consciousness": {"$max": "$consciousness_level"},
                        "min_consciousness": {"$min": "$consciousness_level"}
                    }
                }
            ])
            
            result = await self.db.consciousness_events.aggregate(pipeline).to_list(length=1)
            
            if result:
                return result[0]
            else:
                return {
                    "total_events": 0,
                    "avg_consciousness": 0.0,
                    "max_consciousness": 0.0,
                    "min_consciousness": 0.0
                }
                
        except Exception as e:
            logger.error(f"의식 통계 조회 실패: {str(e)}")
            return {
                "total_events": 0,
                "avg_consciousness": 0.0,
                "max_consciousness": 0.0,
                "min_consciousness": 0.0
            }
    
    async def store_memory_pattern(self, pattern_type: str, pattern_data: Dict, 
                                  frequency: int = 1):
        """메모리 패턴 저장"""
        try:
            pattern = {
                "pattern_type": pattern_type,
                "pattern_data": pattern_data,
                "frequency": frequency,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            result = await self.db.memory_patterns.insert_one(pattern)
            logger.info(f"메모리 패턴 저장 완료: {result.inserted_id}")
            return result.inserted_id
            
        except Exception as e:
            logger.error(f"메모리 패턴 저장 실패: {str(e)}")
            return None
    
    async def get_memory_patterns(self, pattern_type: Optional[str] = None, 
                                 limit: int = 50) -> List[Dict]:
        """메모리 패턴 조회"""
        try:
            filter_query = {}
            if pattern_type:
                filter_query["pattern_type"] = pattern_type
            
            cursor = self.db.memory_patterns.find(filter_query).sort("timestamp", -1).limit(limit)
            patterns = await cursor.to_list(length=limit)
            return patterns
            
        except Exception as e:
            logger.error(f"메모리 패턴 조회 실패: {str(e)}")
            return []
    
    async def log_system_event(self, event_type: str, message: str, level: str = "INFO", 
                              metadata: Dict = None):
        """시스템 로그 저장"""
        try:
            log_data = {
                "event_type": event_type,
                "message": message,
                "level": level,
                "metadata": metadata or {},
                "timestamp": asyncio.get_event_loop().time()
            }
            
            result = await self.db.system_logs.insert_one(log_data)
            logger.info(f"시스템 로그 저장 완료: {result.inserted_id}")
            # ObjectId를 문자열로 변환하여 반환
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"시스템 로그 저장 실패: {str(e)}")
            return None
    
    async def get_interactions_by_condition(self, condition: Dict) -> List[Dict]:
        """조건에 따른 상호작용 검색"""
        try:
            cursor = self.db.user_interactions.find(condition).sort("timestamp", -1).limit(20)
            interactions = await cursor.to_list(length=20)
            return interactions
            
        except Exception as e:
            logger.error(f"조건별 상호작용 검색 실패: {str(e)}")
            return []
    
    async def search_memories(self, user_id: str, query: str, search_type: str = "keyword") -> List[Dict]:
        """메모리 검색"""
        try:
            search_conditions = []
            
            if search_type == "keyword":
                # 키워드 기반 검색
                search_conditions.append({
                    "user_id": user_id,
                    "$or": [
                        {"user_input": {"$regex": query, "$options": "i"}},
                        {"ai_response": {"$regex": query, "$options": "i"}}
                    ]
                })
            elif search_type == "emotion":
                # 감정 기반 검색
                search_conditions.append({
                    "user_id": user_id,
                    "metadata.emotion": {"$regex": query, "$options": "i"}
                })
            elif search_type == "context":
                # 맥락 기반 검색
                search_conditions.append({
                    "user_id": user_id,
                    "metadata.context": {"$regex": query, "$options": "i"}
                })
            else:
                # 종합 검색
                search_conditions.append({
                    "user_id": user_id,
                    "$or": [
                        {"user_input": {"$regex": query, "$options": "i"}},
                        {"ai_response": {"$regex": query, "$options": "i"}},
                        {"metadata.emotion": {"$regex": query, "$options": "i"}},
                        {"metadata.context": {"$regex": query, "$options": "i"}}
                    ]
                })
            
            all_results = []
            for condition in search_conditions:
                cursor = self.db.user_interactions.find(condition).sort("timestamp", -1).limit(10)
                results = await cursor.to_list(length=10)
                all_results.extend(results)
            
            # 중복 제거
            seen_ids = set()
            unique_results = []
            for result in all_results:
                if str(result["_id"]) not in seen_ids:
                    seen_ids.add(str(result["_id"]))
                    unique_results.append(result)
            
            return unique_results[:20]  # 최대 20개 반환
            
        except Exception as e:
            logger.error(f"메모리 검색 실패: {str(e)}")
            return []
    
    async def get_user_memory_stats(self, user_id: str) -> Dict:
        """사용자 메모리 통계"""
        try:
            # 사용자별 통계
            user_interactions = await self.db.user_interactions.count_documents({"user_id": user_id})
            user_consciousness_events = await self.db.consciousness_events.count_documents({"user_id": user_id})
            
            # 감정별 통계
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": "$metadata.emotion", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            emotion_stats = await self.db.user_interactions.aggregate(pipeline).to_list(length=10)
            
            # 최근 메모리
            cursor = self.db.user_interactions.find({"user_id": user_id}).sort("timestamp", -1).limit(10)
            recent_memories = await cursor.to_list(length=10)
            
            return {
                "user_id": user_id,
                "total_interactions": user_interactions,
                "total_consciousness_events": user_consciousness_events,
                "emotion_stats": emotion_stats,
                "recent_memories": recent_memories
            }
            
        except Exception as e:
            logger.error(f"사용자 메모리 통계 조회 실패: {str(e)}")
            return {"error": str(e)}
    
    # 사용자 관리 메서드들
    async def create_user(self, user_data: Dict) -> str:
        if not self.is_connected or self.db is None:
            logger.error("DB 연결이 되어 있지 않습니다.")
            return None
        """사용자 생성"""
        try:
            result = await self.db.users.insert_one(user_data)
            logger.info(f"사용자 생성 완료: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"사용자 생성 실패: {str(e)}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[Dict]:
        """사용자명으로 사용자 조회"""
        if not self.is_connected or self.db is None:
            logger.error("DB 연결이 되어 있지 않습니다.")
            return None
        try:
            user = await self.db.users.find_one({"username": username})
            return user
        except Exception as e:
            logger.error(f"사용자 조회 실패: {str(e)}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """사용자 ID로 사용자 조회"""
        if not self.is_connected or self.db is None:
            logger.error("DB 연결이 되어 있지 않습니다.")
            return None
        try:
            from bson import ObjectId
            user = await self.db.users.find_one({"_id": ObjectId(user_id)})
            return user
        except Exception as e:
            logger.error(f"사용자 조회 실패: {str(e)}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """이메일로 사용자 조회"""
        if not self.is_connected or self.db is None:
            logger.error("DB 연결이 되어 있지 않습니다.")
            return None
        try:
            user = await self.db.users.find_one({"email": email})
            if user and "_id" in user:
                user["_id"] = str(user["_id"])
            return user
        except Exception as e:
            logger.error(f"이메일로 사용자 조회 실패: {str(e)}")
            return None
    
    async def get_all_users(self) -> List[Dict]:
        if not self.is_connected or self.db is None:
            logger.error("DB 연결이 되어 있지 않습니다.")
            return []
        try:
            cursor = self.db.users.find({})
            users = await cursor.to_list(length=100)
            return self._convert_objectid_to_str(users)
        except Exception as e:
            logger.error(f"사용자 목록 조회 실패: {str(e)}")
            return []
    
    async def update_user_last_login(self, user_id: str):
        """사용자 마지막 로그인 시간 업데이트"""
        try:
            from bson import ObjectId
            await self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"last_login": asyncio.get_event_loop().time()}}
            )
        except Exception as e:
            logger.error(f"사용자 로그인 시간 업데이트 실패: {str(e)}")
    
    async def delete_user(self, user_id: str):
        """사용자 삭제"""
        try:
            from bson import ObjectId
            await self.db.users.delete_one({"_id": ObjectId(user_id)})
            logger.info(f"사용자 삭제 완료: {user_id}")
        except Exception as e:
            logger.error(f"사용자 삭제 실패: {str(e)}")
            raise
    
    async def get_user_statistics(self, user_id: str) -> Dict:
        """사용자 통계 조회"""
        try:
            from bson import ObjectId
            
            # 사용자 정보
            user = await self.get_user_by_id(user_id)
            if not user:
                return {"error": "사용자를 찾을 수 없습니다."}
            
            # 상호작용 통계
            interaction_count = await self.db.user_interactions.count_documents({"user_id": user_id})
            
            # 의식 이벤트 통계
            consciousness_stats = await self.get_consciousness_stats(user_id)
            
            # 세션 통계
            session_count = await self.db.sessions.count_documents({"user_id": user_id})
            
            return {
                "user": user,
                "interaction_count": interaction_count,
                "consciousness_stats": consciousness_stats,
                "session_count": session_count
            }
            
        except Exception as e:
            logger.error(f"사용자 통계 조회 실패: {str(e)}")
            return {"error": str(e)}
    
    # 세션 관리 메서드들
    async def create_session(self, session_data: Dict) -> str:
        if not self.is_connected or self.db is None:
            logger.error("DB 연결이 되어 있지 않습니다.")
            return None
        """세션 생성"""
        try:
            result = await self.db.sessions.insert_one(session_data)
            logger.info(f"세션 생성 완료: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"세션 생성 실패: {str(e)}")
            return None
    
    async def get_session_by_id(self, session_id: str) -> Optional[Dict]:
        """세션 ID로 세션 조회"""
        try:
            session = await self.db.sessions.find_one({"session_id": session_id})
            if session and "_id" in session:
                session["_id"] = str(session["_id"])
            return session
        except Exception as e:
            logger.error(f"세션 조회 실패: {str(e)}")
            return None
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """세션 조회"""
        try:
            session = await self.db.sessions.find_one({"session_id": session_id})
            if session and "_id" in session:
                session["_id"] = str(session["_id"])
            return session
        except Exception as e:
            logger.error(f"세션 조회 실패: {str(e)}")
            return None
    
    async def remove_session(self, session_id: str):
        """세션 삭제"""
        try:
            await self.db.sessions.delete_one({"session_id": session_id})
            logger.info(f"세션 삭제 완료: {session_id}")
        except Exception as e:
            logger.error(f"세션 삭제 실패: {str(e)}")
    
    async def get_user_sessions(self, user_id: str) -> List[Dict]:
        """사용자의 세션 목록 조회"""
        try:
            cursor = self.db.sessions.find({"user_id": user_id}).sort("created_at", -1)
            sessions = await cursor.to_list(length=50)
            
            # ObjectId를 문자열로 변환
            return self._convert_objectid_to_str(sessions)
        except Exception as e:
            logger.error(f"사용자 세션 목록 조회 실패: {str(e)}")
            return []

    async def get_sessions(self, query: Dict = None) -> List[Dict]:
        if not self.is_connected or self.db is None:
            logger.error("DB 연결이 되어 있지 않습니다.")
            return []
        try:
            filter_query = query or {}
            cursor = self.db.sessions.find(filter_query).sort("created_at", -1)
            sessions = await cursor.to_list(length=100)
            return sessions
        except Exception as e:
            logger.error(f"세션 목록 조회 실패: {str(e)}")
            return []
    
    async def save_message(self, session_id: str, sender: str, content: str, timestamp: str = None) -> str:
        if not self.is_connected or self.db is None:
            logger.error("DB 연결이 되어 있지 않습니다.")
            return None
        """메시지 저장"""
        try:
            message_data = {
                "session_id": session_id,
                "content": content,
                "sender": sender,
                "timestamp": timestamp or asyncio.get_event_loop().time()
            }
            
            result = await self.db.messages.insert_one(message_data)
            logger.info(f"메시지 저장 완료: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"메시지 저장 실패: {str(e)}")
            return None
    
    async def get_session_messages(self, session_id: str) -> List[Dict]:
        if not self.is_connected or self.db is None:
            logger.error("DB 연결이 되어 있지 않습니다.")
            return []
        try:
            cursor = self.db.messages.find({"session_id": session_id}).sort("timestamp", 1)
            messages = await cursor.to_list(length=100)
            logger.info(f"세션 메시지 조회 성공: {session_id} - {len(messages)}개 메시지")
            return messages
        except Exception as e:
            logger.error(f"세션 메시지 조회 실패: {str(e)}")
            return []
    
    async def update_session(self, session_id: str, update_data: Dict):
        """세션 업데이트"""
        try:
            await self.db.sessions.update_one(
                {"session_id": session_id},
                {"$set": update_data}
            )
            logger.info(f"세션 업데이트 완료: {session_id}")
        except Exception as e:
            logger.error(f"세션 업데이트 실패: {str(e)}")
            raise
    
    async def store_aura_data(self, user_id: str, aura_data: Dict) -> str:
        """아우라 데이터 저장"""
        try:
            aura_data["user_id"] = user_id
            aura_data["timestamp"] = asyncio.get_event_loop().time()
            
            result = await self.db.user_interactions.insert_one(aura_data)
            logger.info(f"아우라 데이터 저장 완료: {result.inserted_id}")
            # ObjectId를 문자열로 변환하여 반환
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"아우라 데이터 저장 실패: {str(e)}")
            raise
    
    async def _create_default_admin(self):
        """기본 관리자 계정 생성"""
        try:
            # 기존 관리자 확인
            admin = await self.get_user_by_username("admin")
            if admin:
                logger.info("기본 관리자 계정이 이미 존재합니다.")
                return
            
            # 기본 관리자 계정 생성
            import hashlib
            admin_data = {
                "username": "admin",
                "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
                "email": "admin@eora.ai",
                "is_admin": True,
                "created_at": asyncio.get_event_loop().time(),
                "last_login": None,
                "session_count": 0,
                "total_interactions": 0
            }
            
            await self.create_user(admin_data)
            logger.info("기본 관리자 계정이 생성되었습니다. (username: admin, password: admin123)")
            
        except Exception as e:
            logger.error(f"기본 관리자 계정 생성 실패: {str(e)}")

# 전역 데이터베이스 매니저 인스턴스
try:
    db_manager = DatabaseManager()
except Exception as e:
    logger.error(f"DatabaseManager 초기화 실패: {e}")
    db_manager = None 