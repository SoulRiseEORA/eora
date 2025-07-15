"""
memory_db.py

EORA 시스템용 메모리 데이터베이스 모듈
- MongoDB 기반 메모리 저장 및 검색
- 간단한 로컬 파일 기반 fallback 지원
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import threading

logger = logging.getLogger(__name__)

# 전역 설정
MEMORY_DB_FILE = "memory_db.json"
MEMORY_LOCK = threading.Lock()

class MemoryDB:
    """메모리 데이터베이스 클래스"""
    
    def __init__(self, use_mongodb: bool = True):
        self.use_mongodb = use_mongodb
        self.mongo_client = None
        self.mongo_db = None
        self.memory_file = MEMORY_DB_FILE
        
        if use_mongodb:
            self._init_mongodb()
        else:
            self._init_file_db()
    
    def _init_mongodb(self):
        """MongoDB 초기화"""
        try:
            from pymongo import MongoClient
            self.mongo_client = MongoClient('mongodb://localhost:27017/')
            self.mongo_db = self.mongo_client['EORA']
            logger.info("✅ MongoDB 연결 성공")
        except Exception as e:
            logger.warning(f"⚠️ MongoDB 연결 실패: {str(e)}")
            logger.info("📁 로컬 파일 기반 메모리로 fallback")
            self.use_mongodb = False
            self._init_file_db()
    
    def _init_file_db(self):
        """로컬 파일 기반 DB 초기화"""
        try:
            if not os.path.exists(self.memory_file):
                with open(self.memory_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 로컬 메모리 파일 초기화: {self.memory_file}")
        except Exception as e:
            logger.error(f"❌ 로컬 메모리 파일 초기화 실패: {str(e)}")
    
    def save_chunk(self, category: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        메모리 청크 저장
        
        Args:
            category (str): 메모리 카테고리
            content (str): 저장할 내용
            metadata (Optional[Dict]): 추가 메타데이터
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            if not content or not content.strip():
                return False
            
            timestamp = datetime.utcnow().isoformat()
            chunk_data = {
                "category": category,
                "content": content.strip(),
                "timestamp": timestamp,
                "metadata": metadata or {}
            }
            
            if self.use_mongodb and self.mongo_db is not None:
                # MongoDB 저장
                collection = self.mongo_db[category]
                result = collection.insert_one(chunk_data)
                logger.debug(f"✅ MongoDB 저장 성공: {category} - {result.inserted_id}")
                return True
            else:
                # 로컬 파일 저장
                with MEMORY_LOCK:
                    data = {}
                    if os.path.exists(self.memory_file):
                        with open(self.memory_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                    
                    if category not in data:
                        data[category] = []
                    
                    data[category].append(chunk_data)
                    
                    with open(self.memory_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    logger.debug(f"✅ 로컬 파일 저장 성공: {category}")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ 메모리 저장 실패: {str(e)}")
            return False
    
    def search_chunks(self, category: str, query: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """
        메모리 청크 검색
        
        Args:
            category (str): 검색할 카테고리
            query (str): 검색 쿼리 (선택사항)
            limit (int): 최대 결과 수
            
        Returns:
            List[Dict]: 검색 결과
        """
        try:
            if self.use_mongodb and self.mongo_db is not None:
                # MongoDB 검색
                collection = self.mongo_db[category]
                if query:
                    # 텍스트 검색 (간단한 키워드 매칭)
                    results = collection.find({"content": {"$regex": query, "$options": "i"}})
                else:
                    results = collection.find()
                
                return list(results.limit(limit))
            else:
                # 로컬 파일 검색
                with MEMORY_LOCK:
                    if not os.path.exists(self.memory_file):
                        return []
                    
                    with open(self.memory_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if category not in data:
                        return []
                    
                    chunks = data[category]
                    
                    if query:
                        # 간단한 키워드 검색
                        filtered_chunks = []
                        query_lower = query.lower()
                        for chunk in chunks:
                            if query_lower in chunk.get("content", "").lower():
                                filtered_chunks.append(chunk)
                        chunks = filtered_chunks
                    
                    # 최신순 정렬
                    chunks.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                    return chunks[:limit]
                    
        except Exception as e:
            logger.error(f"❌ 메모리 검색 실패: {str(e)}")
            return []
    
    def get_all_categories(self) -> List[str]:
        """모든 카테고리 목록 반환"""
        try:
            if self.use_mongodb and self.mongo_db is not None:
                return self.mongo_db.list_collection_names()
            else:
                with MEMORY_LOCK:
                    if not os.path.exists(self.memory_file):
                        return []
                    
                    with open(self.memory_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    return list(data.keys())
                    
        except Exception as e:
            logger.error(f"❌ 카테고리 목록 조회 실패: {str(e)}")
            return []
    
    def clear_category(self, category: str) -> bool:
        """특정 카테고리 전체 삭제"""
        try:
            if self.use_mongodb and self.mongo_db is not None:
                collection = self.mongo_db[category]
                collection.delete_many({})
                logger.info(f"✅ MongoDB 카테고리 삭제: {category}")
                return True
            else:
                with MEMORY_LOCK:
                    if not os.path.exists(self.memory_file):
                        return False
                    
                    with open(self.memory_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if category in data:
                        del data[category]
                        
                        with open(self.memory_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        
                        logger.info(f"✅ 로컬 파일 카테고리 삭제: {category}")
                        return True
                    
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 카테고리 삭제 실패: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """메모리 통계 정보"""
        try:
            categories = self.get_all_categories()
            stats = {
                "total_categories": len(categories),
                "categories": {},
                "storage_type": "mongodb" if self.use_mongodb else "local_file"
            }
            
            for category in categories:
                chunks = self.search_chunks(category, limit=1000)
                stats["categories"][category] = len(chunks)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ 통계 조회 실패: {str(e)}")
            return {}

# 전역 인스턴스
_memory_db = None

def get_memory_db() -> MemoryDB:
    """메모리 DB 인스턴스 반환 (싱글톤)"""
    global _memory_db
    if _memory_db is None:
        _memory_db = MemoryDB()
    return _memory_db

# 편의 함수들
def save_chunk(category: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
    """메모리 청크 저장 (편의 함수)"""
    return get_memory_db().save_chunk(category, content, metadata)

def search_chunks(category: str, query: str = "", limit: int = 10) -> List[Dict[str, Any]]:
    """메모리 청크 검색 (편의 함수)"""
    return get_memory_db().search_chunks(category, query, limit)

def get_all_categories() -> List[str]:
    """모든 카테고리 목록 (편의 함수)"""
    return get_memory_db().get_all_categories()

def clear_category(category: str) -> bool:
    """카테고리 삭제 (편의 함수)"""
    return get_memory_db().clear_category(category)

def get_memory_stats() -> Dict[str, Any]:
    """메모리 통계 (편의 함수)"""
    return get_memory_db().get_stats()

# 테스트 함수
def test_memory_db():
    """메모리 DB 테스트"""
    print("=== Memory DB 테스트 ===")
    
    # 테스트 데이터 저장
    test_categories = ["테스트", "학습", "대화"]
    for category in test_categories:
        for i in range(3):
            content = f"{category} 테스트 내용 {i+1}"
            success = save_chunk(category, content)
            print(f"저장: {category} - {content} - {'성공' if success else '실패'}")
    
    # 검색 테스트
    for category in test_categories:
        results = search_chunks(category, limit=5)
        print(f"검색 결과 ({category}): {len(results)}개")
    
    # 통계 테스트
    stats = get_memory_stats()
    print(f"통계: {stats}")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_memory_db() 