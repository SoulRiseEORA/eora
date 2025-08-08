"""
벡터 저장소
- 임베딩 생성
- 메모리 저장
- 메모리 검색
"""

import os
import sys
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple, Union
from openai import OpenAI, AsyncOpenAI
import numpy as np
import faiss
from pathlib import Path
from datetime import datetime
import openai
from .openai_client import get_openai_client
import redis
from aura_system.config import get_config
from aura_system.embeddings import get_embeddings
from redis.asyncio import Redis
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, OperationFailure
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.objectid import ObjectId
from dotenv import load_dotenv
from asyncio import CancelledError

logger = logging.getLogger(__name__)

def _get_valid_openai_key():
    """통합 API 키 검색 함수"""
    # 여러 가능한 환경변수 이름 시도
    possible_keys = [
        "OPENAI_API_KEY",
        "OPENAI_API_KEY_1", 
        "OPENAI_API_KEY_2",
        "OPENAI_API_KEY_3",
        "OPENAI_API_KEY_4",
        "OPENAI_API_KEY_5"
    ]
    
    # 환경 변수에서 찾기
    for key_name in possible_keys:
        key_value = os.getenv(key_name)
        if key_value and key_value.startswith("sk-") and len(key_value) > 50:
            logger.info(f"✅ Vector Store - 유효한 API 키 발견: {key_name}")
            # 환경변수에 강제로 설정하여 일관성 보장
            os.environ["OPENAI_API_KEY"] = key_value
            return key_value
    
    logger.warning("⚠️ Vector Store - 유효한 OpenAI API 키를 찾을 수 없습니다")
    return os.getenv("OPENAI_API_KEY")  # 기본값으로 폴백

class FaissIndex:
    """Faiss 인덱스 관리"""
    
    def __init__(self, dimension: int = 1536):
        """초기화"""
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata = []
        
    def add(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]):
        """벡터 추가"""
        self.index.add(vectors)
        self.metadata.extend(metadata)
        
    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """벡터 검색"""
        distances, indices = self.index.search(query_vector, k)
        return [
            {
                "metadata": self.metadata[idx],
                "distance": float(distances[0][i])
            }
            for i, idx in enumerate(indices[0])
        ]
        
    def save(self, path: str):
        """인덱스 저장"""
        faiss.write_index(self.index, f"{path}.index")
        with open(f"{path}.metadata", "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            
    @classmethod
    def load(cls, path: str) -> "FaissIndex":
        """인덱스 로드"""
        index = cls()
        index.index = faiss.read_index(f"{path}.index")
        with open(f"{path}.metadata", "r", encoding="utf-8") as f:
            index.metadata = json.load(f)
        return index

    def get_embedding(self, text: str) -> np.ndarray:
        """텍스트 임베딩 생성
        
        Args:
            text (str): 임베딩할 텍스트
            
        Returns:
            np.ndarray: 임베딩 벡터
        """
        try:
            return embed_text(text)
        except Exception as e:
            logger.error(f"❌ 임베딩 생성 실패: {str(e)}")
            raise

def embed_text(text: str) -> np.ndarray:
    """텍스트 임베딩 생성 (동기)
    
    Args:
        text (str): 임베딩할 텍스트
        
    Returns:
        np.ndarray: 임베딩 벡터
    """
    try:
        client = OpenAI(api_key=_get_valid_openai_key())
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return np.array(response.data[0].embedding)
    except Exception as e:
        logger.error(f"❌ 임베딩 생성 실패: {str(e)}")
        raise

async def embed_text_async(text: str, api_key: str = None) -> List[float]:
    """텍스트 임베딩 생성"""
    try:
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API 키가 필요합니다.")
        
        async_client = AsyncOpenAI(api_key=api_key)
        response = await async_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    except CancelledError:
        logger.warning("embed_text_async에서 CancelledError 발생: 앱 종료 등으로 인한 자연스러운 현상")
        return None
    except Exception as e:
        logger.error(f"❌ 텍스트 임베딩 실패: {str(e)}")
        raise

def get_embedding(text: str) -> np.ndarray:
    """텍스트 임베딩 생성 (동기) - 캐싱 적용
    
    Args:
        text (str): 임베딩할 텍스트
        
    Returns:
        np.ndarray: 임베딩 벡터
    """
    from embedding_cache import cached_embedding
    
    def _generate_embedding(text: str):
        try:
            client = OpenAI(api_key=_get_valid_openai_key())
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"❌ 임베딩 생성 실패: {str(e)}")
            raise
    
    try:
        embedding_list = cached_embedding(text, _generate_embedding)
        return np.array(embedding_list) if embedding_list else np.array([])
    except Exception as e:
        logger.error(f"❌ 캐시된 임베딩 생성 실패: {str(e)}")
        raise

