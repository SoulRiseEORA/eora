"""
aura_system.memory_manager

메모리 관리자 모듈
- 메모리 관리
- 메모리 정리
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MemoryManager:
    """메모리 관리자 클래스"""
    
    def __init__(self):
        self.memories = {}
        self.categories = {}
    
    def add_memory(self, category: str, content: str, metadata: Dict[str, Any] = None) -> str:
        """
        메모리 추가
        
        Args:
            category (str): 메모리 카테고리
            content (str): 메모리 내용
            metadata (Dict): 메타데이터
            
        Returns:
            str: 메모리 ID
        """
        try:
            import uuid
            memory_id = str(uuid.uuid4())
            
            memory_data = {
                "id": memory_id,
                "category": category,
                "content": content,
                "metadata": metadata or {},
                "timestamp": "2024-01-01T00:00:00"
            }
            
            self.memories[memory_id] = memory_data
            
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(memory_id)
            
            logger.debug(f"메모리 추가 성공: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"메모리 추가 실패: {str(e)}")
            return ""
    
    def get_memories(self, category: str = None) -> List[Dict[str, Any]]:
        """
        메모리 조회
        
        Args:
            category (str): 카테고리 (선택사항)
            
        Returns:
            List[Dict]: 메모리 목록
        """
        try:
            if category:
                if category not in self.categories:
                    return []
                
                memory_ids = self.categories[category]
                return [self.memories.get(mid, {}) for mid in memory_ids]
            else:
                return list(self.memories.values())
                
        except Exception as e:
            logger.error(f"메모리 조회 실패: {str(e)}")
            return []
    
    def clear_memories(self, category: str = None) -> bool:
        """
        메모리 정리
        
        Args:
            category (str): 카테고리 (선택사항)
            
        Returns:
            bool: 성공 여부
        """
        try:
            if category:
                if category in self.categories:
                    memory_ids = self.categories[category]
                    for mid in memory_ids:
                        if mid in self.memories:
                            del self.memories[mid]
                    del self.categories[category]
                    logger.info(f"카테고리 '{category}' 메모리 정리 완료")
            else:
                self.memories.clear()
                self.categories.clear()
                logger.info("모든 메모리 정리 완료")
            
            return True
            
        except Exception as e:
            logger.error(f"메모리 정리 실패: {str(e)}")
            return False

# 전역 인스턴스
_memory_manager = None

def get_memory_manager() -> MemoryManager:
    """메모리 관리자 인스턴스 반환 (싱글톤)"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager

# 테스트 함수
def test_memory_manager():
    """메모리 관리자 테스트"""
    print("=== Memory Manager 테스트 ===")
    
    manager = get_memory_manager()
    
    # 메모리 추가
    test_memories = [
        ("학습", "파이썬 기초 학습"),
        ("대화", "사용자와의 대화 기록"),
        ("학습", "머신러닝 개념 학습")
    ]
    
    for category, content in test_memories:
        memory_id = manager.add_memory(category, content)
        print(f"메모리 추가: {category} - {content} - ID: {memory_id}")
    
    # 메모리 조회
    all_memories = manager.get_memories()
    print(f"전체 메모리: {len(all_memories)}개")
    
    learning_memories = manager.get_memories("학습")
    print(f"학습 메모리: {len(learning_memories)}개")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_memory_manager() 