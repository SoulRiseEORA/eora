import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import numpy as np
from openai import AsyncOpenAI
from redis.asyncio import Redis

from .config import get_config

logger = logging.getLogger(__name__)

class Embeddings:
    def __init__(self):
        self.config = get_config()
        self._initialize()
        
    def _initialize(self):
        try:
            openai_config = self.config.get("openai", {})
            self.client = AsyncOpenAI(
                api_key=openai_config.get("api_key", os.getenv("OPENAI_API_KEY")),
            )
            redis_config = self.config.get("redis", {})
            self.redis = Redis(
                host=redis_config.get("host", "localhost"),
                port=redis_config.get("port", 6379),
                db=redis_config.get("db", 0),
                decode_responses=True
            )
            self.model = openai_config.get("embedding_model", "text-embedding-3-small")
            self.dimensions = openai_config.get("embedding_dimensions", 1536)
            self.batch_size = openai_config.get("embedding_batch_size", 100)
            logger.info("✅ 임베딩 컴포넌트 초기화 완료")
        except Exception as e:
            logger.error(f"❌ 초기화 실패: {str(e)}")
            raise
            
    async def create_embedding(self, text: str, use_cache: bool = True) -> Optional[np.ndarray]:
        try:
            if not text:
                return None
            if use_cache:
                cached_embedding = await self._get_cached_embedding(text)
                if cached_embedding is not None:
                    return cached_embedding
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
                dimensions=self.dimensions
            )
            if not response or not response.data:
                return None
            vector = np.array(response.data[0].embedding, dtype=np.float32)
            if use_cache:
                await self._cache_embedding(text, vector)
            return vector
        except Exception as e:
            logger.error(f"❌ 임베딩 생성 실패: {str(e)}")
            return None
            
    async def create_embeddings_batch(self, texts: List[str], use_cache: bool = True) -> List[Optional[np.ndarray]]:
        try:
            if not texts:
                return []
            results = []
            for i in range(0, len(texts), self.batch_size):
                batch = texts[i:i + self.batch_size]
                cached_embeddings = []
                uncached_texts = []
                uncached_indices = []
                if use_cache:
                    for j, text in enumerate(batch):
                        cached = await self._get_cached_embedding(text)
                        if cached is not None:
                            cached_embeddings.append((j, cached))
                        else:
                            uncached_texts.append(text)
                            uncached_indices.append(j)
                else:
                    uncached_texts = batch
                    uncached_indices = list(range(len(batch)))
                if uncached_texts:
                    response = await self.client.embeddings.create(
                        model=self.model,
                        input=uncached_texts,
                        dimensions=self.dimensions
                    )
                    if response and response.data:
                        for j, embedding in enumerate(response.data):
                            vector = np.array(embedding.embedding, dtype=np.float32)
                            idx = uncached_indices[j]
                            cached_embeddings.append((idx, vector))
                            if use_cache:
                                await self._cache_embedding(uncached_texts[j], vector)
                cached_embeddings.sort(key=lambda x: x[0])
                results.extend([v for _, v in cached_embeddings])
            return results
        except Exception as e:
            logger.error(f"❌ 배치 임베딩 생성 실패: {str(e)}")
            return [None] * len(texts)
            
    async def _get_cached_embedding(self, text: str) -> Optional[np.ndarray]:
        try:
            cached_data = await self.redis.get(f"embedding:{text}")
            if cached_data:
                return np.array(json.loads(cached_data), dtype=np.float32)
            return None
        except Exception as e:
            logger.error(f"❌ 캐시된 임베딩 조회 실패: {str(e)}")
            return None
            
    async def _cache_embedding(self, text: str, vector: np.ndarray):
        try:
            await self.redis.setex(
                f"embedding:{text}",
                3600,
                json.dumps(vector.tolist())
            )
        except Exception as e:
            logger.error(f"❌ 임베딩 캐시 실패: {str(e)}")
            
    async def test_connection(self) -> bool:
        try:
            await self.client.embeddings.create(
                model=self.model,
                input="test",
                dimensions=self.dimensions
            )
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error(f"❌ 연결 테스트 실패: {str(e)}")
            return False
            
    async def cleanup(self):
        try:
            if hasattr(self, 'redis'):
                await self.redis.close()
            logger.info("✅ 리소스 정리 완료")
        except Exception as e:
            logger.error(f"❌ 정리 중 오류 발생: {str(e)}")
            
    def __del__(self):
        asyncio.create_task(self.cleanup())

_embeddings = None

async def get_embeddings() -> Embeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = Embeddings()
    return _embeddings