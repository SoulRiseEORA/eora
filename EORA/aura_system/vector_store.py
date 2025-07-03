"""
aura_system.vector_store

벡터 저장소 모듈
- 텍스트 임베딩 생성
- 벡터 저장 및 검색
"""

import numpy as np
import hashlib
import logging
from typing import List, Optional
from utils_lightweight import simple_embed

logger = logging.getLogger(__name__)

def embed_text(text: str) -> List[float]:
    """
    텍스트를 벡터로 임베딩
    
    Args:
        text (str): 임베딩할 텍스트
        
    Returns:
        List[float]: 임베딩 벡터
    """
    try:
        if not text or not isinstance(text, str):
            return [0.0] * 128
        
        # utils_lightweight의 simple_embed 사용
        return simple_embed(text)
        
    except Exception as e:
        logger.error(f"임베딩 생성 실패: {str(e)}")
        return [0.0] * 128

async def embed_text_async(text: str) -> List[float]:
    """
    비동기 텍스트 임베딩 (동기 버전과 동일)
    
    Args:
        text (str): 임베딩할 텍스트
        
    Returns:
        List[float]: 임베딩 벡터
    """
    return embed_text(text)

def get_embedding(text: str) -> List[float]:
    """
    임베딩 생성 (별칭 함수)
    
    Args:
        text (str): 임베딩할 텍스트
        
    Returns:
        List[float]: 임베딩 벡터
    """
    return embed_text(text)

# 테스트 함수
def test_vector_store():
    """벡터 저장소 테스트"""
    print("=== Vector Store 테스트 ===")
    
    test_texts = [
        "안녕하세요",
        "오늘 날씨가 좋네요",
        "인공지능에 대해 이야기해보세요"
    ]
    
    for text in test_texts:
        embedding = embed_text(text)
        print(f"텍스트: {text}")
        print(f"임베딩 차원: {len(embedding)}")
        print(f"임베딩 샘플: {embedding[:5]}")
        print()
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_vector_store() 