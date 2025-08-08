import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import asyncio
from dataclasses import dataclass
from enum import Enum

try:
    import pymongo
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class StorageType(Enum):
    """저장소 타입"""
    CHAT = "chat"
    MEMORY = "memory"
    FILE = "file"
    CACHE = "cache"

@dataclass
class StorageQuota:
    """사용자별 저장공간 할당량"""
    user_id: str
    total_quota_mb: int = 100  # 기본 100MB로 변경
    used_mb: int = 0
    chat_used_mb: int = 0
    memory_used_mb: int = 0
    file_used_mb: int = 0
    cache_used_mb: int = 0
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    @property
    def available_mb(self) -> int:
        """사용 가능한 저장공간 (MB)"""
        return max(0, self.total_quota_mb - self.used_mb)
    
    @property
    def usage_percentage(self) -> float:
        """사용률 (%)"""
        if self.total_quota_mb == 0:
            return 0.0
        return (self.used_mb / self.total_quota_mb) * 100
    
    @property
    def is_full(self) -> bool:
        """저장공간이 가득 찼는지 확인"""
        return self.used_mb >= self.total_quota_mb
    
    @property
    def is_warning(self) -> bool:
        """95MB 이상 경고 구간 진입 여부"""
        return self.used_mb >= (self.total_quota_mb * 0.95)

