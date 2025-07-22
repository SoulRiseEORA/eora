"""
recall_memory_with_enhancements.py
- 메모리 회상 기능 강화
- 벡터 검색 및 태그 기반 검색 통합
- 감정 분석 및 시간적 관련성 고려
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import numpy as np
from redis.asyncio import Redis
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, OperationFailure
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.objectid import ObjectId
from dotenv import load_dotenv
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecallEnhancer:
    """메모리 회상 강화 클래스"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        if not self._initialized:
            self._meta_store = None
            self._vector_store = None
            self._embeddings = None
            self._memory_store = None
            self._initialized = True
            
    @property
    def meta_store(self):
        return self._meta_store
        
    @meta_store.setter
    def meta_store(self, value):
        self._meta_store = value
        
    @property
    def vector_store(self):
        return self._vector_store
        
    @vector_store.setter
    def vector_store(self, value):
        self._vector_store = value
        
    @property
    def embeddings(self):
        return self._embeddings
        
    @embeddings.setter
    def embeddings(self, value):
        self._embeddings = value
        
    @property
    def memory_store(self):
        return self._memory_store
        
    @memory_store.setter
    def memory_store(self, value):
        self._memory_store = value
        
    async def initialize(self):
        """비동기 초기화"""
        try:
            # 메타데이터 저장소 초기화
            from aura_system.meta_store import get_meta_store
            self._meta_store = await get_meta_store()
            if not self._meta_store:
                raise Exception("메타데이터 저장소 초기화 실패")
                
            # 벡터 저장소 초기화
            from aura_system.vector_store import get_vector_store
            self._vector_store = await get_vector_store()
            if not self._vector_store:
                raise Exception("벡터 저장소 초기화 실패")
                
            # 메모리 저장소 초기화
            from aura_system.memory_store import get_memory_store
            self._memory_store = await get_memory_store()
            if not self._memory_store:
                raise Exception("메모리 저장소 초기화 실패")
                
            # 임베딩 모델 초기화
            from aura_system.embeddings import get_embeddings
            self._embeddings = await get_embeddings()
            if not self._embeddings:
                raise Exception("임베딩 모델 초기화 실패")
                
            logger.info("✅ 메모리 회상 강화 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ 메모리 회상 강화 초기화 실패: {str(e)}")
            return False
            
    async def recall_memory(
        self,
        query: str,
        limit: int = 5,
        min_score: float = 0.7
    ) -> List[Dict[str, Any]]:
        """메모리 회상"""
        try:
            # 벡터 검색
            vector_results = await self._vector_store.search(
                query,
                limit=limit * 2  # 더 많은 결과를 가져와서 필터링
            )
            
            # 태그 기반 검색
            tag_results = await self._search_by_tags(query)
            
            # 결과 병합 및 점수 계산
            merged_results = await self._merge_results(
                vector_results,
                tag_results,
                limit=limit,
                min_score=min_score
            )
            
            return merged_results
            
        except Exception as e:
            logger.error(f"❌ 메모리 회상 실패: {str(e)}")
            return []
            
    async def _search_by_tags(self, query: str) -> List[Dict[str, Any]]:
        """태그 기반 검색"""
        try:
            return await self._meta_store.search_by_tags(query)
            
        except Exception as e:
            logger.error(f"❌ 태그 검색 실패: {str(e)}")
            return []
            
    async def _merge_results(
        self,
        vector_results: List[Dict[str, Any]],
        tag_results: List[Dict[str, Any]],
        limit: int,
        min_score: float
    ) -> List[Dict[str, Any]]:
        """검색 결과 병합"""
        try:
            # 결과 ID 추출
            vector_ids = {r['id'] for r in vector_results}
            tag_ids = {r['id'] for r in tag_results}
            
            # 공통 결과 찾기
            common_ids = vector_ids.intersection(tag_ids)
            
            # 점수 계산 및 정렬
            scored_results = []
            for result in vector_results + tag_results:
                if result['id'] in common_ids:
                    # 공통 결과는 더 높은 점수
                    result['score'] *= 1.2
                scored_results.append(result)
                
            # 중복 제거 및 정렬
            unique_results = {}
            for result in scored_results:
                if result['id'] not in unique_results or \
                   result['score'] > unique_results[result['id']]['score']:
                    unique_results[result['id']] = result
                    
            # 최종 결과 필터링 및 정렬
            final_results = [
                r for r in unique_results.values()
                if r['score'] >= min_score
            ]
            final_results.sort(key=lambda x: x['score'], reverse=True)
            
            return final_results[:limit]
            
        except Exception as e:
            logger.error(f"❌ 결과 병합 실패: {str(e)}")
            return []
            
    async def cleanup(self):
        """리소스 정리"""
        try:
            if self._meta_store:
                await self._meta_store.cleanup()
                
            if self._vector_store:
                await self._vector_store.cleanup()
                
            if self._memory_store:
                await self._memory_store.cleanup()
                
            if self._embeddings:
                await self._embeddings.cleanup()
                
            logger.info("✅ 메모리 회상 강화 정리 완료")
            
        except Exception as e:
            logger.error(f"❌ 메모리 회상 강화 정리 실패: {str(e)}")
            
    def __del__(self):
        pass

# 싱글톤 인스턴스
_recall_enhancer = None

async def get_recall_enhancer() -> RecallEnhancer:
    """메모리 회상 강화 인스턴스 반환"""
    global _recall_enhancer
    if _recall_enhancer is None:
        _recall_enhancer = RecallEnhancer()
        if not await _recall_enhancer.initialize():
            logger.error("❌ 메모리 회상 강화 초기화 실패")
            return None
    return _recall_enhancer 