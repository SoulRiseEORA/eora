"""
memory_structurer.py
- 메모리 원자 구조 정의
- 메모리 원자 생성 및 검증
- 메모리 원자 병합
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

# 상대 경로 임포트
from .config import get_config
from .embeddings import get_embeddings
from .vector_store import get_vector_store

logger = logging.getLogger(__name__)

class MemoryAtom:
    def __init__(
        self,
        content: str,
        memory_id: Optional[str] = None,
        type: str = "text",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.memory_id = memory_id or self._generate_memory_id()
        self.type = type
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
    def _generate_memory_id(self) -> str:
        """메모리 ID 생성"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        return f"mem_{timestamp}"
        
    def to_dict(self) -> Dict[str, Any]:
        """메모리 원자를 딕셔너리로 변환"""
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "type": self.type,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryAtom':
        """딕셔너리에서 메모리 원자 생성"""
        return cls(
            content=data["content"],
            memory_id=data["memory_id"],
            type=data["type"],
            metadata=data["metadata"]
        )

class MemoryStructurer:
    def __init__(self):
        self.config = get_config()
        self._initialized = False
        self._initialize()
        
    def _initialize(self):
        try:
            # MongoDB 클라이언트 초기화
            mongo_config = self.config.get("mongodb", {})
            self.client = AsyncIOMotorClient(
                mongo_config.get("uri", os.getenv("MONGODB_URI", "mongodb://localhost:27017")),
                maxPoolSize=mongo_config.get("max_pool_size", 100),
                minPoolSize=mongo_config.get("min_pool_size", 10)
            )
            self.db = self.client[mongo_config.get("db_name", "aura_db")]
            self.memories = self.db.memories
            
            # Redis 클라이언트 초기화
            redis_config = self.config.get("redis", {})
            self.redis = Redis(
                host=redis_config.get("host", "localhost"),
                port=redis_config.get("port", 6379),
                db=redis_config.get("db", 0),
                decode_responses=True
            )
            
            # 컴포넌트 초기화
            self.embeddings = None
            self.vector_store = None
            
            # 인덱스 생성
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._create_indexes())
            else:
                loop.run_until_complete(self._create_indexes())
            
            logger.info("✅ 메모리 구조화기 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ 초기화 실패: {str(e)}")
            raise
            
    async def _initialize_components(self):
        """비동기 컴포넌트 초기화"""
        try:
            self.embeddings = await get_embeddings()
            self.vector_store = await get_vector_store()
            
        except Exception as e:
            logger.error(f"❌ 컴포넌트 초기화 실패: {str(e)}")
            raise

    async def _create_indexes(self):
        """인덱스 생성"""
        try:
            # 메모리 컬렉션 인덱스
            await self.memories.create_index([("content", "text")])
            await self.memories.create_index([("timestamp", -1)])
            await self.memories.create_index([("type", 1)])
            await self.memories.create_index([("importance", -1)])
            
            logger.info("✅ 인덱스 생성 완료")
            
        except Exception as e:
            logger.error(f"❌ 인덱스 생성 실패: {str(e)}")
            raise
            
    async def structure_memory(
        self,
        content: str,
        type: str = "text",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[MemoryAtom]:
        try:
            if not content:
                return None
                
            # 메모리 원자 생성
            memory = MemoryAtom(
                content=content,
                type=type,
                metadata=metadata or {}
            )
            
            # 메타데이터 생성
            memory.metadata.update(await self._generate_metadata(content))
            
            # 벡터 생성
            vector = await self._create_vector(content)
            if vector is None:
                return None
                
            # MongoDB에 저장
            doc = memory.to_dict()
            doc["vector"] = vector.tolist()
            
            result = await self.memories.insert_one(doc)
            if not result.inserted_id:
                return None
                
            # Redis 캐시 업데이트
            await self._cache_memory(memory.memory_id, doc)
            
            return memory
            
        except Exception as e:
            logger.error(f"❌ 메모리 구조화 실패: {str(e)}")
            return None
            
    async def _generate_metadata(self, content: str) -> Dict[str, Any]:
        try:
            # 태그 추출
            tags = await self._extract_tags(content)
            
            # 중요도 계산
            importance = await self._calculate_importance(content)
            
            # 감정 분석
            emotion = await self._analyze_emotion(content)
            
            return {
                "tags": tags,
                "importance": importance,
                "emotion": emotion,
                "length": len(content),
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 메타데이터 생성 실패: {str(e)}")
            return {}
            
    async def _create_vector(self, content: str) -> Optional[np.ndarray]:
        try:
            if not self.embeddings:
                await self._initialize_components()
                
            return await self.embeddings.create_embedding(content)
            
        except Exception as e:
            logger.error(f"❌ 벡터 생성 실패: {str(e)}")
            return None
            
    async def _extract_tags(self, content: str) -> List[str]:
        try:
            # 키워드 기반 태그 추출
            keywords = self.config.get("keywords", [])
            tags = []
            
            for keyword in keywords:
                if keyword.lower() in content.lower():
                    tags.append(keyword)
                    
            return tags
            
        except Exception as e:
            logger.error(f"❌ 태그 추출 실패: {str(e)}")
            return []
            
    async def _calculate_importance(self, content: str) -> float:
        try:
            # 기본 중요도 계산
            base_importance = min(1.0, len(content) / 1000)
            
            # 키워드 기반 중요도 조정
            keywords = self.config.get("keywords", [])
            keyword_count = sum(1 for k in keywords if k.lower() in content.lower())
            
            # 최종 중요도 계산
            importance = base_importance + (keyword_count * 0.1)
            return min(1.0, importance)
            
        except Exception as e:
            logger.error(f"❌ 중요도 계산 실패: {str(e)}")
            return 0.5
            
    async def _analyze_emotion(self, content: str) -> Dict[str, float]:
        try:
            # 감정 키워드 기반 분석
            emotions = self.config.get("emotions", {})
            scores = {emotion: 0.0 for emotion in emotions}
            
            for emotion, keywords in emotions.items():
                for keyword in keywords:
                    if keyword.lower() in content.lower():
                        scores[emotion] += 0.2
                        
            # 점수 정규화
            total = sum(scores.values())
            if total > 0:
                scores = {k: v/total for k, v in scores.items()}
                
            return scores
            
        except Exception as e:
            logger.error(f"❌ 감정 분석 실패: {str(e)}")
            return {}
            
    async def _get_cached_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        try:
            # Redis에서 메모리 조회
            cached_data = await self.redis.get(f"memory:{memory_id}")
            if cached_data:
                return json.loads(cached_data)
                
            return None
            
        except Exception as e:
            logger.error(f"❌ 캐시된 메모리 조회 실패: {str(e)}")
            return None
            
    async def _cache_memory(self, memory_id: str, memory: Dict[str, Any]):
        try:
            # Redis에 메모리 캐시
            await self.redis.setex(
                f"memory:{memory_id}",
                3600,  # 1시간 TTL
                json.dumps(memory)
            )
            
        except Exception as e:
            logger.error(f"❌ 메모리 캐시 실패: {str(e)}")
            
    async def test_connection(self) -> bool:
        try:
            # MongoDB 연결 테스트
            await self.db.command("ping")
            
            # Redis 연결 테스트
            await self.redis.ping()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 연결 테스트 실패: {str(e)}")
            return False
            
    async def cleanup(self):
        try:
            # 리소스 정리
            if hasattr(self, 'client'):
                self.client.close()
            if hasattr(self, 'redis'):
                await self.redis.close()
                
            logger.info("✅ 리소스 정리 완료")
            
        except Exception as e:
            logger.error(f"❌ 정리 중 오류 발생: {str(e)}")
            
    def __del__(self):
        pass

    async def initialize(self):
        """(옵션) 메모리 스트럭처러 초기화"""
        pass

# 싱글톤 인스턴스
_memory_structurer = None

async def get_memory_structurer() -> MemoryStructurer:
    """메모리 구조화기 인스턴스 반환"""
    global _memory_structurer
    if _memory_structurer is None:
        _memory_structurer = MemoryStructurer()
    return _memory_structurer
