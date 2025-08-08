#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI 성능 최적화 모듈
API 응답속도 향상을 위한 최적화 시스템
"""

import time
import asyncio
import threading
from typing import Dict, Any, List, Optional, Callable
from functools import wraps, lru_cache
import logging
from datetime import datetime, timedelta
import json
import hashlib

logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """성능 최적화 및 캐싱 시스템"""
    
    def __init__(self):
        self.response_cache = {}
        self.memory_cache = {}
        self.session_cache = {}
        self.cache_ttl = 300  # 5분 캐시
        self.max_cache_size = 1000
        self.performance_stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'avg_response_time': 0.0,
            'slow_requests': 0
        }
        
    def cache_key(self, *args, **kwargs) -> str:
        """캐시 키 생성"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def is_cache_valid(self, timestamp: datetime) -> bool:
        """캐시 유효성 검사"""
        return (datetime.now() - timestamp).seconds < self.cache_ttl
    
    def cache_response(self, key: str, data: Any) -> None:
        """응답 캐싱"""
        if len(self.response_cache) >= self.max_cache_size:
            # 오래된 캐시 항목 제거
            oldest_key = min(self.response_cache.keys(), 
                           key=lambda k: self.response_cache[k]['timestamp'])
            del self.response_cache[oldest_key]
        
        self.response_cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def get_cached_response(self, key: str) -> Optional[Any]:
        """캐시된 응답 조회"""
        if key in self.response_cache:
            cache_item = self.response_cache[key]
            if self.is_cache_valid(cache_item['timestamp']):
                self.performance_stats['cache_hits'] += 1
                return cache_item['data']
            else:
                del self.response_cache[key]
        return None


def performance_monitor(func):
    """성능 모니터링 데코레이터"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            response_time = end_time - start_time
            
            # 성능 통계 업데이트
            optimizer.performance_stats['total_requests'] += 1
            current_avg = optimizer.performance_stats['avg_response_time']
            total_requests = optimizer.performance_stats['total_requests']
            
            optimizer.performance_stats['avg_response_time'] = (
                (current_avg * (total_requests - 1) + response_time) / total_requests
            )
            
            if response_time > 2.0:  # 2초 이상이면 느린 요청
                optimizer.performance_stats['slow_requests'] += 1
                logger.warning(f"⚠️ 느린 응답 감지: {func.__name__} - {response_time:.2f}초")
            
            logger.info(f"⚡ {func.__name__}: {response_time:.3f}초")
    
    return wrapper


def cached_response(ttl: int = 300):
    """응답 캐싱 데코레이터"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = optimizer.cache_key(func.__name__, *args, **kwargs)
            
            # 캐시된 응답 확인
            cached = optimizer.get_cached_response(cache_key)
            if cached:
                logger.info(f"💾 캐시 히트: {func.__name__}")
                return cached
            
            # 새 응답 생성 및 캐싱
            result = await func(*args, **kwargs)
            optimizer.cache_response(cache_key, result)
            
            return result
        
        return wrapper
    return decorator


class AsyncBatchProcessor:
    """비동기 배치 처리 시스템"""
    
    def __init__(self, batch_size: int = 10, max_wait_time: float = 0.1):
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.pending_requests = []
        self.batch_lock = asyncio.Lock()
        
    async def add_to_batch(self, request_data: Dict[str, Any]) -> Any:
        """배치에 요청 추가"""
        async with self.batch_lock:
            future = asyncio.Future()
            self.pending_requests.append({
                'data': request_data,
                'future': future
            })
            
            # 배치 크기 도달 또는 대기 시간 초과 시 처리
            if len(self.pending_requests) >= self.batch_size:
                await self._process_batch()
            else:
                asyncio.create_task(self._wait_and_process())
            
            return await future
    
    async def _wait_and_process(self):
        """대기 후 배치 처리"""
        await asyncio.sleep(self.max_wait_time)
        async with self.batch_lock:
            if self.pending_requests:
                await self._process_batch()
    
    async def _process_batch(self):
        """배치 처리 실행"""
        if not self.pending_requests:
            return
        
        current_batch = self.pending_requests.copy()
        self.pending_requests.clear()
        
        try:
            # 배치 처리 로직 (병렬 처리)
            tasks = []
            for request in current_batch:
                task = self._process_single_request(request['data'])
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 결과 반환
            for request, result in zip(current_batch, results):
                if isinstance(result, Exception):
                    request['future'].set_exception(result)
                else:
                    request['future'].set_result(result)
                    
        except Exception as e:
            # 모든 요청에 에러 반환
            for request in current_batch:
                request['future'].set_exception(e)
    
    async def _process_single_request(self, request_data: Dict[str, Any]) -> Any:
        """단일 요청 처리"""
        # 실제 처리 로직은 상속받는 클래스에서 구현
        return request_data


