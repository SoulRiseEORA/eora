"""
emotion_core.py
- 감정 분석 코어 시스템
- 감정 레이블 추정 및 매칭
"""

import logging
from typing import Dict, Any, List, Tuple
import json
import os

logger = logging.getLogger(__name__)

class EmotionCore:
    """감정 분석 코어 시스템"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._cache = {}
            self._cache_size = 1000
            self._emotion_history = []
            self._max_history = 50
            
            # 감정 매핑 로드
            self._load_emotion_mappings()
            
            self._initialized = True
            logger.info("✅ EmotionCore 초기화 완료")
    
    def _load_emotion_mappings(self):
        """감정 매핑 데이터 로드"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 감정 코드 매핑 로드
            with open(os.path.join(current_dir, 'emotion_code_map.json'), 'r', encoding='utf-8') as f:
                self.emotion_code_map = json.load(f)
            
            # 감정 키워드 매핑 로드
            with open(os.path.join(current_dir, 'emotion_keywords_map.json'), 'r', encoding='utf-8') as f:
                self.emotion_keywords_map = json.load(f)
            
            # 감정 매핑 로드
            with open(os.path.join(current_dir, 'emotion_mapping.json'), 'r', encoding='utf-8') as f:
                self.emotion_mapping = json.load(f)
                
            logger.info("✅ 감정 매핑 데이터 로드 완료")
            
        except Exception as e:
            logger.error(f"⚠️ 감정 매핑 데이터 로드 실패: {str(e)}")
            self.emotion_code_map = {}
            self.emotion_keywords_map = {}
            self.emotion_mapping = {}
    
    def estimate_emotion_label(self, text: str) -> str:
        """감정 레이블 추정"""
        try:
            if any(word in text for word in ["기쁨", "행복", "즐거움"]):
                return "joy"
            elif any(word in text for word in ["슬픔", "눈물", "아픔"]):
                return "sadness"
            elif any(word in text for word in ["화남", "분노", "짜증"]):
                return "anger"
            elif any(word in text for word in ["두려움", "공포", "불안"]):
                return "fear"
            else:
                return "neutral"
        except Exception as e:
            logger.error(f"⚠️ 감정 레이블 추정 실패: {str(e)}")
            return "neutral"
    
    def emotion_match_score(self, text1: str, text2: str) -> float:
        """감정 매칭 점수 계산"""
        try:
            label1 = self.estimate_emotion_label(text1)
            label2 = self.estimate_emotion_label(text2)
            return 1.0 if label1 == label2 else 0.0
        except Exception as e:
            logger.error(f"⚠️ 감정 매칭 점수 계산 실패: {str(e)}")
            return 0.0
    
    def analyze_emotion(self, text: str) -> Dict[str, Any]:
        """감정 분석 수행"""
        try:
            # 1. 캐시 확인
            if text in self._cache:
                return self._cache[text]
            
            # 2. 감정 레이블 추정
            emotion_label = self.estimate_emotion_label(text)
            
            # 3. 감정 코드 매핑
            emotion_code = self.emotion_code_map.get(emotion_label, "N000")
            
            # 4. 감정 키워드 매핑
            emotion_keywords = self.emotion_keywords_map.get(emotion_label, [])
            
            # 5. 결과 생성
            result = {
                "emotion": emotion_label,
                "code": emotion_code,
                "keywords": emotion_keywords,
                "intensity": 0.5,  # 기본 강도
                "confidence": 0.8  # 기본 신뢰도
            }
            
            # 6. 캐시 업데이트
            self._update_cache(text, result)
            
            # 7. 이력 업데이트
            self._update_emotion_history(result)
            
            return result
            
        except Exception as e:
            logger.error(f"⚠️ 감정 분석 실패: {str(e)}")
            return self._create_default_emotion()
    
    def _update_cache(self, key: str, value: Dict[str, Any]):
        """캐시 업데이트"""
        try:
            if len(self._cache) >= self._cache_size:
                self._cache.pop(next(iter(self._cache)))
            self._cache[key] = value
        except Exception as e:
            logger.error(f"⚠️ 캐시 업데이트 실패: {str(e)}")
    
    def _update_emotion_history(self, emotion: Dict[str, Any]):
        """감정 이력 업데이트"""
        try:
            self._emotion_history.append(emotion)
            if len(self._emotion_history) > self._max_history:
                self._emotion_history.pop(0)
        except Exception as e:
            logger.error(f"⚠️ 감정 이력 업데이트 실패: {str(e)}")
    
    def _create_default_emotion(self) -> Dict[str, Any]:
        """기본 감정 결과 생성"""
        return {
            "emotion": "neutral",
            "code": "N000",
            "keywords": [],
            "intensity": 0.5,
            "confidence": 0.5
        }

def get_emotion_core() -> EmotionCore:
    """EmotionCore 싱글톤 인스턴스 반환"""
    return EmotionCore()
