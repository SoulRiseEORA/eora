"""
aura_system.wisdom_engine
- 지혜 엔진 모듈
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
from aura_system.consciousness_engine import analyze_consciousness
from ai_core.engine_base import BaseEngine

logger = logging.getLogger(__name__)

class WisdomEngine(BaseEngine):
    """지혜 엔진"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._cache = {}
        self._cache_size = 1000
        self._wisdom_history = []
        self._max_history = 50
        
        # 지혜 가중치
        self.wisdom_weights = {
            "cognitive": 0.3,
            "emotional": 0.3,
            "spiritual": 0.2,
            "practical": 0.2
        }
        
        # 지혜 카테고리
        self.wisdom_categories = {
            "통찰": ["통찰", "깨달음", "이해", "인식", "지각"],
            "지혜": ["지혜", "지식", "학습", "경험", "성장"],
            "통합": ["통합", "융합", "조화", "균형", "화합"],
            "초월": ["초월", "영성", "신비", "신성", "깨달음"]
        }
        
        # 지혜 수준 지표
        self.wisdom_level_indicators = {
            "최고차": ["신성", "신비", "신성", "신비", "신성"],
            "고차": ["초월", "신비", "신성", "영성", "깨달음"],
            "중차": ["통합", "조화", "균형", "화합", "연결"],
            "저차": ["자각", "인식", "지각", "감지", "인지"]
        }
        
        logger.info("✅ WisdomEngine 초기화 완료")

    async def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """입력 처리
        
        Args:
            input_data (str): 입력 텍스트
            context (dict, optional): 컨텍스트 정보
            
        Returns:
            dict: 처리 결과
        """
        try:
            # BeliefEngine을 여기서 import하여 순환 참조 방지
            from aura_system.belief_engine import BeliefEngine, get_belief_engine
            belief_engine = get_belief_engine()
            
            # 1. 캐시 확인
            cache_key = hash(input_data + str(context))
            if cache_key in self._cache:
                logger.info("✅ 캐시된 지혜 분석 결과 사용")
                return self._cache[cache_key]
            
            # 2. 텍스트 임베딩
            embedding = await embed_text_async(input_data)
            
            # 3. 감정 분석
            emotion, intensity, emotion_scores = await analyze_emotion(input_data)
            
            # 4. 문맥 분석
            if not context:
                context = await analyze_context(input_data)
            
            # 5. 신념 분석
            belief = await belief_engine.analyze_belief(input_data, context)
            
            # 6. 의식 분석
            consciousness = await analyze_consciousness(input_data, context)
            
            # 7. 지혜 카테고리 분석
            category, category_score = self._analyze_wisdom_category(input_data)
            
            # 8. 지혜 수준 분석
            level = self._analyze_wisdom_level(input_data)
            
            # 9. 지혜 깊이 분석
            depth = await self._analyze_wisdom_depth(embedding)
            
            # 10. 지혜 점수 계산
            wisdom_score = await self.calculate_wisdom(
                embedding,
                belief,
                consciousness
            )
            
            # 11. 지혜 이력 업데이트
            wisdom_result = {
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
                "wisdom_score": wisdom_score,
                "consciousness": consciousness,
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
            
            self._update_wisdom_history(wisdom_result)
            
            # 12. 결과 캐싱
            self._update_cache(cache_key, wisdom_result)
            
            logger.info(f"✅ 지혜 분석 완료: {wisdom_score:.2f}")
            return wisdom_result
            
        except Exception as e:
            logger.error(f"⚠️ 지혜 분석 실패: {str(e)}")
            return self._create_default_wisdom()

    def _analyze_wisdom_category(self, text: str) -> Tuple[str, float]:
        """지혜 카테고리 분석"""
        try:
            max_score = 0.0
            best_category = "통찰"
            
            for category, keywords in self.wisdom_categories.items():
                score = sum(1 for keyword in keywords if keyword in text)
                if score > max_score:
                    max_score = score
                    best_category = category
            
            # 점수 정규화
            normalized_score = min(max_score / 5, 1.0)
            
            return best_category, normalized_score
            
        except Exception as e:
            logger.error(f"⚠️ 지혜 카테고리 분석 실패: {str(e)}")
            return "통찰", 0.5

    def _analyze_wisdom_level(self, text: str) -> Dict[str, Any]:
        """지혜 수준 분석"""
        try:
            level_scores = {}
            
            for level, indicators in self.wisdom_level_indicators.items():
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
            logger.error(f"⚠️ 지혜 수준 분석 실패: {str(e)}")
            return {"level": "중차", "score": 0.5}

    async def _analyze_wisdom_depth(self, embedding: List[float]) -> Dict[str, Any]:
        """지혜 깊이 분석"""
        try:
            # 1. 임베딩 기반 깊이 점수 계산
            depth_score = np.mean(embedding) if embedding else 0.5
            
            # 2. 지혜 가중치 적용
            weighted_score = depth_score * self.wisdom_weights["cognitive"]
            
            # 3. 결과 생성
            return {
                "score": weighted_score,
                "confidence": min(weighted_score * 2, 1.0)
            }
            
        except Exception as e:
            logger.error(f"⚠️ 지혜 깊이 분석 실패: {str(e)}")
            return {
                "score": 0.5,
                "confidence": 0.5
            }

    async def calculate_wisdom(
        self,
        embedding: List[float],
        belief: Dict[str, Any],
        consciousness: Dict[str, Any]
    ) -> float:
        """지혜 점수 계산"""
        try:
            # 1. 인지적 지혜 점수
            cognitive_score = belief.get("category", {}).get("score", 0.5)
            
            # 2. 감정적 지혜 점수
            emotional_score = consciousness.get("emotion", {}).get("intensity", 0.5)
            
            # 3. 영적 지혜 점수
            spiritual_score = consciousness.get("depth", {}).get("spiritual", 0.5)
            
            # 4. 실용적 지혜 점수 (임베딩 복잡도)
            complexity_score = np.std(embedding) / np.mean(np.abs(embedding))
            practical_score = min(complexity_score, 1.0)
            
            # 5. 종합 점수 계산
            wisdom_score = (
                cognitive_score * self.wisdom_weights["cognitive"] +
                emotional_score * self.wisdom_weights["emotional"] +
                spiritual_score * self.wisdom_weights["spiritual"] +
                practical_score * self.wisdom_weights["practical"]
            )
            
            return wisdom_score
            
        except Exception as e:
            logger.error(f"⚠️ 지혜 점수 계산 실패: {str(e)}")
            return 0.0

    def _update_wisdom_history(self, wisdom: Dict[str, Any]):
        """지혜 이력 업데이트"""
        try:
            self._wisdom_history.append(wisdom)
            if len(self._wisdom_history) > self._max_history:
                self._wisdom_history.pop(0)
            logger.info("✅ 지혜 이력 업데이트 완료")
        except Exception as e:
            logger.error(f"⚠️ 지혜 이력 업데이트 실패: {str(e)}")

    def _update_cache(self, key: int, value: Dict[str, Any]):
        """캐시 업데이트"""
        try:
            if len(self._cache) >= self._cache_size:
                self._cache.pop(next(iter(self._cache)))
            self._cache[key] = value
            logger.info("✅ 캐시 업데이트 완료")
        except Exception as e:
            logger.error(f"⚠️ 캐시 업데이트 실패: {str(e)}")

    def _create_default_wisdom(self) -> Dict[str, Any]:
        """기본 지혜 결과 생성"""
        return {
            "category": {
                "name": "통찰",
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
            "level": {
                "level": "중차",
                "score": 0.5
            },
            "depth": {
                "score": 0.5,
                "confidence": 0.5
            },
            "wisdom_score": 0.5,
            "consciousness": {},
            "context": {},
            "timestamp": datetime.now().isoformat()
        }

def get_wisdom_engine() -> WisdomEngine:
    """WisdomEngine의 싱글톤 인스턴스를 반환합니다."""
    return WisdomEngine()

async def analyze_wisdom(text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """지혜 분석을 수행하는 편의 함수"""
    engine = get_wisdom_engine()
    return await engine.process(text, context) 