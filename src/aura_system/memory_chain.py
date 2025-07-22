"""
memory_chain.py
- 메모리 체인 관리
- 체인 생성, 조회, 업데이트, 삭제
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import numpy as np
from redis.asyncio import Redis
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, OperationFailure
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.objectid import ObjectId
from dotenv import load_dotenv
from pathlib import Path

# 상대 경로 임포트
from .config import get_config
from .memory_structurer import MemoryAtom
from .embeddings import get_embeddings
from .vector_store import get_vector_store

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ 환경 설정 로드 및 MongoDB 연결
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
REDIS_URI = os.getenv("REDIS_URI", "redis://localhost:6379")
DB_NAME = os.getenv("MONGO_DB", "aura_memory")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["memory_chains"]

# Redis 클라이언트 초기화
redis_client = Redis.from_url(REDIS_URI)

MEMORY_CHAIN_JSON_PATH = Path(__file__).parent.parent / "memory" / "memory_chain_db.json"

class MemoryChain:
    """메모리 체인 관리 클래스"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.config = get_config()
            self._redis_client = None
            self._mongo_client = None
            self._initialized = True
    
    async def initialize(self):
        """비동기 초기화"""
        try:
            # MongoDB 클라이언트 초기화
            mongo_config = self.config.get("mongodb", {})
            self._mongo_client = AsyncIOMotorClient(
                mongo_config.get("uri", os.getenv("MONGODB_URI", "mongodb://localhost:27017")),
                maxPoolSize=mongo_config.get("max_pool_size", 100),
                minPoolSize=mongo_config.get("min_pool_size", 10)
            )
            self._db = self._mongo_client[mongo_config.get("db_name", "aura_db")]
            
            # Redis 클라이언트 초기화
            redis_config = self.config.get("redis", {})
            self._redis_client = Redis(
                host=redis_config.get("host", "localhost"),
                port=redis_config.get("port", 6379),
                db=redis_config.get("db", 0),
                decode_responses=True
            )
            
            # 임베딩과 벡터 스토어 초기화
            self.embeddings = await get_embeddings()
            self.vector_store = await get_vector_store()
            
            # 인덱스 생성
            await self._create_indexes()
            
            logger.info("✅ 메모리 체인 저장소 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ 초기화 실패: {str(e)}")
            raise
            
    async def _create_indexes(self):
        try:
            # memory_chains 컬렉션 인덱스
            await self._db.memory_chains.create_index([("chain_id", ASCENDING)], unique=True)
            await self._db.memory_chains.create_index([("metadata.tags", ASCENDING)])
            await self._db.memory_chains.create_index([("metadata.timestamp", DESCENDING)])
            await self._db.memory_chains.create_index([("metadata.importance", DESCENDING)])
            await self._db.memory_chains.create_index([("metadata.type", ASCENDING)])
            
            # 복합 인덱스
            await self._db.memory_chains.create_index([
                ("metadata.tags", ASCENDING),
                ("metadata.timestamp", DESCENDING)
            ])
            
            logger.info("✅ 인덱스 생성 완료")
            
        except Exception as e:
            logger.error(f"❌ 인덱스 생성 실패: {str(e)}")
            raise
            
    async def create_chain(
        self,
        memories: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
        prev_chain_id: Optional[str] = None
    ) -> Optional[str]:
        try:
            if not memories:
                return None
            
            # 체인 ID 생성
            chain_id = f"chain_{datetime.utcnow().timestamp()}"

            # 이전 체인 요약 불러오기
            prev_summary = ""
            if prev_chain_id:
                prev_chain = await self.get_chain(prev_chain_id)
                if prev_chain and "summary" in prev_chain:
                    prev_summary = prev_chain["summary"]

            # 이번 10턴 요약 생성 (예시: memories의 content 합치기)
            this_summary = "\n".join([m.get("content", "") for m in memories])
            # 최종 요약: 이전 요약 + 이번 요약
            final_summary = (prev_summary + "\n" if prev_summary else "") + this_summary

            # 메타데이터 구조화
            structured_metadata = self._structure_metadata(chain_id, metadata or {})

            # 체인 문서 생성
            chain_doc = {
                "chain_id": chain_id,
                "prev_chain_id": prev_chain_id,
                "summary": final_summary,
                "memories": memories,
                "metadata": structured_metadata,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            # MongoDB에 저장
            result = await self._db.memory_chains.insert_one(chain_doc)
            if not result.inserted_id:
                return None

            # Redis 캐시 업데이트
            await self._cache_chain(chain_id, chain_doc)

            return chain_id

        except Exception as e:
            logger.error(f"❌ 체인 생성 실패: {str(e)}")
            return None
            
    async def get_chain(
        self,
        chain_id: str,
        use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        try:
            if not chain_id:
                return None
                
            # 캐시 확인
            if use_cache:
                cached_chain = await self._get_cached_chain(chain_id)
                if cached_chain:
                    return cached_chain
                    
            # MongoDB에서 조회
            chain = await self._db.memory_chains.find_one({"chain_id": chain_id})
            if not chain:
                return None
                
            # 캐시 업데이트
            if use_cache:
                await self._cache_chain(chain_id, chain)
                
            return chain
            
        except Exception as e:
            logger.error(f"❌ 체인 조회 실패: {str(e)}")
            return None
            
    async def update_chain(
        self,
        chain_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        try:
            if not chain_id or not updates:
                return False
                
            # 업데이트 문서 생성
            update_doc = {
                "$set": {
                    "metadata": updates,
                    "updated_at": datetime.utcnow()
                }
            }
            
            # MongoDB 업데이트
            result = await self._db.memory_chains.update_one(
                {"chain_id": chain_id},
                update_doc
            )
            
            if result.modified_count == 0:
                return False
                
            # Redis 캐시 무효화
            await self._invalidate_cache(chain_id)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 체인 업데이트 실패: {str(e)}")
            return False
            
    async def delete_chain(self, chain_id: str) -> bool:
        try:
            if not chain_id:
                return False
                
            # MongoDB에서 삭제
            result = await self._db.memory_chains.delete_one({"chain_id": chain_id})
            
            if result.deleted_count == 0:
                return False
                
            # Redis 캐시 무효화
            await self._invalidate_cache(chain_id)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 체인 삭제 실패: {str(e)}")
            return False
            
    def _structure_metadata(
        self,
        chain_id: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            # 기본 메타데이터
            structured_metadata = {
                "chain_id": chain_id,
                "timestamp": datetime.utcnow().timestamp(),
                "type": metadata.get("type", "default"),
                "importance": metadata.get("importance", 0.5),
                "tags": metadata.get("tags", []),
                "emotion": metadata.get("emotion", {}),
                "context": metadata.get("context", {}),
                "source": metadata.get("source", "system")
            }
            
            return structured_metadata
            
        except Exception as e:
            logger.error(f"❌ 메타데이터 구조화 실패: {str(e)}")
            return {}
            
    async def _cache_chain(
        self,
        chain_id: str,
        chain_data: Dict[str, Any],
        ttl: Optional[int] = None
    ):
        try:
            # Redis에 체인 캐시
            await self._redis_client.setex(
                f"chain:{chain_id}",
                ttl or 3600,  # 기본 1시간 TTL
                json.dumps(chain_data)
            )
            
        except Exception as e:
            logger.error(f"❌ 체인 캐시 실패: {str(e)}")
            
    async def _get_cached_chain(self, chain_id: str) -> Optional[Dict[str, Any]]:
        try:
            # Redis에서 체인 조회
            cached_data = await self._redis_client.get(f"chain:{chain_id}")
            if cached_data:
                return json.loads(cached_data)
                
            return None
            
        except Exception as e:
            logger.error(f"❌ 캐시된 체인 조회 실패: {str(e)}")
            return None
            
    async def _invalidate_cache(self, chain_id: str):
        try:
            # Redis 캐시 삭제
            await self._redis_client.delete(f"chain:{chain_id}")
            
        except Exception as e:
            logger.error(f"❌ 캐시 무효화 실패: {str(e)}")
            
    async def cleanup(self):
        try:
            # 리소스 정리
            if hasattr(self, 'client'):
                self.client.close()
            if hasattr(self, 'redis'):
                await self.redis.close()
                
            logger.info("✅ 리소스 정리 완료")
            
        except Exception as e:
            logger.error(f"❌ 리소스 정리 실패: {str(e)}")

    def __del__(self):
        """소멸자"""
        if self._initialized:
            try:
                loop = asyncio.get_running_loop()
                if loop and loop.is_running():
                    asyncio.create_task(self.cleanup())
            except RuntimeError:
                pass

# 싱글톤 인스턴스
_memory_chain = None

async def get_memory_chain() -> MemoryChain:
    """메모리 체인 인스턴스를 가져옵니다."""
    instance = MemoryChain()
    if not instance._initialized:
        await instance.initialize()
    return instance

async def find_or_create_chain_id(text: str) -> str:
    """텍스트와 관련된 체인을 찾거나 새로 생성합니다."""
    memory_chain_manager = await get_memory_chain()
    
    # 임베딩 기반 유사 체인 검색 (이 기능은 vector_store에 구현되어야 함)
    # 여기서는 임시로 내용 기반 검색을 가정합니다.
    # chain_id = await memory_chain_manager.vector_store.search_similar_chains(text)
    
    # 임시 내용 기반 검색 (MongoDB 텍스트 검색 인덱스 필요)
    try:
        result = await memory_chain_manager._db.memory_chains.find_one({"$text": {"$search": text}})
        chain_id = result.get("chain_id") if result else None
    except Exception:
        chain_id = None # 텍스트 인덱스가 없거나 검색 실패 시

    if chain_id:
        logger.info(f"기존 체인을 찾았습니다: {chain_id}")
        return chain_id
    
    # 기존 체인이 없으면 새로 생성
    logger.info("기존 체인을 찾지 못해 새로 생성합니다.")
    new_chain_id = await memory_chain_manager.create_chain(
        memories=[{"content": text, "type": "seed"}],
        metadata={"source": "auto_find_or_create", "topic": text[:50]}
    )
    return new_chain_id or "default_chain_id" 