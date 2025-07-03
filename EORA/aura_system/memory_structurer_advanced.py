"""
aura_system.memory_structurer_advanced

고급 메모리 구조화 모듈
- 감정 분석
- 신념 벡터 추출
"""

import logging
from typing import List, Dict, Any
from utils_lightweight import simple_emotion, extract_keywords

logger = logging.getLogger(__name__)

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
            # 감정이 감지되면 기본 강도 0.5 반환
            return 0.5
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
        
        # 키워드 기반 간단한 신념 벡터 생성
        keywords = extract_keywords(text, max_keywords=10)
        
        # 10차원 벡터로 변환
        vector = [0.0] * 10
        for i, keyword in enumerate(keywords[:10]):
            vector[i] = 0.1 + (i * 0.05)  # 키워드별로 다른 가중치
        
        return vector
        
    except Exception as e:
        logger.error(f"신념 벡터 추출 실패: {str(e)}")
        return [0.0] * 10

# 테스트 함수
def test_memory_structurer():
    """메모리 구조화 테스트"""
    print("=== Memory Structurer 테스트 ===")
    
    test_texts = [
        "나는 정말 기쁘고 행복하다",
        "오늘은 슬프고 우울하다",
        "인공지능에 대해 궁금하다"
    ]
    
    for text in test_texts:
        emotion_score = estimate_emotion(text)
        belief_vector = extract_belief_vector(text)
        
        print(f"텍스트: {text}")
        print(f"감정 강도: {emotion_score}")
        print(f"신념 벡터: {belief_vector[:5]}")
        print()
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_memory_structurer() 