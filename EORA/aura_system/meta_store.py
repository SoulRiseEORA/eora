"""
aura_system.meta_store

메타데이터 저장소 모듈
- 메타데이터 관리
- 원자 단위 데이터 접근
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def get_all_atoms() -> List[Dict[str, Any]]:
    """
    모든 원자 데이터 반환
    
    Returns:
        List[Dict]: 원자 데이터 목록
    """
    try:
        # 간단한 더미 데이터 반환
        atoms = [
            {
                "id": "atom_1",
                "type": "memory",
                "content": "첫 번째 원자 메모리",
                "metadata": {"created": "2024-01-01"}
            },
            {
                "id": "atom_2", 
                "type": "emotion",
                "content": "기쁨",
                "metadata": {"intensity": 0.8}
            },
            {
                "id": "atom_3",
                "type": "belief",
                "content": "인공지능은 유용하다",
                "metadata": {"confidence": 0.9}
            }
        ]
        
        return atoms
        
    except Exception as e:
        logger.error(f"원자 데이터 조회 실패: {str(e)}")
        return []

# 테스트 함수
def test_meta_store():
    """메타 저장소 테스트"""
    print("=== Meta Store 테스트 ===")
    
    atoms = get_all_atoms()
    print(f"원자 데이터: {len(atoms)}개")
    
    for atom in atoms:
        print(f"- {atom['type']}: {atom['content']}")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_meta_store() 