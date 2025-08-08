
"""
memory_store.py
- 메모리 저장소 관리
- 메모리 생성, 조회, 업데이트, 삭제
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
from .vector_store import get_vector_store, FaissIndex

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
collection = db["memories"]

# Redis 클라이언트 초기화
redis_client = Redis.from_url(REDIS_URI)

MEMORY_JSON_PATH = Path(__file__).parent.parent / "memory" / "memory_db.json"

class MemoryStore:
    """메모리 저장소 관리 클래스"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, redis_manager=None, vector_store=None):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.config = get_config()
        self.embeddings = get_embeddings()
        self.vector_store = vector_store or get_vector_store()
        if self.vector_store is None:
            self.vector_store = FaissIndex()
            logger.warning("⚠️ vector_store가 None이어서 FaissIndex로 초기화함")
        self._redis_client = redis_manager or redis_client
        self._mongo_client = None
        self._initialized = False

    def _initialize(self):
        try:
            mongo_config = self.config.get("mongodb", {})
            self._mongo_client = AsyncIOMotorClient(
                mongo_config.get("uri", os.getenv("MONGODB_URI", "mongodb://localhost:27017")),
                maxPoolSize=mongo_config.get("max_pool_size", 100),
                minPoolSize=mongo_config.get("min_pool_size", 10)
            )
            self._db = self._mongo_client[mongo_config.get("db_name", "aura_db")]
            self._create_indexes()
            logger.info("✅ 메모리 저장소 초기화 완료")
        except Exception as e:
            logger.error(f"❌ 초기화 실패: {str(e)}")
            raise

    async def initialize(self):
        if not self._initialized:
            self._initialize()
            try:
                if self._redis_client:
                    await self._redis_client.ping()
            except Exception as e:
                logger.warning(f"⚠️ Redis 초기화 실패 또는 연결 문제: {e}")
            self._initialized = True
            logger.info("✅ 메모리 스토어 비동기 초기화 완료")

    def _create_indexes(self):
        try:
            self._db["memories"].create_index([("timestamp", DESCENDING)])
            self._db["memories"].create_index([("content", "text")])
        except Exception as e:
            logger.warning(f"⚠️ Mongo 인덱스 생성 실패: {e}")

    async def store_memory(self, key: str, value: Any, metadata: Optional[Dict] = None):
        try:
            doc = {
                "key": key,
                "value": value,
                "metadata": metadata or {},
                "timestamp": datetime.now()
            }
            await self._db["memories"].insert_one(doc)
            await self._redis_client.set(key, json.dumps(doc), ex=3600)
        except Exception as e:
            logger.error(f"❌ 메모리 저장 실패: {e}")

    async def recall_memory(self, key: str) -> Optional[Dict]:
        try:
            val = await self._redis_client.get(key)
            if val:
                return json.loads(val)

            # fallback to Mongo
            try:
                obj_id = ObjectId(key)
                doc = await self._db["memories"].find_one({"_id": obj_id})
            except:
                doc = await self._db["memories"].find_one({"key": key})

            if doc:
                await self._redis_client.set(key, json.dumps(doc), ex=3600)
            return doc
        except Exception as e:
            logger.error(f"❌ 메모리 회상 실패: {e}")
            return None

    async def cleanup(self):
        try:
            if self._redis_client:
                await self._redis_client.close()
            if self._mongo_client:
                self._mongo_client.close()
            logger.info("✅ MemoryStore 정리 완료")
        except Exception as e:
            logger.error(f"❌ 정리 실패: {e}")

def get_memory_store() -> MemoryStore:
    return MemoryStore()