class VectorStore:
    """벡터 저장소"""
    
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
            self._db = None
            self._initialized = True
            
    async def initialize(self):
        """비동기 초기화"""
        try:
            # 컴포넌트 초기화
            self.embeddings = get_embeddings()
            
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
            
            # 인덱스 생성
            await self._create_indexes()
            
            logger.info("✅ 벡터 저장소 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ 초기화 실패: {str(e)}")
            raise
            
    async def _create_indexes(self):
        """인덱스 생성"""
        try:
            # vectors 컬렉션 인덱스
            await self._db.vectors.create_index([("vector_id", ASCENDING)], unique=True)
            await self._db.vectors.create_index([("metadata.tags", ASCENDING)])
            await self._db.vectors.create_index([("metadata.timestamp", DESCENDING)])
            await self._db.vectors.create_index([("metadata.type", ASCENDING)])
            
            # 복합 인덱스
            await self._db.vectors.create_index([
                ("metadata.tags", ASCENDING),
                ("metadata.timestamp", DESCENDING)
            ])
            
            logger.info("✅ 인덱스 생성 완료")
            
        except Exception as e:
            logger.error(f"❌ 인덱스 생성 실패: {str(e)}")
            
    async def store_vector(
        self,
        vector_id: str,
        vector: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            if vector is None or not isinstance(vector, np.ndarray):
                return False
                
            # 벡터 데이터 구조화
            vector_data = {
                "vector_id": vector_id,
                "vector": vector.tolist(),
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # MongoDB에 저장
            await self._db.vectors.insert_one(vector_data)
            
            # Redis에 캐시
            await self._redis_client.setex(
                f"vector:{vector_id}",
                3600,  # 1시간 TTL
                json.dumps(vector_data)
            )
            
            logger.info(f"✅ 벡터 저장 완료: {vector_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 벡터 저장 실패: {str(e)}")
            return False
            
    async def get_vector(self, vector_id: str) -> Optional[Dict[str, Any]]:
        try:
            # Redis 캐시 확인
            cached_vector = await self._redis_client.get(f"vector:{vector_id}")
            if cached_vector:
                return json.loads(cached_vector)
                
            # MongoDB에서 조회
            vector = await self._db.vectors.find_one({"vector_id": vector_id})
            if vector:
                # Redis에 캐시
                await self._redis_client.setex(
                    f"vector:{vector_id}",
                    3600,  # 1시간 TTL
                    json.dumps({
                        "vector": vector["vector"],
                        "metadata": vector["metadata"]
                    })
                )
                return vector
                
            return None
            
        except Exception as e:
            logger.error(f"❌ 벡터 조회 실패: {str(e)}")
            return None
            
    async def update_vector(
        self,
        vector_id: str,
        vector: Optional[np.ndarray] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            # 업데이트 데이터 검증
            if not await self._validate_updates(vector, metadata):
                return False
                
            # 업데이트 데이터 준비
            update_data = {"updated_at": datetime.utcnow().isoformat()}
            if vector is not None:
                update_data["vector"] = vector.tolist()
            if metadata is not None:
                update_data["metadata"] = metadata
                
            # MongoDB 업데이트
            result = await self._db.vectors.update_one(
                {"vector_id": vector_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                # Redis 캐시 삭제
                await self._redis_client.delete(f"vector:{vector_id}")
                
                logger.info(f"✅ 벡터 업데이트 완료: {vector_id}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"❌ 벡터 업데이트 실패: {str(e)}")
            return False
            
    async def delete_vector(self, vector_id: str) -> bool:
        try:
            # MongoDB에서 삭제
            result = await self._db.vectors.delete_one({"vector_id": vector_id})
            
            if result.deleted_count > 0:
                # Redis 캐시 삭제
                await self._redis_client.delete(f"vector:{vector_id}")
                
                logger.info(f"✅ 벡터 삭제 완료: {vector_id}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"❌ 벡터 삭제 실패: {str(e)}")
            return False
            
    async def search_vectors(
        self,
        query_vector: np.ndarray,
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        try:
            if query_vector is None or not isinstance(query_vector, np.ndarray):
                return []
                
            # 모든 벡터 조회
            cursor = self._db.vectors.find({})
            vectors = await cursor.to_list(length=None)
            
            # 유사도 계산 및 정렬
            results = []
            for vector_data in vectors:
                similarity = self._calculate_similarity(
                    query_vector,
                    np.array(vector_data["vector"])
                )
                
                if similarity >= threshold:
                    results.append({
                        **vector_data,
                        "similarity": similarity
                    })
                    
            # 유사도 기준 정렬
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"❌ 벡터 검색 실패: {str(e)}")
            return []
            
    def _calculate_similarity(
        self,
        vector1: np.ndarray,
        vector2: np.ndarray
    ) -> float:
        try:
            # 코사인 유사도 계산
            dot_product = np.dot(vector1, vector2)
            norm1 = np.linalg.norm(vector1)
            norm2 = np.linalg.norm(vector2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            return float(dot_product / (norm1 * norm2))
            
        except Exception as e:
            logger.error(f"❌ 유사도 계산 실패: {str(e)}")
            return 0.0
            
    async def _validate_updates(
        self,
        vector: Optional[np.ndarray],
        metadata: Optional[Dict[str, Any]]
    ) -> bool:
        try:
            # 벡터 검증
            if vector is not None and not isinstance(vector, np.ndarray):
                return False
                
            # 메타데이터 검증
            if metadata is not None and not isinstance(metadata, dict):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"❌ 업데이트 검증 실패: {str(e)}")
            return False
            
    async def cleanup(self):
        """리소스 정리"""
        try:
            if self._mongo_client:
                self._mongo_client.close()
            if self._redis_client:
                await self._redis_client.close()
                
            if hasattr(self, 'embeddings'):
                await self.embeddings.cleanup()
                
            logger.info("✅ 리소스 정리 완료")
            
        except Exception as e:
            logger.error(f"❌ 정리 중 오류 발생: {str(e)}")
            
    def __del__(self):
        pass

# 싱글톤 인스턴스
_vector_store = None

async def get_vector_store() -> VectorStore:
    """벡터 저장소 인스턴스 반환"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
        await _vector_store.initialize()
    return _vector_store 