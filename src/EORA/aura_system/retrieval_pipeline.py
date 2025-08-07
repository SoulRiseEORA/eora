"""
aura_system.retrieval_pipeline

검색 파이프라인 모듈
- 메모리 검색
- 관련성 계산
"""

import logging
from typing import List, Dict, Any, Optional
from utils_lightweight import cosine_similarity, simple_embed

logger = logging.getLogger(__name__)

async def retrieve(query_embedding: List[float], keywords: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
    """
    메모리 검색
    
    Args:
        query_embedding (List[float]): 쿼리 임베딩
        keywords (List[str]): 키워드 목록
        top_k (int): 최대 결과 수
        
    Returns:
        List[Dict]: 검색 결과
    """
    try:
        # 간단한 더미 결과 반환
        results = []
        for i in range(min(top_k, 3)):
            results.append({
                "id": f"dummy_{i}",
                "content": f"더미 메모리 {i+1}",
                "similarity": 0.8 - (i * 0.1),
                "keywords": keywords[:2]
            })
        
        return results
        
    except Exception as e:
        logger.error(f"메모리 검색 실패: {str(e)}")
        return []

# 테스트 함수
def test_retrieval_pipeline():
    """검색 파이프라인 테스트"""
    print("=== Retrieval Pipeline 테스트 ===")
    
    query_embedding = simple_embed("테스트 쿼리")
    keywords = ["테스트", "검색"]
    
    import asyncio
    results = asyncio.run(retrieve(query_embedding, keywords))
    
    print(f"검색 결과: {len(results)}개")
    for result in results:
        print(f"- {result['content']} (유사도: {result['similarity']:.2f})")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_retrieval_pipeline() 