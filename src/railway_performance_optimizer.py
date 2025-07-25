#!/usr/bin/env python3
"""
Railway 성능 최적화 모듈
- MongoDB 연결 최적화
- 캐싱 시스템 개선
- 비동기 처리 최적화
- 메모리 사용량 최적화
"""

import os
import asyncio
import logging
import time
from typing import Dict, Any, Optional
from functools import lru_cache
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

class RailwayPerformanceOptimizer:
    """Railway 환경 성능 최적화 클래스"""
    
    def __init__(self):
        self.mongo_client = None
        self.redis_client = None
        self.connection_cache = {}
        self.query_cache = {}
        self.max_cache_size = 1000
        self.cache_ttl = 300  # 5분
        
    async def optimize_mongodb_connection(self):
        """MongoDB 연결 최적화"""
        try:
            # Railway 환경 감지
            is_railway = bool(os.getenv("RAILWAY_ENVIRONMENT") or 
                             os.getenv("RAILWAY_PROJECT_ID") or 
                             os.getenv("RAILWAY_SERVICE_ID"))
            
            # 연결 URL 목록 (Railway 우선)
            urls_to_try = []
            if is_railway:
                railway_urls = [
                    os.getenv("MONGO_PUBLIC_URL"),
                    os.getenv("MONGO_URL"),
                    "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594"
                ]
                urls_to_try.extend([url for url in railway_urls if url])
            else:
                local_urls = [
                    os.getenv("MONGODB_URI"),
                    "mongodb://localhost:27017"
                ]
                urls_to_try.extend([url for url in local_urls if url])
            
            # 최적화된 연결 설정
            for url in urls_to_try:
                try:
                    # Railway 환경에서는 더 빠른 타임아웃 사용
                    timeout = 1000 if is_railway else 5000
                    
                    client = MongoClient(
                        url,
                        serverSelectionTimeoutMS=timeout,
                        connectTimeoutMS=timeout,
                        socketTimeoutMS=timeout,
                        maxPoolSize=5,  # Railway에서는 작은 풀 크기
                        minPoolSize=1,
                        maxIdleTimeMS=30000,  # 30초 후 연결 해제
                        waitQueueTimeoutMS=2000,  # 2초 대기
                        retryWrites=True,
                        retryReads=True
                    )
                    
                    # 연결 테스트
                    client.admin.command('ping')
                    
                    self.mongo_client = client
                    logger.info(f"✅ 최적화된 MongoDB 연결 성공: {url.split('@')[-1] if '@' in url else url}")
                    return client
                    
                except Exception as e:
                    logger.warning(f"⚠️ MongoDB 연결 실패: {url.split('@')[-1] if '@' in url else url} - {e}")
                    continue
            
            logger.error("❌ 모든 MongoDB 연결 시도 실패")
            return None
            
        except Exception as e:
            logger.error(f"❌ MongoDB 연결 최적화 실패: {e}")
            return None
    
    async def optimize_redis_connection(self):
        """Redis 연결 최적화"""
        try:
            # Railway 환경에서는 Redis 연결 풀 최적화
            is_railway = bool(os.getenv("RAILWAY_ENVIRONMENT"))
            
            pool_config = {
                'host': 'localhost',
                'port': 6379,
                'db': 0,
                'decode_responses': True,
                'socket_timeout': 1 if is_railway else 5,
                'socket_connect_timeout': 1 if is_railway else 5,
                'retry_on_timeout': True,
                'max_connections': 10 if is_railway else 50
            }
            
            self.redis_client = aioredis.Redis(**pool_config)
            await self.redis_client.ping()
            
            logger.info("✅ 최적화된 Redis 연결 성공")
            return self.redis_client
            
        except Exception as e:
            logger.warning(f"⚠️ Redis 연결 실패: {e}")
            return None
    
    @lru_cache(maxsize=100)
    def get_cached_query(self, query_key: str) -> Optional[Dict]:
        """쿼리 결과 캐싱"""
        return self.query_cache.get(query_key)
    
    def set_cached_query(self, query_key: str, result: Dict):
        """쿼리 결과 캐시 저장"""
        if len(self.query_cache) >= self.max_cache_size:
            # 가장 오래된 항목 제거
            oldest_key = next(iter(self.query_cache))
            del self.query_cache[oldest_key]
        
        self.query_cache[query_key] = {
            'result': result,
            'timestamp': time.time(),
            'ttl': self.cache_ttl
        }
    
    async def optimized_database_query(self, collection_name: str, query: Dict, limit: int = 10) -> list:
        """최적화된 데이터베이스 쿼리"""
        try:
            if not self.mongo_client:
                return []
            
            # 캐시 키 생성
            cache_key = f"{collection_name}:{hash(str(query))}:{limit}"
            cached_result = self.get_cached_query(cache_key)
            
            if cached_result and (time.time() - cached_result['timestamp']) < cached_result['ttl']:
                logger.info("✅ 캐시된 쿼리 결과 사용")
                return cached_result['result']
            
            # 실제 쿼리 실행
            collection = self.mongo_client.get_database().get_collection(collection_name)
            
            # Railway 환경에서는 더 작은 배치 크기 사용
            is_railway = bool(os.getenv("RAILWAY_ENVIRONMENT"))
            batch_size = 50 if is_railway else 100
            
            result = list(collection.find(query).limit(limit).batch_size(batch_size))
            
            # 결과 캐싱
            self.set_cached_query(cache_key, result)
            
            logger.info(f"✅ 최적화된 쿼리 실행 완료: {len(result)}개 결과")
            return result
            
        except Exception as e:
            logger.error(f"❌ 최적화된 쿼리 실패: {e}")
            return []
    
    async def optimize_memory_usage(self):
        """메모리 사용량 최적화"""
        try:
            # 캐시 크기 조정
            if len(self.query_cache) > self.max_cache_size * 0.8:
                # 오래된 캐시 항목 제거
                current_time = time.time()
                expired_keys = [
                    key for key, value in self.query_cache.items()
                    if (current_time - value['timestamp']) > value['ttl']
                ]
                
                for key in expired_keys:
                    del self.query_cache[key]
                
                logger.info(f"🧹 만료된 캐시 항목 {len(expired_keys)}개 제거")
            
            # MongoDB 연결 풀 정리
            if self.mongo_client:
                # 사용하지 않는 연결 정리
                self.mongo_client.close()
                logger.info("🧹 MongoDB 연결 풀 정리 완료")
            
            logger.info("✅ 메모리 사용량 최적화 완료")
            
        except Exception as e:
            logger.error(f"❌ 메모리 최적화 실패: {e}")
    
    async def optimize_async_operations(self):
        """비동기 작업 최적화"""
        try:
            # 동시 실행 제한 (Railway 환경에서는 더 작은 값)
            is_railway = bool(os.getenv("RAILWAY_ENVIRONMENT"))
            max_concurrent = 5 if is_railway else 20
            
            # 세마포어 생성
            semaphore = asyncio.Semaphore(max_concurrent)
            
            logger.info(f"✅ 비동기 작업 최적화 완료 (최대 동시 실행: {max_concurrent})")
            return semaphore
            
        except Exception as e:
            logger.error(f"❌ 비동기 작업 최적화 실패: {e}")
            return None

