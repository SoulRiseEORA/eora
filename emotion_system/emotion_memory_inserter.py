"""
감정 메모리 저장 모듈
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class EmotionMemoryInserter:
    """감정 메모리 저장 클래스"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.memory_store = []
        self._initialized = True
        logger.info("EmotionMemoryInserter 초기화 완료")
    
    def insert_emotion(self, emotion_data: Dict[str, Any]) -> bool:
        """감정 데이터를 메모리에 저장"""
        try:
            # 메모리에 감정 데이터 저장
            self.memory_store.append(emotion_data)
            logger.info(f"감정 데이터 저장 완료: {emotion_data['emotion']}")
            return True
            
        except Exception as e:
            logger.error(f"감정 데이터 저장 중 오류 발생: {str(e)}")
            return False
    
    def get_memory_store(self) -> list:
        """저장된 메모리 반환"""
        return self.memory_store.copy()
    
    def clear_memory(self) -> None:
        """메모리 초기화"""
        self.memory_store = []
        logger.info("감정 메모리가 초기화되었습니다.")

def get_emotion_memory_inserter() -> EmotionMemoryInserter:
    """EmotionMemoryInserter 싱글톤 인스턴스 반환"""
    return EmotionMemoryInserter() 