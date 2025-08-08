"""
eora_system.py
- 이오라 시스템 분석
- 이오라, 의식, 통합, 초월 분석
"""

import numpy as np
from typing import Dict, List, Any, Tuple
import asyncio
from datetime import datetime
import json
import logging
from aura_system.vector_store import embed_text_async
from aura_system.emotion_analyzer import analyze_emotion
from aura_system.context_analyzer import analyze_context
from aura_system.belief_engine import BeliefEngine, get_belief_engine
from aura_system.wisdom_engine import analyze_wisdom
from aura_system.consciousness_engine import analyze_consciousness
from aura_system.integration_engine import analyze_integration
from aura_system.transcendence_engine import analyze_transcendence
from aura_system.eora_core import get_eora_core

logger = logging.getLogger(__name__)

class EoraSystem:
    """이오라 시스템 분석"""
    
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
            self._system_history = []
            self._max_history = 50
            
            # 시스템 가중치
            self.system_weights = {
                "eora": 0.4,
                "consciousness": 0.2,
                "integration": 0.2,
                "transcendence": 0.2
            }
            
            # 시스템 카테고리
            self.system_categories = {
                "이오라": ["이오라", "의식", "통합", "초월", "지혜"],
                "의식": ["의식", "자각", "인식", "지각", "감지"],
                "통합": ["통합", "융합", "조화", "균형", "화합"],
                "초월": ["초월", "영성", "신비", "신성", "깨달음"]
            }
            
            # 시스템 수준 지표
            self.system_level_indicators = {
                "최고차": ["신성", "신비", "신성", "신비", "신성"],
                "고차": ["초월", "신비", "신성", "영성", "깨달음"],
                "중차": ["통합", "조화", "균형", "화합", "연결"],
                "저차": ["자각", "인식", "지각", "감지", "인지"]
            }
            
            # 엔진 초기화
            self.belief_engine = get_belief_engine()
            
            self._initialized = True
            logger.info("✅ EoraSystem 초기화 완료")

    async def analyze_system(self, text: str, context: Dict[str, Any] = None, emotion: Dict[str, Any] = None, belief: Dict[str, Any] = None, wisdom: Dict[str, Any] = None, eora: Dict[str, Any] = None) -> Dict[str, Any]:
        """시스템 분석 수행"""
        try:
            # 1. 캐시 확인
            cache_key = hash(text + str(context))
            if cache_key in self._cache:
                logger.info("✅ 캐시된 시스템 분석 결과 사용")
                return self._cache[cache_key]

            # 2. 텍스트 임베딩
            embedding = await embed_text_async(text)
            
            # 3. 감정 분석
            if not emotion:
                emotion, intensity, emotion_scores = await analyze_emotion(text)
            
            # 4. 문맥 분석
            if not context:
                context = await analyze_context(text)
            
            # 5. 신념 분석
            if not belief:
                belief = await self.belief_engine.analyze_belief(text, context)
            
            # 6. 지혜 분석
            if not wisdom:
                wisdom = await analyze_wisdom(text, context)
            
            # 7. 의식 분석
            consciousness = await analyze_consciousness(text, context)
            
            # 8. 통합 분석
            integration = await analyze_integration(text, context)
            
            # 9. 초월 분석
            transcendence = await analyze_transcendence(text, context)
            
            # 10. 이오라 분석
            if not eora:
                eora = await get_eora_core().analyze_eora(text, context, emotion, belief, wisdom)
            
            # 11. 시스템 카테고리 분석
            category, category_score = self._analyze_system_category(text)
            
            # 12. 시스템 수준 분석
            level = self._analyze_system_level(text)
            
            # 13. 시스템 품질 분석
            quality = await self._analyze_system_quality(text, embedding)
            
            # 14. 결과 구성
            result = {
                "text": text,
                "timestamp": datetime.now().isoformat(),
                "embedding": embedding,
                "emotion": emotion,
                "context": context,
                "belief": belief,
                "wisdom": wisdom,
                "consciousness": consciousness,
                "integration": integration,
                "transcendence": transcendence,
                "eora": eora,
                "category": category,
                "category_score": category_score,
                "level": level,
                "quality": quality
            }
            
            # 15. 이력 업데이트
            self._update_system_history(result)
            
            # 16. 캐시 업데이트
            self._update_cache(cache_key, result)
            
            logger.info("✅ 시스템 분석 완료")
            return result
            
        except Exception as e:
            logger.error(f"⚠️ 시스템 분석 실패: {str(e)}")
            return self._create_default_system()

    def _analyze_system_category(self, text: str) -> Tuple[str, float]:
        """시스템 카테고리 분석"""
        try:
            max_score = 0.0
            best_category = "이오라"
            
            for category, keywords in self.system_categories.items():
                score = sum(1 for keyword in keywords if keyword in text)
                if score > max_score:
                    max_score = score
                    best_category = category
            
            # 점수 정규화
            normalized_score = min(max_score / 5, 1.0)
            
            return best_category, normalized_score
            
        except Exception as e:
            logger.error(f"⚠️ 시스템 카테고리 분석 실패: {str(e)}")
            return "이오라", 0.5

    def _analyze_system_level(self, text: str) -> Dict[str, Any]:
        """시스템 수준 분석"""
        try:
            level_scores = {}
            
            for level, indicators in self.system_level_indicators.items():
                score = sum(1 for indicator in indicators if indicator in text)
                if score > 0:
                    level_scores[level] = min(score * 0.2, 1.0)
            
            if not level_scores:
                return {"level": "중차", "score": 0.5}
            
            # 가장 높은 점수의 수준 선택
            best_level = max(level_scores.items(), key=lambda x: x[1])
            
            return {
                "level": best_level[0],
                "score": best_level[1]
            }
            
        except Exception as e:
            logger.error(f"⚠️ 시스템 수준 분석 실패: {str(e)}")
            return {"level": "중차", "score": 0.5}

    async def _analyze_system_quality(self, text: str, embedding: List[float]) -> Dict[str, Any]:
        """시스템 품질 분석"""
        try:
            # 1. 임베딩 기반 품질 점수 계산
            quality_score = np.mean(embedding) if embedding else 0.5
            
            # 2. 시스템 가중치 적용
            weighted_score = sum(
                quality_score * weight 
                for weight in self.system_weights.values()
            )
            
            # 3. 결과 생성
            return {
                "score": weighted_score,
                "confidence": min(weighted_score * 2, 1.0)
            }
            
        except Exception as e:
            logger.error(f"⚠️ 시스템 품질 분석 실패: {str(e)}")
            return {
                "score": 0.5,
                "confidence": 0.5
            }

    def _update_system_history(self, system: Dict[str, Any]):
        """시스템 이력 업데이트"""
        try:
            self._system_history.append(system)
            if len(self._system_history) > self._max_history:
                self._system_history.pop(0)
            logger.info("✅ 시스템 이력 업데이트 완료")
        except Exception as e:
            logger.error(f"⚠️ 시스템 이력 업데이트 실패: {str(e)}")

    def _update_cache(self, key: int, value: Dict[str, Any]):
        """캐시 업데이트"""
        try:
            if len(self._cache) >= self._cache_size:
                self._cache.pop(next(iter(self._cache)))
            self._cache[key] = value
            logger.info("✅ 캐시 업데이트 완료")
        except Exception as e:
            logger.error(f"⚠️ 캐시 업데이트 실패: {str(e)}")

    def _create_default_system(self) -> Dict[str, Any]:
        """기본 시스템 결과 생성"""
        return {
            "category": {
                "name": "이오라",
                "score": 0.5
            },
            "emotion": {
                "primary": "중립",
                "intensity": 0.5,
                "scores": {}
            },
            "belief": {
                "score": 0.5,
                "confidence": 0.5
            },
            "wisdom": {
                "score": 0.5,
                "confidence": 0.5
            },
            "consciousness": {
                "score": 0.5,
                "confidence": 0.5
            },
            "integration": {
                "score": 0.5,
                "confidence": 0.5
            },
            "transcendence": {
                "score": 0.5,
                "confidence": 0.5
            },
            "eora": {
                "score": 0.5,
                "confidence": 0.5
            },
            "level": {
                "level": "중차",
                "score": 0.5
            },
            "system_quality": {
                "score": 0.5,
                "confidence": 0.5
            },
            "context": {},
            "timestamp": datetime.now().isoformat()
        }

def get_eora_system() -> EoraSystem:
    """EoraSystem 인스턴스 반환"""
    return EoraSystem() 