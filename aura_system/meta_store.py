"""
meta_store.py
- 메타데이터 저장소 구현
- MongoDB를 사용한 메타데이터 관리
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from pymongo import ASCENDING, DESCENDING
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

class Config:
    """설정 클래스"""
    
    def __init__(self):
        """초기화"""
        self.mongodb = {
            "uri": os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
            "db_name": os.getenv("MONGODB_DATABASE", "aura_system"),
            "collection": os.getenv("MONGODB_COLLECTION", "metadata")
        }
        
        self.redis = {
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PORT", 6379)),
            "db": int(os.getenv("REDIS_DB", 0))
        }
        
        self.vector_store = {
            "type": os.getenv("VECTOR_STORE_TYPE", "faiss"),
            "dimension": int(os.getenv("VECTOR_STORE_DIMENSION", 1536))
        }
        
        self.embeddings = {
            "model": os.getenv("EMBEDDINGS_MODEL", "text-embedding-ada-002"),
            "dimension": int(os.getenv("EMBEDDINGS_DIMENSION", 1536))
        }

class MetaStore:
    """메타데이터 저장소 클래스"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        if not self._initialized:
            self.config = Config()
            self.mongo_client = None
            self.redis_client = None
            self._initialized = True
            
    async def initialize(self):
        """비동기 초기화"""
        try:
            # MongoDB 클라이언트 초기화
            self.mongo_client = AsyncIOMotorClient(
                self.config.mongodb["uri"],
                serverSelectionTimeoutMS=5000
            )
            
            # Redis 클라이언트 초기화
            self.redis_client = aioredis.Redis(
                host=self.config.redis["host"],
                port=self.config.redis["port"],
                db=self.config.redis["db"],
                decode_responses=True
            )
            
            # 인덱스 생성
            await self._create_indexes()
            
            logger.info("✅ 메타데이터 저장소 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ 메타데이터 저장소 초기화 실패: {str(e)}")
            raise
            
    async def _create_indexes(self):
        """인덱스 생성"""
        try:
            db = self.mongo_client[self.config.mongodb["db_name"]]
            
            # metadata 컬렉션 인덱스
            await db.metadata.create_index([("memory_id", ASCENDING)], unique=True)
            await db.metadata.create_index([("tags", ASCENDING)])
            await db.metadata.create_index([("timestamp", DESCENDING)])
            await db.metadata.create_index([("type", ASCENDING)])
            
            # 복합 인덱스
            await db.metadata.create_index([
                ("tags", ASCENDING),
                ("timestamp", DESCENDING)
            ])
            
            logger.info("✅ 인덱스 생성 완료")
            
        except Exception as e:
            logger.error(f"❌ 인덱스 생성 실패: {str(e)}")
            raise
            
    async def store_metadata(
        self,
        memory_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """메타데이터 저장"""
        try:
            db = self.mongo_client[self.config.mongodb["db_name"]]
            
            # 메타데이터 저장
            await db.metadata.update_one(
                {"memory_id": memory_id},
                {"$set": {
                    "memory_id": memory_id,
                    **metadata,
                    "updated_at": datetime.utcnow()
                }},
                upsert=True
            )
            
            # Redis 캐시 업데이트
            cache_key = f"metadata:{memory_id}"
            await self.redis_client.set(
                cache_key,
                json.dumps(metadata, default=str),
                ex=3600  # 1시간 캐시
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 메타데이터 저장 실패: {str(e)}")
            return False
            
    async def get_metadata(
        self,
        memory_id: str
    ) -> Optional[Dict[str, Any]]:
        """메타데이터 조회"""
        try:
            # Redis 캐시 확인
            cache_key = f"metadata:{memory_id}"
            
            # 비동기 Redis 클라이언트의 get 메서드는 await 필요
            cached = await self.redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
                
            # MongoDB에서 조회
            db = self.mongo_client[self.config.mongodb["db_name"]]
            metadata = await db.metadata.find_one({"memory_id": memory_id})
            
            if metadata:
                # Redis 캐시 업데이트
                # MongoDB에서 받은 metadata에는 ObjectId 등이 포함될 수 있으므로 직렬화 가능한 형태로 변환 필요
                # 간단하게는 find_one 결과에서 _id를 str으로 변환하는 등의 처리가 필요하지만,
                # 여기서는 json.dumps의 default를 사용하여 처리.
                await self.redis_client.set(
                    cache_key,
                    json.dumps(metadata, default=str),
                    ex=3600
                )
                return metadata
                
            return None
            
        except Exception as e:
            logger.error(f"❌ 메타데이터 조회 실패: {str(e)}")
            return None
            
    async def update_metadata(
        self,
        memory_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """메타데이터 업데이트"""
        try:
            db = self.mongo_client[self.config.mongodb["db_name"]]
            
            # 메타데이터 업데이트
            result = await db.metadata.update_one(
                {"memory_id": memory_id},
                {"$set": {
                    **metadata,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            if result.modified_count > 0:
                # Redis 캐시 삭제
                cache_key = f"metadata:{memory_id}"
                await self.redis_client.delete(cache_key)
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"❌ 메타데이터 업데이트 실패: {str(e)}")
            return False
            
    async def delete_metadata(self, memory_id: str) -> bool:
        """메타데이터 삭제"""
        try:
            db = self.mongo_client[self.config.mongodb["db_name"]]
            
            # 메타데이터 삭제
            result = await db.metadata.delete_one({"memory_id": memory_id})
            
            if result.deleted_count > 0:
                # Redis 캐시 삭제
                cache_key = f"metadata:{memory_id}"
                await self.redis_client.delete(cache_key)
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"❌ 메타데이터 삭제 실패: {str(e)}")
            return False
            
    async def search_by_tags(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """태그 기반 검색"""
        try:
            db = self.mongo_client[self.config.mongodb["db_name"]]
            
            # 태그 추출
            tags = query.lower().split()
            
            # 태그 기반 검색
            cursor = db.metadata.find(
                {"tags": {"$in": tags}},
                sort=[("timestamp", DESCENDING)],
                limit=limit
            )
            
            return await cursor.to_list(length=limit)
            
        except Exception as e:
            logger.error(f"❌ 태그 검색 실패: {str(e)}")
            return []
            
    async def cleanup(self):
        """리소스 정리"""
        try:
            if self.mongo_client:
                self.mongo_client.close()
                
            if self.redis_client:
                await self.redis_client.close()
                
            logger.info("✅ 메타데이터 저장소 정리 완료")
            
        except Exception as e:
            logger.error(f"❌ 메타데이터 저장소 정리 실패: {str(e)}")
            
    def __del__(self):
        pass

    async def get_all_atoms(self, limit: int = 1000) -> list:
        """metadata 컬렉션의 모든 문서를 리스트로 반환합니다."""
        try:
            db = self.mongo_client[self.config.mongodb["db_name"]]
            cursor = db.metadata.find({}, limit=limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"❌ get_all_atoms 실패: {str(e)}")
            return []

    async def get_atoms_by_ids(self, ids: list, limit: int = 1000) -> list:
        """주어진 ids에 해당하는 metadata 컬렉션의 문서들을 리스트로 반환합니다."""
        if not ids:
            return []
        db = self.mongo_client[self.config.mongodb["db_name"]]
        cursor = db.metadata.find({"memory_id": {"$in": ids}}, limit=limit)
        return await cursor.to_list(length=limit)

# 싱글톤 인스턴스
_meta_store = None

async def get_meta_store() -> MetaStore:
    """메타데이터 저장소 인스턴스 반환"""
    global _meta_store
    if _meta_store is None:
        _meta_store = MetaStore()
        await _meta_store.initialize()
    return _meta_store

async def get_all_atoms(limit: int = 1000) -> list:
    """metadata 컬렉션의 모든 문서를 리스트로 반환합니다."""
    meta_store = await get_meta_store()
    return await meta_store.get_all_atoms(limit=limit)

async def get_atoms_by_ids(ids: list, limit: int = 1000) -> list:
    """주어진 ids에 해당하는 metadata 컬렉션의 문서들을 리스트로 반환합니다."""
    if not ids:
        return []
    meta_store = await get_meta_store()
    return await meta_store.get_atoms_by_ids(ids, limit=limit)
