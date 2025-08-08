"""
aura_system.resonance_engine

공명 엔진 모듈
- 공명 계산
- 감정 분석
- 신념 벡터 추출
"""

import logging
from typing import List, Dict, Any
from utils_lightweight import cosine_similarity, simple_emotion, extract_keywords

logger = logging.getLogger(__name__)

def calculate_resonance(vec1: List[float], vec2: List[float]) -> float:
    """
    두 벡터 간의 공명 계산
    
    Args:
        vec1 (List[float]): 첫 번째 벡터
        vec2 (List[float]): 두 번째 벡터
        
    Returns:
        float: 공명 점수 (0-1)
    """
    try:
        if not vec1 or not vec2:
            return 0.0
        
        # 코사인 유사도를 공명 점수로 사용
        return cosine_similarity(vec1, vec2)
        
    except Exception as e:
        logger.error(f"공명 계산 실패: {str(e)}")
        return 0.0

def estimate_emotion(text: str) -> float:
    """
    감정 강도 추정
    
    Args:
        text (str): 분석할 텍스트
        
    Returns:
        float: 감정 강도 (0-1)
    """
    try:
        if not text:
            return 0.0
        
        emotion = simple_emotion(text)
        if emotion:
            return 0.5  # 기본 감정 강도
        return 0.0
        
    except Exception as e:
        logger.error(f"감정 분석 실패: {str(e)}")
        return 0.0

def extract_belief_vector(text: str) -> List[float]:
    """
    신념 벡터 추출
    
    Args:
        text (str): 분석할 텍스트
        
    Returns:
        List[float]: 신념 벡터
    """
    try:
        if not text:
            return [0.0] * 10
        
        keywords = extract_keywords(text, max_keywords=10)
        
        # 10차원 벡터로 변환
        vector = [0.0] * 10
        for i, keyword in enumerate(keywords[:10]):
            vector[i] = 0.1 + (i * 0.05)
        
        return vector
        
    except Exception as e:
        logger.error(f"신념 벡터 추출 실패: {str(e)}")
        return [0.0] * 10

def embed_text(text: str) -> List[float]:
    """
    텍스트 임베딩 (별칭)
    
    Args:
        text (str): 임베딩할 텍스트
        
    Returns:
        List[float]: 임베딩 벡터
    """
    from .vector_store import embed_text as _embed_text
    return _embed_text(text)

# 테스트 함수
def test_resonance_engine():
    """공명 엔진 테스트"""
    print("=== Resonance Engine 테스트 ===")
    
    # 벡터 생성
    vec1 = [1.0, 0.5, 0.3, 0.8, 0.2]
    vec2 = [0.8, 0.4, 0.2, 0.9, 0.1]
    
    # 공명 계산
    resonance = calculate_resonance(vec1, vec2)
    print(f"공명 점수: {resonance:.3f}")
    
    # 감정 분석
    test_text = "나는 정말 기쁘고 행복하다"
    emotion_score = estimate_emotion(test_text)
    print(f"감정 강도: {emotion_score}")
    
    # 신념 벡터
    belief_vector = extract_belief_vector(test_text)
    print(f"신념 벡터: {belief_vector[:5]}")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_resonance_engine() 