class FastMemoryRecall:
    """빠른 메모리 회상 시스템"""
    
    def __init__(self):
        self.keyword_index = {}
        self.embedding_cache = {}
        self.recent_queries = {}
        
    def build_keyword_index(self, memories: List[Dict[str, Any]]) -> None:
        """키워드 인덱스 구축"""
        self.keyword_index.clear()
        
        for memory in memories:
            content = memory.get('content', '').lower()
            memory_id = memory.get('memory_id') or memory.get('_id')
            
            # 키워드 추출 및 인덱싱
            words = content.split()
            for word in words:
                if len(word) > 2:  # 2글자 이상만 인덱싱
                    if word not in self.keyword_index:
                        self.keyword_index[word] = []
                    self.keyword_index[word].append(memory_id)
    
    def fast_keyword_search(self, query: str, limit: int = 10) -> List[str]:
        """빠른 키워드 검색"""
        query_words = query.lower().split()
        memory_scores = {}
        
        for word in query_words:
            if word in self.keyword_index:
                for memory_id in self.keyword_index[word]:
                    memory_scores[memory_id] = memory_scores.get(memory_id, 0) + 1
        
        # 점수순 정렬
        sorted_memories = sorted(memory_scores.items(), key=lambda x: x[1], reverse=True)
        return [memory_id for memory_id, _ in sorted_memories[:limit]]


class DatabaseOptimizer:
    """데이터베이스 최적화"""
    
    def __init__(self):
        self.connection_pool = None
        self.query_cache = {}
        self.prepared_statements = {}
    
    async def optimize_mongodb_queries(self, collection):
        """MongoDB 쿼리 최적화"""
        try:
            # 인덱스 생성
            await collection.create_index([("user_id", 1), ("timestamp", -1)])
            await collection.create_index([("content", "text")])
            await collection.create_index([("memory_type", 1), ("user_id", 1)])
            
            logger.info("✅ MongoDB 인덱스 최적화 완료")
        except Exception as e:
            logger.error(f"❌ MongoDB 최적화 실패: {e}")
    
    def optimize_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """쿼리 최적화"""
        optimized = query.copy()
        
        # 불필요한 필드 제거
        if 'projection' not in optimized:
            optimized['projection'] = {
                'content': 1,
                'timestamp': 1,
                'user_id': 1,
                'memory_type': 1
            }
        
        # 제한 설정
        if 'limit' not in optimized:
            optimized['limit'] = 50
        
        return optimized


class ResponseCompressor:
    """응답 압축 시스템"""
    
    @staticmethod
    def compress_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """응답 데이터 압축"""
        compressed = {}
        
        # 필수 필드만 포함
        essential_fields = ['success', 'response', 'formatted_response', 'session_id']
        for field in essential_fields:
            if field in data:
                compressed[field] = data[field]
        
        # 긴 텍스트 최적화
        if 'response' in compressed and len(compressed['response']) > 1000:
            # 마크다운 처리된 버전이 있으면 원본은 요약
            if 'formatted_response' in compressed:
                compressed['response'] = compressed['response'][:500] + "..."
        
        return compressed


# 전역 최적화 인스턴스
optimizer = PerformanceOptimizer()
batch_processor = AsyncBatchProcessor()
fast_recall = FastMemoryRecall()
db_optimizer = DatabaseOptimizer()
compressor = ResponseCompressor()


async def optimize_chat_response(original_func):
    """채팅 응답 최적화 래퍼"""
    @wraps(original_func)
    @performance_monitor
    @cached_response(ttl=60)  # 1분 캐시
    async def optimized_wrapper(*args, **kwargs):
        # 배치 처리로 요청 최적화
        request_data = {
            'func': original_func,
            'args': args,
            'kwargs': kwargs
        }
        
        result = await batch_processor.add_to_batch(request_data)
        
        # 응답 압축
        if isinstance(result, dict):
            result = compressor.compress_response(result)
        
        return result
    
    return optimized_wrapper


def get_performance_stats() -> Dict[str, Any]:
    """성능 통계 반환"""
    stats = optimizer.performance_stats.copy()
    stats.update({
        'cache_size': len(optimizer.response_cache),
        'cache_hit_rate': (
            stats['cache_hits'] / max(stats['total_requests'], 1) * 100
        ),
        'slow_request_rate': (
            stats['slow_requests'] / max(stats['total_requests'], 1) * 100
        )
    })
    return stats


async def warm_up_system():
    """시스템 워밍업"""
    logger.info("🔥 시스템 워밍업 시작...")
    
    try:
        # 데이터베이스 연결 최적화
        from database import db_manager
        db_mgr = db_manager()
        if db_mgr and hasattr(db_mgr, 'memories_collection'):
            await db_optimizer.optimize_mongodb_queries(db_mgr.memories_collection)
        
        # 메모리 인덱스 구축
        # (실제 메모리 데이터가 있을 때 구축)
        
        logger.info("✅ 시스템 워밍업 완료")
        
    except Exception as e:
        logger.error(f"❌ 시스템 워밍업 실패: {e}")


# 시스템 시작 시 워밍업
async def initialize_optimizer():
    """최적화 시스템 초기화"""
    try:
        await warm_up_system()
        print("✅ 성능 최적화 시스템 준비 완료")
    except Exception as e:
        print(f"❌ 최적화 시스템 초기화 실패: {e}")
        # 에러가 발생해도 시스템이 중단되지 않도록 함 