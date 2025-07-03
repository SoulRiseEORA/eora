"""
aura_system.memory_store

메모리 저장소 모듈
- 메모리 저장 및 검색
- 메타데이터 관리
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class MemoryStore:
    """메모리 저장소 클래스"""
    
    def __init__(self):
        self.memories = {}
        self.metadata = {}
    
    def store_memory(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        메모리 저장
        
        Args:
            content (str): 저장할 내용
            metadata (Optional[Dict]): 메타데이터
            
        Returns:
            str: 메모리 ID
        """
        try:
            memory_id = str(uuid.uuid4())
            
            memory_data = {
                "id": memory_id,
                "content": content,
                "metadata": metadata or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.memories[memory_id] = memory_data
            logger.debug(f"메모리 저장 성공: {memory_id}")
            
            return memory_id
            
        except Exception as e:
            logger.error(f"메모리 저장 실패: {str(e)}")
            return ""
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        메모리 조회
        
        Args:
            memory_id (str): 메모리 ID
            
        Returns:
            Optional[Dict]: 메모리 데이터
        """
        return self.memories.get(memory_id)
    
    def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        메모리 검색
        
        Args:
            query (str): 검색 쿼리
            limit (int): 최대 결과 수
            
        Returns:
            List[Dict]: 검색 결과
        """
        try:
            results = []
            query_lower = query.lower()
            
            for memory in self.memories.values():
                content = memory.get("content", "").lower()
                if query_lower in content:
                    results.append(memory)
            
            # 최신순 정렬
            results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"메모리 검색 실패: {str(e)}")
            return []
    
    def clear_memories(self) -> bool:
        """
        모든 메모리 삭제
        
        Returns:
            bool: 성공 여부
        """
        try:
            self.memories.clear()
            logger.info("모든 메모리 삭제 완료")
            return True
        except Exception as e:
            logger.error(f"메모리 삭제 실패: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        메모리 통계
        
        Returns:
            Dict: 통계 정보
        """
        return {
            "total_memories": len(self.memories),
            "oldest_memory": min([m.get("timestamp", "") for m in self.memories.values()], default=""),
            "newest_memory": max([m.get("timestamp", "") for m in self.memories.values()], default="")
        }

# 전역 인스턴스
_memory_store = None

def get_memory_store() -> MemoryStore:
    """메모리 저장소 인스턴스 반환 (싱글톤)"""
    global _memory_store
    if _memory_store is None:
        _memory_store = MemoryStore()
    return _memory_store

# 테스트 함수
def test_memory_store():
    """메모리 저장소 테스트"""
    print("=== Memory Store 테스트 ===")
    
    store = get_memory_store()
    
    # 메모리 저장 테스트
    test_memories = [
        "첫 번째 테스트 메모리",
        "두 번째 테스트 메모리",
        "세 번째 테스트 메모리"
    ]
    
    memory_ids = []
    for memory in test_memories:
        memory_id = store.store_memory(memory)
        memory_ids.append(memory_id)
        print(f"저장: {memory} - ID: {memory_id}")
    
    # 메모리 검색 테스트
    results = store.search_memories("테스트")
    print(f"검색 결과: {len(results)}개")
    
    # 통계 테스트
    stats = store.get_stats()
    print(f"통계: {stats}")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_memory_store() 