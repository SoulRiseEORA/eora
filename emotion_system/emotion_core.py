"""
감정 시스템의 핵심 모듈
"""

import logging
from typing import Dict, Any, Optional
from .emotion_logic_module import EmotionLogicModule, get_emotion_logic_module
from .emotion_memory_inserter import EmotionMemoryInserter, get_emotion_memory_inserter

logger = logging.getLogger(__name__)

class EmotionCore:
    """감정 시스템의 핵심 클래스"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.logic_module = get_emotion_logic_module()
        self.memory_inserter = get_emotion_memory_inserter()
        self._initialized = True
        logger.info("EmotionCore 초기화 완료")
    
    def process_emotion(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """감정 처리 메인 로직"""
        try:
            # 감정 분석
            emotion_result = self.logic_module.analyze_emotion(input_data)
            
            # 메모리 저장
            if emotion_result.get('should_store', False):
                self.memory_inserter.insert_emotion(emotion_result)
            
            return emotion_result
            
        except Exception as e:
            logger.error(f"감정 처리 중 오류 발생: {str(e)}")
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def get_emotion_state(self) -> Dict[str, Any]:
        """현재 감정 상태 반환"""
        return self.logic_module.get_current_state()
    
    def reset_emotion_state(self) -> None:
        """감정 상태 초기화"""
        self.logic_module.reset_state()
        logger.info("감정 상태가 초기화되었습니다.")

def get_emotion_core() -> EmotionCore:
    """EmotionCore 싱글톤 인스턴스 반환"""
    return EmotionCore() 