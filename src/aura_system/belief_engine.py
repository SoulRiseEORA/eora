"""
aura_system.belief_engine
- 신념 엔진 모듈
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import asyncio
import logging
from datetime import datetime
import json
from aura_system.vector_store import embed_text_async
from aura_system.emotion_analyzer import analyze_emotion
from aura_system.context_analyzer import analyze_context

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

class BeliefEngine(BaseEngine):
    """신념 엔진"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.belief_store = {}
        self.cache = {}
        self.history = []
        self._cache_size = 1000
        self._max_history = 50
        
        # 신념 가중치
        self.belief_weights = {
            "emotional": 0.3,
            "logical": 0.3,
            "experiential": 0.2,
            "ethical": 0.2
        }
        
        # 신념 카테고리
        self.belief_categories = {
            "자아": ["자아", "정체성", "자기인식", "자기존중", "자기성장"],
            "관계": ["관계", "연결", "공감", "신뢰", "소통"],
            "가치": ["가치", "의미", "목적", "방향성", "철학"],
            "지식": ["지식", "학습", "이해", "통찰", "지혜"],
            "윤리": ["윤리", "도덕", "정의", "책임", "선함"],
            "성장": ["성장", "발전", "변화", "진화", "혁신"],
            "자연": ["자연", "우주", "생명", "조화", "균형"],
            "초월": ["초월", "영성", "신비", "깨달음", "통찰"]
        }
        
        # 신념 강도 지표
        self.belief_intensity_indicators = {
            "강한": ["절대", "완전", "항상", "절대로", "반드시"],
            "중간": ["보통", "일반적", "대체로", "주로", "보통"],
            "약한": ["가능", "아마", "어쩌면", "때로", "가끔"]
        }
        
        logger.info("✅ BeliefEngine 초기화 완료")

    async def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """입력 처리
        
        Args:
            input_data (str): 입력 텍스트
            context (dict, optional): 컨텍스트 정보
            
        Returns:
            dict: 처리 결과
        """
        return await self.analyze_belief(input_data, context)

    async def analyze_belief(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """신념 분석 수행"""
        try:
            # 1. 캐시 확인
            cache_key = hash(text + str(context))
            if cache_key in self.cache:
                logger.info("✅ 캐시된 신념 분석 결과 사용")
                return self.cache[cache_key]

            # 2. 텍스트 임베딩
            embedding = await embed_text_async(text)
            
            # 3. 감정 분석
            emotion, intensity, emotion_scores = await analyze_emotion(text)
            
            # 4. 문맥 분석
            if not context:
                context = await analyze_context(text)
            
            # 5. 신념 카테고리 분석
            category, category_score = self._analyze_belief_category(text)
            
            # 6. 신념 강도 분석
            intensity_level = self._analyze_belief_intensity(text)
            
            # 7. 신념 일관성 분석
            consistency = await self._analyze_belief_consistency(text, embedding)
            
            # 8. 신념 통합
            belief = {
                "category": {
                    "name": category,
                    "score": category_score
                },
                "emotion": {
                    "primary": emotion,
                    "intensity": intensity,
                    "scores": emotion_scores
                },
                "intensity": intensity_level,
                "consistency": consistency,
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
            
            # 9. 신념 이력 업데이트
            self._update_belief_history(belief)
            
            # 10. 결과 캐싱
            self._update_cache(cache_key, belief)
            
            logger.info("✅ 신념 분석 완료")
            return belief
            
        except Exception as e:
            logger.error(f"⚠️ 신념 분석 실패: {str(e)}")
            return self._create_default_belief()

    def _analyze_belief_category(self, text: str) -> Tuple[str, float]:
        """신념 카테고리 분석"""
        try:
            max_score = 0.0
            best_category = "자아"
            
            for category, keywords in self.belief_categories.items():
                score = sum(1 for keyword in keywords if keyword in text)
                if score > max_score:
                    max_score = score
                    best_category = category
            
            # 점수 정규화
            normalized_score = min(max_score / 5, 1.0)
            
            logger.info(f"✅ 신념 카테고리 분석 완료: {best_category} ({normalized_score:.2f})")
            return best_category, normalized_score
            
        except Exception as e:
            logger.error(f"⚠️ 신념 카테고리 분석 실패: {str(e)}")
            return "자아", 0.5

    def _analyze_belief_intensity(self, text: str) -> Dict[str, Any]:
        """신념 강도 분석"""
        try:
            intensity_scores = {}
            
            for level, indicators in self.belief_intensity_indicators.items():
                score = sum(1 for indicator in indicators if indicator in text)
                if score > 0:
                    intensity_scores[level] = min(score * 0.2, 1.0)
            
            if not intensity_scores:
                return {"level": "중간", "score": 0.5}
            
            # 가장 높은 점수의 강도 선택
            best_intensity = max(intensity_scores.items(), key=lambda x: x[1])
            
            logger.info(f"✅ 신념 강도 분석 완료: {best_intensity[0]} ({best_intensity[1]:.2f})")
            return {
                "level": best_intensity[0],
                "score": best_intensity[1]
            }
            
        except Exception as e:
            logger.error(f"⚠️ 신념 강도 분석 실패: {str(e)}")
            return {"level": "중간", "score": 0.5}

    async def _analyze_belief_consistency(self, text: str, embedding: List[float]) -> Dict[str, Any]:
        """신념 일관성 분석"""
        try:
            consistency = {
                "internal": 0.5,
                "external": 0.5,
                "temporal": 0.5
            }
            
            # 내부 일관성 (감정과 내용의 일치성)
            emotion_scores = await analyze_emotion(text)
            if emotion_scores[1] > 0.7:  # 강한 감정
                consistency["internal"] = 0.8
            
            # 외부 일관성 (문맥과의 일치성)
            context = await analyze_context(text)
            if context["semantic"]["specificity"] > 0.7:
                consistency["external"] = 0.8
            
            # 시간적 일관성 (이력과의 일치성)
            if self.history:
                last_belief = self.history[-1]
                if last_belief["category"]["name"] == self._analyze_belief_category(text)[0]:
                    consistency["temporal"] = 0.8
            
            logger.info("✅ 신념 일관성 분석 완료")
            return consistency
            
        except Exception as e:
            logger.error(f"⚠️ 신념 일관성 분석 실패: {str(e)}")
            return {"internal": 0.5, "external": 0.5, "temporal": 0.5}

    def _update_belief_history(self, belief: Dict[str, Any]):
        """신념 이력 업데이트"""
        try:
            self.history.append(belief)
            if len(self.history) > self._max_history:
                self.history.pop(0)
            logger.info("✅ 신념 이력 업데이트 완료")
        except Exception as e:
            logger.error(f"⚠️ 신념 이력 업데이트 실패: {str(e)}")

    def _update_cache(self, key: int, value: Dict[str, Any]):
        """캐시 업데이트"""
        try:
            if len(self.cache) >= self._cache_size:
                self.cache.pop(next(iter(self.cache)))
            self.cache[key] = value
            logger.info("✅ 신념 캐시 업데이트 완료")
        except Exception as e:
            logger.error(f"⚠️ 신념 캐시 업데이트 실패: {str(e)}")

    def _create_default_belief(self) -> Dict[str, Any]:
        """기본 신념 생성"""
        return {
            "category": {"name": "자아", "score": 0.5},
            "emotion": {
                "primary": "neutral",
                "intensity": 0.5,
                "scores": {"neutral": 1.0}
            },
            "intensity": {"level": "중간", "score": 0.5},
            "consistency": {"internal": 0.5, "external": 0.5, "temporal": 0.5},
            "context": {},
            "timestamp": datetime.now().isoformat()
        }

def get_belief_engine() -> BeliefEngine:
    """BeliefEngine 인스턴스 반환"""
    return BeliefEngine() 