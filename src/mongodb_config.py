"""
Railway 환경 최적화 MongoDB 설정 통합 관리자
모든 모듈에서 사용할 수 있는 통합 MongoDB 연결 관리
"""

import os
import logging
from pymongo import MongoClient
from typing import Optional

logger = logging.getLogger(__name__)

# 전역 MongoDB 클라이언트 캐시
_cached_mongo_client = None
_cached_db = None

def get_optimized_mongodb_connection() -> Optional[MongoClient]:
    """Railway 환경에 최적화된 MongoDB 연결을 반환합니다."""
    global _cached_mongo_client
    
    if _cached_mongo_client is not None:
        try:
            # 연결 상태 확인
            _cached_mongo_client.admin.command('ping')
            return _cached_mongo_client
        except Exception:
            logger.warning("🔄 기존 MongoDB 연결이 끊어져 재연결을 시도합니다.")
            _cached_mongo_client = None
    
    # Railway 환경 감지
    is_railway = bool(os.getenv("RAILWAY_ENVIRONMENT") or 
                     os.getenv("RAILWAY_PROJECT_ID") or 
                     os.getenv("RAILWAY_SERVICE_ID") or
                     "railway.app" in os.getenv("RAILWAY_PUBLIC_DOMAIN", ""))
    
    # 연결 URL 목록 (Railway 환경에서는 Railway URL 우선)
    urls_to_try = []
    
    if is_railway:
        # Railway 환경: Railway MongoDB URL 우선
        railway_urls = [
            os.getenv("MONGO_PUBLIC_URL"),
            os.getenv("MONGO_URL"), 
            "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594",
            "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@mongodb.railway.internal:27017"
        ]
        urls_to_try.extend([url for url in railway_urls if url])
    else:
        # 로컬 환경: localhost 우선
        local_urls = [
            os.getenv("MONGODB_URI"),
            "mongodb://localhost:27017",
            "mongodb://127.0.0.1:27017"
        ]
        urls_to_try.extend([url for url in local_urls if url])
    
    # 연결 시도
    for url in urls_to_try:
        try:
            client = MongoClient(
                url,
                serverSelectionTimeoutMS=2000,  # 2초로 단축
                connectTimeoutMS=2000,
                socketTimeoutMS=2000,
                maxPoolSize=10,
                minPoolSize=1
            )
            
            # 연결 테스트
            client.admin.command('ping')
            
            logger.info(f"✅ MongoDB 연결 성공: {url.split('@')[-1] if '@' in url else url}")
            _cached_mongo_client = client
            return client
            
        except Exception as e:
            logger.warning(f"⚠️ MongoDB 연결 실패: {url.split('@')[-1] if '@' in url else url} - {e}")
            continue
    
    logger.error("❌ 모든 MongoDB 연결 시도 실패")
    return None

def get_optimized_database(db_name: str = "eora_ai"):
    """최적화된 데이터베이스 인스턴스를 반환합니다."""
    global _cached_db
    
    if _cached_db is not None:
        return _cached_db
    
    client = get_optimized_mongodb_connection()
    if client:
        _cached_db = client[db_name]
        return _cached_db
    
    return None

def reset_mongodb_cache():
    """MongoDB 캐시를 초기화합니다."""
    global _cached_mongo_client, _cached_db
    _cached_mongo_client = None
    _cached_db = None

# 하위 호환성을 위한 함수들
def get_mongo_client():
    """하위 호환성을 위한 함수"""
    return get_optimized_mongodb_connection()

def get_database(db_name: str = "eora_ai"):
    """하위 호환성을 위한 함수"""
    return get_optimized_database(db_name) 