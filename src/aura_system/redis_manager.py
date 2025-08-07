"""
redis_manager.py
- Redis 서버 관리
- Redis 연결 및 설정 관리
- 비동기 처리 지원
"""

import os
import json
import logging
import asyncio
import atexit
from typing import Dict, Any, Optional, List
from pathlib import Path
from redis.asyncio import Redis
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisManager:
    """Redis 서버 관리 클래스"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self.redis_client = None
            self.redis_db = None
            self._load_config()
            atexit.register(self._sync_cleanup)

    def _sync_cleanup(self):
        """동기식 정리 함수"""
        try:
            if self.redis_client:
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        loop.create_task(self._async_cleanup())
                    else:
                        loop.run_until_complete(self._async_cleanup())
                except RuntimeError:
                    # 이벤트 루프가 없는 경우 새로 생성
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(self._async_cleanup())
                    finally:
                        try:
                            loop.stop()
                            loop.close()
                        except Exception as e:
                            logger.error(f"이벤트 루프 종료 중 오류 발생: {str(e)}")
        except Exception as e:
            logger.error(f"Redis 정리 중 오류 발생: {str(e)}")

    async def _async_cleanup(self):
        """비동기 정리 함수"""
        try:
            if self.redis_client:
                await self.redis_client.close()
                self.redis_client = None
                logger.info("Redis 연결 종료")
        except Exception as e:
            logger.error(f"Redis 정리 중 오류 발생: {str(e)}")

    def __del__(self):
        """소멸자"""
        try:
            self._sync_cleanup()
        except Exception as e:
            logger.error(f"Redis 소멸자에서 오류 발생: {str(e)}")

    def _load_config(self):
        """Redis 설정 로드"""
        try:
            # .env 파일 로드
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
            load_dotenv(env_path)
            
            # Redis 설정
            self.redis_host = os.getenv('REDIS_HOST', 'localhost')
            self.redis_port = int(os.getenv('REDIS_PORT', 6379))
            self.redis_db = int(os.getenv('REDIS_DB', 0))
            self.redis_password = os.getenv('REDIS_PASSWORD', None)
            
            logger.info(f"Redis 설정 로드 완료: {self.redis_host}:{self.redis_port}")
        except Exception as e:
            logger.error(f"Redis 설정 로드 중 오류 발생: {str(e)}")
            raise

    async def initialize(self):
        """Redis 연결 초기화"""
        try:
            if not self.redis_client:
                self.redis_client = Redis(
                    host=self.redis_host,
                    port=self.redis_port,
                    db=self.redis_db,
                    password=self.redis_password,
                    decode_responses=True
                )
                # 연결 테스트
                await self.redis_client.ping()
                logger.info("Redis 연결 성공")
        except Exception as e:
            logger.error(f"Redis 연결 중 오류 발생: {str(e)}")
            raise

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """데이터 저장"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return await self.redis_client.set(key, value, ex=expire)
        except Exception as e:
            logger.error(f"Redis 데이터 저장 중 오류 발생: {str(e)}")
            return False

    async def get(self, key: str) -> Any:
        """데이터 조회"""
        try:
            value = await self.redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"Redis 데이터 조회 중 오류 발생: {str(e)}")
            return None

    async def delete(self, key: str) -> bool:
        """데이터 삭제"""
        try:
            return bool(await self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Redis 데이터 삭제 중 오류 발생: {str(e)}")
            return False

    async def close(self):
        """Redis 연결 종료"""
        try:
            if self.redis_client:
                await self.redis_client.close()
                self.redis_client = None
                logger.info("Redis 연결 종료")
        except Exception as e:
            logger.error(f"Redis 연결 종료 중 오류 발생: {str(e)}")

# 싱글톤 인스턴스
_redis_manager = None

def get_redis_manager() -> RedisManager:
    """Redis 관리자 인스턴스 반환"""
    global _redis_manager
    if _redis_manager is None:
        _redis_manager = RedisManager()
    return _redis_manager 