class StorageManager:
    """사용자별 저장공간 관리 시스템"""
    
    def __init__(self, mongo_client=None, redis_client=None):
        self.mongo_client = mongo_client
        self.redis_client = redis_client
        self.db = None
        self.users_collection = None
        self.chat_collection = None
        self.memory_collection = None
        self.storage_quota_collection = None
        self.system_stats_collection = None
        
        if MONGO_AVAILABLE and mongo_client:
            self._setup_mongo_collections()
        
        if REDIS_AVAILABLE and redis_client:
            self._setup_redis()
    
    def _setup_mongo_collections(self):
        """MongoDB 컬렉션 설정"""
        try:
            self.db = self.mongo_client.eora_ai_storage
            self.users_collection = self.db.users
            self.chat_collection = self.db.user_chats
            self.memory_collection = self.db.user_memories
            self.storage_quota_collection = self.db.storage_quotas
            self.system_stats_collection = self.db.system_stats
            
            # 인덱스 생성
            self._create_indexes()
            print("✅ MongoDB 저장소 컬렉션 설정 완료")
        except Exception as e:
            print(f"❌ MongoDB 저장소 설정 실패: {e}")
    
    def _setup_redis(self):
        """Redis 설정"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                print("✅ Redis 연결 확인 완료")
        except Exception as e:
            print(f"⚠️ Redis 연결 실패: {e}")
    
    def _create_indexes(self):
        """MongoDB 인덱스 생성"""
        try:
            # 사용자별 채팅 인덱스
            if self.chat_collection is not None:
                self.chat_collection.create_index([
                    ("user_id", pymongo.ASCENDING),
                    ("session_id", pymongo.ASCENDING),
                    ("timestamp", pymongo.DESCENDING)
                ])
            
            # 사용자별 메모리 인덱스
            if self.memory_collection is not None:
                self.memory_collection.create_index([
                    ("user_id", pymongo.ASCENDING),
                    ("memory_type", pymongo.ASCENDING),
                    ("created_at", pymongo.DESCENDING)
                ])
            
            # 저장공간 할당량 인덱스
            if self.storage_quota_collection is not None:
                self.storage_quota_collection.create_index([
                    ("user_id", pymongo.ASCENDING)
                ], unique=True)
            
            # 시스템 통계 인덱스
            if self.system_stats_collection is not None:
                self.system_stats_collection.create_index([
                    ("date", pymongo.ASCENDING)
                ])
            
            print("✅ MongoDB 인덱스 생성 완료")
        except Exception as e:
            print(f"⚠️ 인덱스 생성 실패: {e}")
    
    async def get_user_storage_quota(self, user_id: str) -> StorageQuota:
        """사용자 저장공간 할당량 조회"""
        try:
            if self.storage_quota_collection is None:
                return StorageQuota(user_id=user_id)
            
            # Redis 캐시 확인
            cache_key = f"storage_quota:{user_id}"
            if REDIS_AVAILABLE and self.redis_client:
                cached = self.redis_client.get(cache_key)
                if cached:
                    data = json.loads(cached)
                    return StorageQuota(**data)
            
            # MongoDB에서 조회
            quota_data = self.storage_quota_collection.find_one({"user_id": user_id})
            
            if quota_data:
                quota = StorageQuota(
                    user_id=quota_data["user_id"],
                    total_quota_mb=quota_data.get("total_quota_mb", 100),
                    used_mb=quota_data.get("used_mb", 0),
                    chat_used_mb=quota_data.get("chat_used_mb", 0),
                    memory_used_mb=quota_data.get("memory_used_mb", 0),
                    file_used_mb=quota_data.get("file_used_mb", 0),
                    cache_used_mb=quota_data.get("cache_used_mb", 0),
                    created_at=quota_data.get("created_at", datetime.now()),
                    updated_at=quota_data.get("updated_at", datetime.now())
                )
            else:
                # 새 사용자: 기본 할당량 생성
                quota = StorageQuota(user_id=user_id)
                await self.create_user_storage_quota(quota)
            
            # Redis 캐시 저장 (5분)
            if REDIS_AVAILABLE and self.redis_client:
                self.redis_client.setex(
                    cache_key, 
                    300, 
                    json.dumps(quota.__dict__, default=str)
                )
            
            return quota
            
        except Exception as e:
            print(f"❌ 저장공간 할당량 조회 실패: {e}")
            return StorageQuota(user_id=user_id)
    
    async def create_user_storage_quota(self, quota: StorageQuota) -> bool:
        """사용자 저장공간 할당량 생성"""
        try:
            if self.storage_quota_collection is None:
                return False
            
            quota_data = {
                "user_id": quota.user_id,
                "total_quota_mb": quota.total_quota_mb,
                "used_mb": quota.used_mb,
                "chat_used_mb": quota.chat_used_mb,
                "memory_used_mb": quota.memory_used_mb,
                "file_used_mb": quota.file_used_mb,
                "cache_used_mb": quota.cache_used_mb,
                "created_at": quota.created_at,
                "updated_at": quota.updated_at
            }
            
            self.storage_quota_collection.insert_one(quota_data)
            
            # Redis 캐시 무효화
            if REDIS_AVAILABLE and self.redis_client:
                cache_key = f"storage_quota:{quota.user_id}"
                self.redis_client.delete(cache_key)
            
            print(f"✅ 사용자 저장공간 할당량 생성: {quota.user_id}")
            return True
            
        except Exception as e:
            print(f"❌ 저장공간 할당량 생성 실패: {e}")
            return False
    
    async def update_storage_usage(self, user_id: str, storage_type: StorageType, size_mb: float) -> bool:
        """저장공간 사용량 업데이트"""
        try:
            if self.storage_quota_collection is None:
                return False
            
            # 현재 할당량 조회
            quota = await self.get_user_storage_quota(user_id)
            
            # 사용량 업데이트
            update_data = {
                "updated_at": datetime.now()
            }
            
            if storage_type == StorageType.CHAT:
                quota.chat_used_mb += size_mb
                update_data["chat_used_mb"] = quota.chat_used_mb
            elif storage_type == StorageType.MEMORY:
                quota.memory_used_mb += size_mb
                update_data["memory_used_mb"] = quota.memory_used_mb
            elif storage_type == StorageType.FILE:
                quota.file_used_mb += size_mb
                update_data["file_used_mb"] = quota.file_used_mb
            elif storage_type == StorageType.CACHE:
                quota.cache_used_mb += size_mb
                update_data["cache_used_mb"] = quota.cache_used_mb
            
            # 총 사용량 계산
            quota.used_mb = quota.chat_used_mb + quota.memory_used_mb + quota.file_used_mb + quota.cache_used_mb
            update_data["used_mb"] = quota.used_mb
            
            # MongoDB 업데이트
            self.storage_quota_collection.update_one(
                {"user_id": user_id},
                {"$set": update_data},
                upsert=True
            )
            
            # Redis 캐시 무효화
            if REDIS_AVAILABLE and self.redis_client:
                cache_key = f"storage_quota:{user_id}"
                self.redis_client.delete(cache_key)
            
            print(f"✅ 저장공간 사용량 업데이트: {user_id} - {storage_type.value} +{size_mb}MB")
            return True
            
        except Exception as e:
            print(f"❌ 저장공간 사용량 업데이트 실패: {e}")
            return False
    
    async def check_storage_available(self, user_id: str, required_mb: float) -> Tuple[bool, str, bool]:
        """저장공간 사용 가능 여부 확인 (경고 상태 포함)"""
        try:
            quota = await self.get_user_storage_quota(user_id)
            warning = quota.is_warning
            if quota.available_mb >= required_mb:
                if warning:
                    return True, f"경고: 저장공간이 95% 이상 사용 중입니다. (남은 용량: {quota.available_mb:.1f}MB)", True
                else:
                    return True, f"사용 가능: {quota.available_mb:.1f}MB", False
            else:
                return False, f"저장공간 부족: 필요 {required_mb}MB, 사용가능 {quota.available_mb:.1f}MB", warning
        except Exception as e:
            print(f"❌ 저장공간 확인 실패: {e}")
            return False, "저장공간 확인 실패", False
    
    async def expand_storage_quota(self, user_id: str, additional_mb: int) -> bool:
        """저장공간 확장"""
        try:
            if self.storage_quota_collection is None:
                return False
            
            result = self.storage_quota_collection.update_one(
                {"user_id": user_id},
                {
                    "$inc": {"total_quota_mb": additional_mb},
                    "$set": {"updated_at": datetime.now()}
                }
            )
            
            if result.modified_count > 0:
                # Redis 캐시 무효화
                if REDIS_AVAILABLE and self.redis_client:
                    cache_key = f"storage_quota:{user_id}"
                    self.redis_client.delete(cache_key)
                
                print(f"✅ 저장공간 확장 완료: {user_id} +{additional_mb}MB")
                return True
            else:
                print(f"⚠️ 저장공간 확장 실패: 사용자를 찾을 수 없음 - {user_id}")
                return False
                
        except Exception as e:
            print(f"❌ 저장공간 확장 실패: {e}")
            return False
    
    async def save_chat_message(self, user_id: str, message: str, response: str, session_id: str = "default") -> Tuple[bool, str, bool]:
        """채팅 메시지 저장 (저장공간 관리 포함, 경고 반환)"""
        try:
            if self.chat_collection is None:
                return False, "DB 연결 오류", False
            message_size_mb = (len(message.encode('utf-8')) + len(response.encode('utf-8'))) / (1024 * 1024)
            available, msg, warning = await self.check_storage_available(user_id, message_size_mb)
            if not available:
                print(f"⚠️ 저장공간 부족으로 채팅 저장 실패: {user_id}")
                return False, msg, warning
            chat_data = {
                "user_id": user_id,
                "session_id": session_id,
                "message": message,
                "response": response,
                "timestamp": datetime.now(),
                "size_mb": message_size_mb
            }
            self.chat_collection.insert_one(chat_data)
            await self.update_storage_usage(user_id, StorageType.CHAT, message_size_mb)
            print(f"✅ 채팅 메시지 저장 완료: {user_id} - {session_id}")
            return True, msg, warning
        except Exception as e:
            print(f"❌ 채팅 메시지 저장 실패: {e}")
            return False, "저장 실패", False
    
    async def save_memory(self, user_id: str, memory_data: dict, memory_type: str = "general") -> Tuple[bool, str, bool]:
        """메모리 저장 (저장공간 관리 포함, 경고 반환)"""
        try:
            if self.memory_collection is None:
                return False, "DB 연결 오류", False
            memory_size_mb = len(json.dumps(memory_data, ensure_ascii=False).encode('utf-8')) / (1024 * 1024)
            available, msg, warning = await self.check_storage_available(user_id, memory_size_mb)
            if not available:
                print(f"⚠️ 저장공간 부족으로 메모리 저장 실패: {user_id}")
                return False, msg, warning
            memory_record = {
                "user_id": user_id,
                "memory_type": memory_type,
                "memory_data": memory_data,
                "created_at": datetime.now(),
                "size_mb": memory_size_mb
            }
            self.memory_collection.insert_one(memory_record)
            await self.update_storage_usage(user_id, StorageType.MEMORY, memory_size_mb)
            print(f"✅ 메모리 저장 완료: {user_id} - {memory_type}")
            return True, msg, warning
        except Exception as e:
            print(f"❌ 메모리 저장 실패: {e}")
            return False, "저장 실패", False
    
    async def get_user_chats(self, user_id: str, session_id: str = None, limit: int = 100) -> List[Dict]:
        """사용자 채팅 내역 조회"""
        try:
            if self.chat_collection is None:
                return []
            
            query = {"user_id": user_id}
            if session_id:
                query["session_id"] = session_id
            
            cursor = self.chat_collection.find(query).sort("timestamp", -1).limit(limit)
            chats = list(cursor)
            
            # ObjectId를 문자열로 변환
            for chat in chats:
                chat["_id"] = str(chat["_id"])
                chat["timestamp"] = chat["timestamp"].isoformat()
            
            return chats
            
        except Exception as e:
            print(f"❌ 채팅 내역 조회 실패: {e}")
            return []
    
    async def get_user_memories(self, user_id: str, memory_type: str = None, limit: int = 100) -> List[Dict]:
        """사용자 메모리 조회"""
        try:
            if self.memory_collection is None:
                return []
            
            query = {"user_id": user_id}
            if memory_type:
                query["memory_type"] = memory_type
            
            cursor = self.memory_collection.find(query).sort("created_at", -1).limit(limit)
            memories = list(cursor)
            
            # ObjectId를 문자열로 변환
            for memory in memories:
                memory["_id"] = str(memory["_id"])
                memory["created_at"] = memory["created_at"].isoformat()
            
            return memories
            
        except Exception as e:
            print(f"❌ 메모리 조회 실패: {e}")
            return []
    
    async def get_system_storage_stats(self) -> Dict:
        """시스템 전체 저장공간 통계 (관리자용)"""
        try:
            if self.storage_quota_collection is None:
                return {}
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_users": {"$sum": 1},
                        "total_quota_mb": {"$sum": "$total_quota_mb"},
                        "total_used_mb": {"$sum": "$used_mb"},
                        "total_chat_mb": {"$sum": "$chat_used_mb"},
                        "total_memory_mb": {"$sum": "$memory_used_mb"},
                        "total_file_mb": {"$sum": "$file_used_mb"},
                        "total_cache_mb": {"$sum": "$cache_used_mb"}
                    }
                }
            ]
            result = list(self.storage_quota_collection.aggregate(pipeline))
            if result:
                stats = result[0]
                stats["usage_percentage"] = (stats["total_used_mb"] / stats["total_quota_mb"] * 100) if stats["total_quota_mb"] > 0 else 0
                stats["available_mb"] = stats["total_quota_mb"] - stats["total_used_mb"]
                return {
                    "total_users": stats["total_users"],
                    "total_quota_mb": stats["total_quota_mb"],
                    "total_used_mb": stats["total_used_mb"],
                    "available_mb": stats["available_mb"],
                    "usage_percentage": stats["usage_percentage"],
                    "total_chat_mb": stats["total_chat_mb"],
                    "total_memory_mb": stats["total_memory_mb"],
                    "total_file_mb": stats["total_file_mb"],
                    "total_cache_mb": stats["total_cache_mb"]
                }
            else:
                return {
                    "total_users": 0,
                    "total_quota_mb": 0,
                    "total_used_mb": 0,
                    "available_mb": 0,
                    "usage_percentage": 0,
                    "total_chat_mb": 0,
                    "total_memory_mb": 0,
                    "total_file_mb": 0,
                    "total_cache_mb": 0
                }
        except Exception as e:
            print(f"❌ 시스템 저장공간 통계 조회 실패: {e}")
            return {}
    
    async def get_top_storage_users(self, limit: int = 10) -> List[Dict]:
        """저장공간 사용량 상위 사용자"""
        try:
            if self.storage_quota_collection is None:
                return []
            
            cursor = self.storage_quota_collection.find().sort("used_mb", -1).limit(limit)
            users = list(cursor)
            
            # ObjectId를 문자열로 변환
            for user in users:
                user["_id"] = str(user["_id"])
                user["usage_percentage"] = (user["used_mb"] / user["total_quota_mb"] * 100) if user["total_quota_mb"] > 0 else 0
                user["available_mb"] = user["total_quota_mb"] - user["used_mb"]
            
            return users
            
        except Exception as e:
            print(f"❌ 상위 사용자 조회 실패: {e}")
            return []
    
    async def cleanup_old_data(self, days: int = 30) -> int:
        """오래된 데이터 정리"""
        try:
            if self.chat_collection is None or self.memory_collection is None:
                return 0
            
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = 0
            
            # 오래된 채팅 삭제
            chat_result = self.chat_collection.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            deleted_count += chat_result.deleted_count
            
            # 오래된 메모리 삭제
            memory_result = self.memory_collection.delete_many({
                "created_at": {"$lt": cutoff_date}
            })
            deleted_count += memory_result.deleted_count
            
            print(f"✅ 오래된 데이터 정리 완료: {deleted_count}개 삭제")
            return deleted_count
            
        except Exception as e:
            print(f"❌ 데이터 정리 실패: {e}")
            return 0

# 전역 저장소 관리자 인스턴스
storage_manager = None

def get_storage_manager(mongo_client=None, redis_client=None) -> StorageManager:
    """저장소 관리자 인스턴스 반환"""
    global storage_manager
    if storage_manager is None:
        storage_manager = StorageManager(mongo_client, redis_client)
    return storage_manager 