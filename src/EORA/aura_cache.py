'''Redis 기반 AURA 회상 정보 캐싱 모듈
- redis-py의 asyncio 서브패키지(redis.asyncio)를 통한 비동기 Redis 접속
- 자주 회상되는 결과를 캐시에 저장하여 성능 향상
- TTL(유효기간) 설정으로 오래된 기억 자동 삭제'''''
import os
import json
import asyncio
import time  # ensure time is available for sleep
try:
    import redis.asyncio as redis  # redis-py 4.x asyncio 지원
except ImportError:
    # fallback to aioredis if redis.asyncio not available
    import aioredis as redis

# 환경 변수 또는 기본 설정
REDIS_URI = os.getenv("REDIS_URI", "redis://localhost:6379/0")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 기본 1시간 TTL

_redis = None

async def init_cache_pool():
    """Redis 연결 풀 초기화"""
    global _redis
    if _redis is None:
        _redis = await redis.from_url(REDIS_URI)
    return _redis

async def get_cached_recall(keyword: str):
    """키워드에 대한 캐시된 회상 정보 반환 (없으면 None)"""
    try:
        r = await init_cache_pool()
        data = await r.get(f"recall:{keyword}")
        if not data:
            return None
        return json.loads(data)
    except Exception:
        # 첫 호출 실패 시 짧게 대기 후 재시도
        time.sleep(0.1)
        try:
            r = await init_cache_pool()
            data = await r.get(f"recall:{keyword}")
            if data:
                return json.loads(data)
        except Exception:
            return None
        return None

async def set_cached_recall(keyword: str, value, ttl: int = None):
    """키워드에 대한 회상 정보를 캐시에 저장 (TTL 적용)"""
    try:
        r = await init_cache_pool()
        payload = json.dumps(value)
        expire = ttl or CACHE_TTL_SECONDS
        await r.set(f"recall:{keyword}", payload, ex=expire)
        return True
    except Exception as e:
        print(f"[aura_cache] 캐시 저장 오류: {e}")
        return False