# 전역 최적화 인스턴스
performance_optimizer = RailwayPerformanceOptimizer()

async def initialize_railway_optimizations():
    """Railway 최적화 초기화"""
    try:
        logger.info("🚀 Railway 성능 최적화 초기화 시작...")
        
        # MongoDB 연결 최적화
        await performance_optimizer.optimize_mongodb_connection()
        
        # Redis 연결 최적화
        await performance_optimizer.optimize_redis_connection()
        
        # 비동기 작업 최적화
        await performance_optimizer.optimize_async_operations()
        
        logger.info("✅ Railway 성능 최적화 초기화 완료")
        
    except Exception as e:
        logger.error(f"❌ Railway 최적화 초기화 실패: {e}")

# 성능 모니터링 함수
def monitor_performance():
    """성능 모니터링"""
    try:
        import psutil
        
        # CPU 사용량
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 메모리 사용량
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # 디스크 사용량
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        logger.info(f"📊 성능 모니터링 - CPU: {cpu_percent}%, 메모리: {memory_percent}%, 디스크: {disk_percent}%")
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'disk_percent': disk_percent
        }
        
    except Exception as e:
        logger.error(f"❌ 성능 모니터링 실패: {e}")
        return None

if __name__ == "__main__":
    # 테스트 실행
    asyncio.run(initialize_railway_optimizations()) 