"""
EORA_Wisdom_Framework.EORAInsightManagerV2

EORA 통찰 관리자 v2
- 통찰 생성 및 관리
- 지혜 기반 판단
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class EORAInsightManagerV2:
    """EORA 통찰 관리자 v2"""
    
    def __init__(self):
        self.insights = []
        self.wisdom_base = {
            "compassion": "자비심을 바탕으로 판단하라",
            "curiosity": "호기심을 유지하며 탐구하라",
            "courage": "용기를 가지고 도전하라",
            "wisdom": "지혜롭게 판단하라"
        }
    
    def generate_insight(self, context: str, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        통찰 생성
        
        Args:
            context (str): 현재 상황
            memories (List[Dict]): 관련 메모리들
            
        Returns:
            Dict: 생성된 통찰
        """
        try:
            insight = {
                "id": f"insight_{len(self.insights) + 1}",
                "context": context,
                "content": f"{context}에 대한 통찰: 지혜로운 판단이 필요합니다.",
                "wisdom_type": "general",
                "confidence": 0.7,
                "timestamp": datetime.utcnow().isoformat(),
                "related_memories": [m.get("id", "") for m in memories[:3]]
            }
            
            self.insights.append(insight)
            logger.debug(f"통찰 생성 완료: {insight['id']}")
            
            return insight
            
        except Exception as e:
            logger.error(f"통찰 생성 실패: {str(e)}")
            return {}
    
    def get_insights(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        통찰 목록 조회
        
        Args:
            limit (int): 최대 결과 수
            
        Returns:
            List[Dict]: 통찰 목록
        """
        try:
            # 최신순 정렬
            sorted_insights = sorted(self.insights, key=lambda x: x.get("timestamp", ""), reverse=True)
            return sorted_insights[:limit]
            
        except Exception as e:
            logger.error(f"통찰 조회 실패: {str(e)}")
            return []
    
    def apply_wisdom(self, situation: str) -> str:
        """
        지혜 적용
        
        Args:
            situation (str): 현재 상황
            
        Returns:
            str: 지혜로운 조언
        """
        try:
            # 상황에 맞는 지혜 선택
            if "도움" in situation or "어려움" in situation:
                return self.wisdom_base["compassion"]
            elif "궁금" in situation or "알고싶" in situation:
                return self.wisdom_base["curiosity"]
            elif "두려움" in situation or "걱정" in situation:
                return self.wisdom_base["courage"]
            else:
                return self.wisdom_base["wisdom"]
                
        except Exception as e:
            logger.error(f"지혜 적용 실패: {str(e)}")
            return "지혜로운 판단을 하세요."

# 테스트 함수
def test_insight_manager():
    """통찰 관리자 테스트"""
    print("=== Insight Manager 테스트 ===")
    
    manager = EORAInsightManagerV2()
    
    # 통찰 생성 테스트
    context = "사용자가 어려움을 겪고 있다"
    memories = [{"id": "mem_1", "content": "이전 도움 요청"}]
    
    insight = manager.generate_insight(context, memories)
    print(f"통찰 생성: {insight.get('content', '')}")
    
    # 지혜 적용 테스트
    wisdom = manager.apply_wisdom("사용자가 도움을 요청했다")
    print(f"지혜 조언: {wisdom}")
    
    # 통찰 목록 조회
    insights = manager.get_insights()
    print(f"통찰 개수: {len(insights)}")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_insight_manager() 