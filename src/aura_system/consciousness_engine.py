"""
aura_system.consciousness_engine
- 의식 엔진 모듈
"""

import numpy as np
from typing import Dict, List, Any, Tuple, Optional
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

class ConsciousnessEngine(BaseEngine):
    """의식 엔진"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.consciousness_store = {}
        self.cache = {}
        self.history = []
        self._cache_size = 1000
        self._max_history = 50
        
        # 의식 가중치
        self.consciousness_weights = {
            "awareness": 0.3,
            "clarity": 0.3,
            "depth": 0.2,
            "stability": 0.2
        }
        
        # 의식 카테고리
        self.consciousness_categories = {
            "자각": ["자각", "인식", "지각", "감지", "인지"],
            "명료": ["명료", "선명", "뚜렷", "명확", "분명"],
            "깊이": ["깊이", "심도", "심층", "본질", "핵심"],
            "안정": ["안정", "균형", "조화", "평화", "화합"]
        }
        
        # 의식 수준 지표
        self.consciousness_level_indicators = {
            "최고차": ["신성", "신비", "신성", "신비", "신성"],
            "고차": ["초월", "신비", "신성", "영성", "깨달음"],
            "중차": ["통합", "조화", "균형", "화합", "연결"],
            "저차": ["자각", "인식", "지각", "감지", "인지"]
        }
        
        logger.info("✅ ConsciousnessEngine 초기화 완료")

    async def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """입력 처리
        
        Args:
            input_data (str): 입력 텍스트
            context (dict, optional): 컨텍스트 정보
            
        Returns:
            dict: 처리 결과
        """
        try:
            # BeliefEngine과 WisdomEngine을 여기서 import하여 순환 참조 방지
            from aura_system.belief_engine import BeliefEngine, get_belief_engine
            from aura_system.wisdom_engine import analyze_wisdom
            belief_engine = get_belief_engine()
            
            # 1. 캐시 확인
            cache_key = hash(input_data + str(context))
            if cache_key in self.cache:
                logger.info("✅ 캐시된 의식 분석 결과 사용")
                return self.cache[cache_key]

            # 2. 텍스트 임베딩
            embedding = await embed_text_async(input_data)
            
            # 3. 감정 분석
            emotion, intensity, emotion_scores = await analyze_emotion(input_data)
            
            # 4. 문맥 분석
            if not context:
                context = await analyze_context(input_data)
            
            # 5. 신념 분석
            belief = await belief_engine.analyze_belief(input_data, context)
            
            # 6. 의식 카테고리 분석
            category, category_score = self._analyze_consciousness_category(input_data)
            
            # 7. 의식 수준 분석
            level = self._analyze_consciousness_level(input_data)
            
            # 8. 의식 깊이 분석
            depth = await self._analyze_consciousness_depth(input_data, embedding)
            
            # 9. 의식 통합
            consciousness = {
                "category": {
                    "name": category,
                    "score": category_score
                },
                "emotion": {
                    "primary": emotion,
                    "intensity": intensity,
                    "scores": emotion_scores
                },
                "belief": belief,
                "level": level,
                "depth": depth,
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
            
            # 10. 의식 이력 업데이트
            self._update_consciousness_history(consciousness)
            
            # 11. 결과 캐싱
            self._update_cache(cache_key, consciousness)
            
            logger.info("✅ 의식 분석 완료")
            return consciousness
            
        except Exception as e:
            logger.error(f"⚠️ 의식 분석 실패: {str(e)}")
            return self._create_default_consciousness()

    def _analyze_consciousness_category(self, text: str) -> Tuple[str, float]:
        """의식 카테고리 분석"""
        try:
            max_score = 0.0
            best_category = "자각"
            
            for category, keywords in self.consciousness_categories.items():
                score = sum(1 for keyword in keywords if keyword in text)
                if score > max_score:
                    max_score = score
                    best_category = category
            
            # 점수 정규화
            normalized_score = min(max_score / 5, 1.0)
            
            logger.info(f"✅ 의식 카테고리 분석 완료: {best_category} ({normalized_score:.2f})")
            return best_category, normalized_score
            
        except Exception as e:
            logger.error(f"⚠️ 의식 카테고리 분석 실패: {str(e)}")
            return "자각", 0.5

    def _analyze_consciousness_level(self, text: str) -> Dict[str, Any]:
        """의식 수준 분석"""
        try:
            level_scores = {}
            
            for level, indicators in self.consciousness_level_indicators.items():
                score = sum(1 for indicator in indicators if indicator in text)
                if score > 0:
                    level_scores[level] = min(score * 0.2, 1.0)
            
            if not level_scores:
                return {"level": "중차", "score": 0.5}
            
            # 가장 높은 점수의 수준 선택
            best_level = max(level_scores.items(), key=lambda x: x[1])
            
            logger.info(f"✅ 의식 수준 분석 완료: {best_level[0]} ({best_level[1]:.2f})")
            return {
                "level": best_level[0],
                "score": best_level[1]
            }
            
        except Exception as e:
            logger.error(f"⚠️ 의식 수준 분석 실패: {str(e)}")
            return {"level": "중차", "score": 0.5}

    async def _analyze_consciousness_depth(self, text: str, embedding: List[float]) -> Dict[str, Any]:
        """의식 깊이 분석"""
        try:
            depth = {
                "cognitive": 0.5,
                "emotional": 0.5,
                "spiritual": 0.5
            }
            
            # 인지적 깊이 (지식과 이해의 깊이)
            context = await analyze_context(text)
            if context["semantic"]["complexity"] > 0.7:
                depth["cognitive"] = 0.8
            
            # 감정적 깊이 (감정과 의식의 깊이)
            emotion_scores = await analyze_emotion(text)
            if emotion_scores[1] > 0.7:  # 강한 감정
                depth["emotional"] = 0.8
            
            # 영적 깊이 (영성과 의식의 깊이)
            wisdom = await analyze_wisdom(text)
            if wisdom["depth"]["score"] > 0.7:
                depth["spiritual"] = 0.8
            
            logger.info("✅ 의식 깊이 분석 완료")
            return depth
            
        except Exception as e:
            logger.error(f"⚠️ 의식 깊이 분석 실패: {str(e)}")
            return {"cognitive": 0.5, "emotional": 0.5, "spiritual": 0.5}

    def _update_consciousness_history(self, consciousness: Dict[str, Any]):
        """의식 이력 업데이트"""
        try:
            self.history.append(consciousness)
            if len(self.history) > self._max_history:
                self.history.pop(0)
            logger.info("✅ 의식 이력 업데이트 완료")
        except Exception as e:
            logger.error(f"⚠️ 의식 이력 업데이트 실패: {str(e)}")

    def _update_cache(self, key: int, value: Dict[str, Any]):
        """캐시 업데이트"""
        try:
            if len(self.cache) >= self._cache_size:
                self.cache.pop(next(iter(self.cache)))
            self.cache[key] = value
            logger.info("✅ 의식 캐시 업데이트 완료")
        except Exception as e:
            logger.error(f"⚠️ 의식 캐시 업데이트 실패: {str(e)}")

    def _create_default_consciousness(self) -> Dict[str, Any]:
        """기본 의식 생성"""
        return {
            "category": {"name": "자각", "score": 0.5},
            "emotion": {
                "primary": "neutral",
                "intensity": 0.5,
                "scores": {"neutral": 1.0}
            },
            "belief": {},
            "level": {"level": "중차", "score": 0.5},
            "depth": {"cognitive": 0.5, "emotional": 0.5, "spiritual": 0.5},
            "context": {},
            "timestamp": datetime.now().isoformat()
        }

# 싱글톤 인스턴스
_consciousness_engine = None

def get_consciousness_engine():
    """의식 엔진 인스턴스 반환"""
    global _consciousness_engine
    if _consciousness_engine is None:
        _consciousness_engine = ConsciousnessEngine()
    return _consciousness_engine

async def analyze_consciousness(context: Dict[str, Any]) -> Dict[str, Any]:
    """의식 분석 수행"""
    engine = get_consciousness_engine()
    return await engine.process_consciousness(context) 