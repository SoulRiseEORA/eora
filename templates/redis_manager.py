#!/usr/bin/env python3
"""
Redis 연결 관리자
Redis 연결 실패 시 graceful fallback을 제공합니다.
"""

import os
import logging
from typing import Optional, Any
import redis.asyncio as redis
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class RedisManager:
    """Redis 연결을 안전하게 관리하는 클래스"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.is_connected = False
        self.fallback_mode = False
        
    async def initialize(self) -> bool:
        """Redis 연결을 초기화합니다."""
        try:
            # 환경 변수에서 Redis 설정 가져오기
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            redis_password = os.getenv('REDIS_PASSWORD')
            redis_db = int(os.getenv('REDIS_DB', 0))
            
            # Redis 클라이언트 생성
            if redis_url != 'redis://localhost:6379':
                # Railway 등에서 제공하는 Redis URL 사용
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
            else:
                # 로컬 Redis 연결
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    password=redis_password,
                    db=redis_db,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
            
            # 연결 테스트
            await self.redis_client.ping()
            self.is_connected = True
            self.fallback_mode = False
            logger.info("✅ Redis 연결 성공")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Redis 연결 실패: {e}")
            logger.info("🔄 Redis 없이 메모리 모드로 실행됩니다.")
            self.is_connected = False
            self.fallback_mode = True
            return False
    
    async def close(self):
        """Redis 연결을 종료합니다."""
        if self.redis_client and self.is_connected:
            try:
                await self.redis_client.close()
                logger.info("Redis 연결 종료")
            except Exception as e:
                logger.error(f"Redis 연결 종료 중 오류: {e}")
    
    async def get(self, key: str, default: Any = None) -> Any:
        """키 값을 가져옵니다."""
        if not self.is_connected:
            return default
        
        try:
            value = await self.redis_client.get(key)
            return value if value is not None else default
        except Exception as e:
            logger.warning(f"Redis GET 오류 ({key}): {e}")
            return default
    
    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """키 값을 설정합니다."""
        if not self.is_connected:
            return False
        
        try:
            await self.redis_client.set(key, value, ex=ex)
            return True
        except Exception as e:
            logger.warning(f"Redis SET 오류 ({key}): {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """키를 삭제합니다."""
        if not self.is_connected:
            return False
        
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Redis DELETE 오류 ({key}): {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """키가 존재하는지 확인합니다."""
        if not self.is_connected:
            return False
        
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.warning(f"Redis EXISTS 오류 ({key}): {e}")
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """키에 만료 시간을 설정합니다."""
        if not self.is_connected:
            return False
        
        try:
            return await self.redis_client.expire(key, seconds)
        except Exception as e:
            logger.warning(f"Redis EXPIRE 오류 ({key}): {e}")
            return False

# 전역 Redis 매니저 인스턴스
redis_manager = RedisManager()

@asynccontextmanager
async def get_redis():
    """Redis 연결을 안전하게 제공하는 컨텍스트 매니저"""
    if redis_manager.is_connected:
        yield redis_manager
    else:
        yield None 