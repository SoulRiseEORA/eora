"""
EORA_Wisdom_Framework.memory_strategy_manager

메모리 전략 관리자
- 컨텍스트별 턴 제한 관리
- 메모리 전략 최적화
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# 컨텍스트별 턴 제한 설정
CONTEXT_TURN_LIMITS = {
    "general": 10,
    "learning": 20,
    "deep_conversation": 15,
    "quick_chat": 5,
    "analysis": 25,
    "creative": 30
}

def get_turn_limit_for_context(context: str) -> int:
    """
    컨텍스트별 턴 제한 반환
    
    Args:
        context (str): 컨텍스트 타입
        
    Returns:
        int: 턴 제한 수
    """
    try:
        return CONTEXT_TURN_LIMITS.get(context, CONTEXT_TURN_LIMITS["general"])
        
    except Exception as e:
        logger.error(f"턴 제한 조회 실패: {str(e)}")
        return CONTEXT_TURN_LIMITS["general"]

def analyze_context(text: str) -> str:
    """
    텍스트를 분석하여 컨텍스트 타입 결정
    
    Args:
        text (str): 분석할 텍스트
        
    Returns:
        str: 컨텍스트 타입
    """
    try:
        text_lower = text.lower()
        
        # 학습 관련 키워드
        if any(word in text_lower for word in ["학습", "배우", "교육", "훈련", "공부"]):
            return "learning"
        
        # 깊은 대화 관련 키워드
        elif any(word in text_lower for word in ["생각", "철학", "의미", "인생", "가치"]):
            return "deep_conversation"
        
        # 빠른 채팅 관련 키워드
        elif any(word in text_lower for word in ["안녕", "고마워", "잘가", "바이"]):
            return "quick_chat"
        
        # 분석 관련 키워드
        elif any(word in text_lower for word in ["분석", "검토", "평가", "조사", "연구"]):
            return "analysis"
        
        # 창의적 관련 키워드
        elif any(word in text_lower for word in ["창작", "아이디어", "상상", "발명", "혁신"]):
            return "creative"
        
        else:
            return "general"
            
    except Exception as e:
        logger.error(f"컨텍스트 분석 실패: {str(e)}")
        return "general"

def get_memory_strategy(context: str) -> Dict[str, Any]:
    """
    컨텍스트별 메모리 전략 반환
    
    Args:
        context (str): 컨텍스트 타입
        
    Returns:
        Dict: 메모리 전략
    """
    try:
        strategies = {
            "general": {
                "recall_limit": 5,
                "storage_priority": "medium",
                "retention_days": 7
            },
            "learning": {
                "recall_limit": 10,
                "storage_priority": "high",
                "retention_days": 30
            },
            "deep_conversation": {
                "recall_limit": 8,
                "storage_priority": "high",
                "retention_days": 14
            },
            "quick_chat": {
                "recall_limit": 3,
                "storage_priority": "low",
                "retention_days": 1
            },
            "analysis": {
                "recall_limit": 15,
                "storage_priority": "high",
                "retention_days": 60
            },
            "creative": {
                "recall_limit": 12,
                "storage_priority": "medium",
                "retention_days": 21
            }
        }
        
        return strategies.get(context, strategies["general"])
        
    except Exception as e:
        logger.error(f"메모리 전략 조회 실패: {str(e)}")
        return {
            "recall_limit": 5,
            "storage_priority": "medium",
            "retention_days": 7
        }

# 테스트 함수
def test_memory_strategy_manager():
    """메모리 전략 관리자 테스트"""
    print("=== Memory Strategy Manager 테스트 ===")
    
    # 컨텍스트 분석 테스트
    test_texts = [
        "파이썬을 배우고 싶어요",
        "인생의 의미에 대해 생각해보자",
        "안녕하세요!",
        "이 코드를 분석해주세요",
        "창의적인 아이디어가 필요해요"
    ]
    
    for text in test_texts:
        context = analyze_context(text)
        turn_limit = get_turn_limit_for_context(context)
        strategy = get_memory_strategy(context)
        
        print(f"텍스트: {text}")
        print(f"컨텍스트: {context}")
        print(f"턴 제한: {turn_limit}")
        print(f"전략: {strategy}")
        print()
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_memory_strategy_manager() 