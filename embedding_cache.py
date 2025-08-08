#!/usr/bin/env python3
"""
임베딩 캐싱 시스템 - GPT 응답 속도 최적화
"""

import hashlib
import threading
from typing import Dict, List, Optional
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

class EmbeddingCache:
    """임베딩 결과를 캐싱하여 중복 계산을 방지하는 클래스"""
    
    def __init__(self, max_size: int = 500):
        self.max_size = max_size
        self._cache: OrderedDict[str, List[float]] = OrderedDict()
        self._lock = threading.RLock()
        
    def _get_cache_key(self, text: str) -> str:
        """텍스트에 대한 캐시 키 생성"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def get(self, text: str) -> Optional[List[float]]:
        """캐시에서 임베딩 조회"""
        if not text or not text.strip():
            return None
            
        cache_key = self._get_cache_key(text.strip())
        
        with self._lock:
            if cache_key in self._cache:
                # LRU: 최근 사용된 것을 맨 뒤로 이동
                embedding = self._cache.pop(cache_key)
                self._cache[cache_key] = embedding
                logger.debug(f"🔍 임베딩 캐시 히트: {text[:50]}...")
                return embedding
                
        return None
    
    def set(self, text: str, embedding: List[float]) -> None:
        """캐시에 임베딩 저장"""
        if not text or not text.strip() or not embedding:
            return
            
        cache_key = self._get_cache_key(text.strip())
        
        with self._lock:
            # 이미 존재하면 업데이트
            if cache_key in self._cache:
                self._cache.pop(cache_key)
            
            # 새로운 항목 추가
            self._cache[cache_key] = embedding
            
            # 크기 제한 초과 시 가장 오래된 항목 제거
            while len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                self._cache.pop(oldest_key)
                logger.debug("📦 임베딩 캐시 크기 제한으로 인한 항목 제거")
                
            logger.debug(f"💾 임베딩 캐시 저장: {text[:50]}... (총 {len(self._cache)}개)")
    
    def clear(self) -> None:
        """캐시 초기화"""
        with self._lock:
            self._cache.clear()
            logger.info("🧹 임베딩 캐시 초기화 완료")
    
    def stats(self) -> Dict[str, int]:
        """캐시 통계 반환"""
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self.max_size
            }

# 전역 임베딩 캐시 인스턴스
_global_cache: Optional[EmbeddingCache] = None
_cache_lock = threading.Lock()

def get_embedding_cache() -> EmbeddingCache:
    """전역 임베딩 캐시 인스턴스 반환 (지연 초기화)"""
    global _global_cache
    
    if _global_cache is None:
        with _cache_lock:
            if _global_cache is None:
                _global_cache = EmbeddingCache(max_size=500)
                logger.info("🚀 전역 임베딩 캐시 초기화 완료")
    
    return _global_cache

def cached_embedding(text: str, embedding_func) -> List[float]:
    """
    캐시를 사용하는 임베딩 생성 함수
    
    Args:
        text (str): 임베딩을 생성할 텍스트
        embedding_func: 실제 임베딩 생성 함수
        
    Returns:
        List[float]: 임베딩 벡터
    """
    cache = get_embedding_cache()
    
    # 캐시에서 조회
    cached_result = cache.get(text)
    if cached_result is not None:
        return cached_result
    
    # 캐시에 없으면 새로 생성
    try:
        embedding = embedding_func(text)
        if embedding:
            cache.set(text, embedding)
        return embedding
    except Exception as e:
        logger.error(f"❌ 임베딩 생성 실패: {e}")
        return []

def clear_embedding_cache() -> None:
    """전역 임베딩 캐시 초기화"""
    global _global_cache
    if _global_cache:
        _global_cache.clear()

def get_cache_stats() -> Dict[str, int]:
    """캐시 통계 반환"""
    cache = get_embedding_cache()
    return cache.stats()