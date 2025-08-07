"""
aura_system.insight_engine
- 통찰 엔진 모듈
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import asyncio
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class BaseEngine:
    """기본 엔진 클래스"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.initialized = False
        self.logger = logging.getLogger(self.__class__.__name__)
        
    async def initialize(self) -> bool:
        try:
            self.initialized = True
            self.logger.info("✅ 엔진 초기화 완료")
            return True
        except Exception as e:
            self.logger.error(f"❌ 엔진 초기화 실패: {str(e)}")
            return False
            
    async def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.initialized:
            self.logger.error("❌ 엔진이 초기화되지 않았습니다.")
            return {}
            
        try:
            return {
                'status': 'success',
                'result': {}
            }
        except Exception as e:
            self.logger.error(f"❌ 데이터 처리 실패: {str(e)}")
            return {}

class InsightEngine(BaseEngine):
    """통찰 엔진"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.insight_store = {}
        self.cache = {}
        self.history = []
        self._cache_size = 1000
        self._max_history = 50
        
        logger.info("✅ InsightEngine 초기화 완료")

    async def generate_insights(self, memories: List[Dict[str, Any]]) -> List[str]:
        """회상된 메모리로부터 통찰을 생성합니다."""
        if not memories:
            return []
        insights = []
        # timestamp가 str/datetime 혼합일 때 항상 str로 변환해서 비교
        def _get_time_str(m):
            v = m.get("timestamp", "1970-01-01")
            if isinstance(v, str):
                return v
            elif hasattr(v, 'isoformat'):
                return v.isoformat()
            else:
                return str(v)
        latest_memory = max(memories, key=_get_time_str)
        content = latest_memory.get("content", "내용 없음")
        emotion = latest_memory.get("emotion_label", "중립")
        insight = f"최근 '{emotion}' 감정과 관련된 '{content[:20]}...' 내용이 회상되었습니다. 이는 현재 대화 주제와 연관이 있을 수 있습니다."
        insights.append(insight)
        return insights

    async def initialize(self):
        """시스템 초기화"""
        try:
            self.initialized = True
            logger.info("통찰 엔진 초기화 완료")
        except Exception as e:
            logger.error(f"통찰 엔진 초기화 실패: {str(e)}")
            raise
            
    async def process_insight(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """통찰 처리 수행"""
        if not self.initialized:
            raise RuntimeError("시스템이 초기화되지 않았습니다.")
            
        try:
            # 통찰 처리 로직 구현
            return {
                "insight_level": 0.9,
                "understanding_depth": "deep",
                "context": context
            }
        except Exception as e:
            logger.error(f"통찰 처리 실패: {str(e)}")
            raise

def analyze_cognitive_layer(text: str) -> str:
    """텍스트의 인지적 계층을 분석합니다."""
    text = text.lower()
    if any(keyword in text for keyword in ["기억", "회상", "정보", "사실"]):
        return "기억(Memory)"
    if any(keyword in text for keyword in ["감정", "느낌", "기분", "슬픔", "기쁨"]):
        return "감정(Emotion)"
    if any(keyword in text for keyword in ["존재", "의미", "자아", "초월", "진리"]):
        return "초월(Transcendence)"
    return "일반(General)"

# 싱글톤 인스턴스
_insight_engine = None

def get_insight_engine() -> InsightEngine:
    """통찰 엔진 인스턴스 반환"""
    global _insight_engine
    if _insight_engine is None:
        _insight_engine = InsightEngine()
    return _insight_engine 