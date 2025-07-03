"""
integration_engine.py
- 통합 분석 엔진
- 통합 수준, 깊이, 통합성 분석
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
from aura_system.belief_engine import BeliefEngine, get_belief_engine
from aura_system.wisdom_engine import analyze_wisdom
from aura_system.consciousness_engine import analyze_consciousness
from ai_core.base import BaseEngine

logger = logging.getLogger(__name__)

class IntegrationEngine(BaseEngine):
    """통합 엔진 클래스"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.integration_store = {}
        self._cache = {}
        self._cache_size = 1000
        self._integration_history = []
        self._max_history = 50
        
        # 엔진 초기화
        self.belief_engine = get_belief_engine()
        
        # 통합 가중치
        self.integration_weights = {
            "cognitive": 0.3,
            "emotional": 0.3,
            "spiritual": 0.2,
            "physical": 0.2
        }
        
        # 통합 카테고리
        self.integration_categories = {
            "조화": ["조화", "화합", "균형", "안정", "평화"],
            "통합": ["통합", "융합", "결합", "연결", "합치"],
            "일체": ["일체", "하나", "통일", "단일", "일원"],
            "응집": ["응집", "집중", "모음", "모집", "수렴"]
        }
        
        # 통합 수준 지표
        self.integration_level_indicators = {
            "최고차": ["신성", "신비", "신성", "신비", "신성"],
            "고차": ["초월", "신비", "신성", "영성", "깨달음"],
            "중차": ["통합", "조화", "균형", "화합", "연결"],
            "저차": ["자각", "인식", "지각", "감지", "인지"]
        }

    async def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """입력 처리
        
        Args:
            input_data (str): 입력 텍스트
            context (dict, optional): 컨텍스트 정보
            
        Returns:
            dict: 처리 결과
        """
        try:
            # 1. 텍스트 임베딩
            embedding = await embed_text_async(input_data)
            
            # 2. 감정 분석
            emotion, intensity, emotion_scores = await analyze_emotion(input_data)
            
            # 3. 문맥 분석
            if not context:
                context = await analyze_context(input_data)
            
            # 4. 신념 분석
            belief = await self.belief_engine.analyze_belief(input_data, context)
            
            # 5. 의식 분석
            consciousness = await analyze_consciousness(input_data, context)
            
            # 6. 통합 점수 계산
            integration_score = await self.calculate_integration(
                embedding,
                belief,
                consciousness
            )
            
            result = {
                "integration_score": integration_score,
                "belief": belief,
                "consciousness": consciousness,
                "emotion": {
                    "primary": emotion,
                    "intensity": intensity,
                    "scores": emotion_scores
                },
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ 통합 분석 완료: {integration_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"⚠️ 통합 분석 실패: {str(e)}")
            return {
                "integration_score": 0.0,
                "belief": {},
                "consciousness": {},
                "emotion": {
                    "primary": "neutral",
                    "intensity": 0.0,
                    "scores": {"neutral": 1.0}
                },
                "context": {},
                "timestamp": datetime.now().isoformat()
            }

    async def calculate_integration(
        self,
        embedding: List[float],
        belief: Dict[str, Any],
        consciousness: Dict[str, Any]
    ) -> float:
        """통합 점수 계산"""
        try:
            # 1. 인지적 통합 점수
            cognitive_score = belief.get("category", {}).get("score", 0.5)
            
            # 2. 감정적 통합 점수
            emotional_score = consciousness.get("emotion", {}).get("intensity", 0.5)
            
            # 3. 영적 통합 점수
            spiritual_score = consciousness.get("depth", {}).get("spiritual", 0.5)
            
            # 4. 물리적 통합 점수 (임베딩 복잡도)
            complexity_score = np.std(embedding) / np.mean(np.abs(embedding))
            physical_score = min(complexity_score, 1.0)
            
            # 5. 종합 점수 계산
            integration_score = (
                cognitive_score * self.integration_weights["cognitive"] +
                emotional_score * self.integration_weights["emotional"] +
                spiritual_score * self.integration_weights["spiritual"] +
                physical_score * self.integration_weights["physical"]
            )
            
            return integration_score
            
        except Exception as e:
            logger.error(f"⚠️ 통합 점수 계산 실패: {str(e)}")
            return 0.0

    def add_integration(self, key: str, integration: Any) -> bool:
        """통합 데이터 추가
        
        Args:
            key (str): 키
            integration (Any): 통합 데이터
            
        Returns:
            bool: 성공 여부
        """
        try:
            self.integration_store[key] = integration
            return True
        except Exception as e:
            logger.error(f"⚠️ 통합 데이터 추가 실패: {str(e)}")
            return False

    def get_integration(self, key: str) -> Optional[Any]:
        """통합 데이터 조회
        
        Args:
            key (str): 키
            
        Returns:
            Any: 통합 데이터
        """
        return self.integration_store.get(key)

    async def analyze_integration(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """통합 분석 수행"""
        try:
            # 1. 캐시 확인
            cache_key = hash(text + str(context))
            if cache_key in self._cache:
                logger.info("✅ 캐시된 통합 분석 결과 사용")
                return self._cache[cache_key]

            # 2. 텍스트 임베딩
            embedding = await embed_text_async(text)
            
            # 3. 감정 분석
            emotion, intensity, emotion_scores = await analyze_emotion(text)
            
            # 4. 문맥 분석
            if not context:
                context = await analyze_context(text)
            
            # 5. 신념 분석
            belief = await self.belief_engine.analyze_belief(text, context)
            
            # 6. 통합 카테고리 분석
            category, category_score = self._analyze_integration_category(text)
            
            # 7. 통합 수준 분석
            level = self._analyze_integration_level(text)
            
            # 8. 통합 깊이 분석
            depth = await self._analyze_integration_depth(text, embedding)
            
            # 9. 통합 통합
            integration = {
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
            
            # 10. 통합 이력 업데이트
            self._update_integration_history(integration)
            
            # 11. 결과 캐싱
            self._update_cache(cache_key, integration)
            
            logger.info("✅ 통합 분석 완료")
            return integration
            
        except Exception as e:
            logger.error(f"⚠️ 통합 분석 실패: {str(e)}")
            return self._create_default_integration()

    def _analyze_integration_category(self, text: str) -> Tuple[str, float]:
        """통합 카테고리 분석"""
        try:
            max_score = 0.0
            best_category = "인지통합"
            
            for category, keywords in self.integration_categories.items():
                score = sum(1 for keyword in keywords if keyword in text)
                if score > max_score:
                    max_score = score
                    best_category = category
            
            # 점수 정규화
            normalized_score = min(max_score / 5, 1.0)
            
            logger.info(f"✅ 통합 카테고리 분석 완료: {best_category} ({normalized_score:.2f})")
            return best_category, normalized_score
            
        except Exception as e:
            logger.error(f"⚠️ 통합 카테고리 분석 실패: {str(e)}")
            return "인지통합", 0.5

    def _analyze_integration_level(self, text: str) -> Dict[str, Any]:
        """통합 수준 분석"""
        try:
            level_scores = {}
            
            for level, indicators in self.integration_level_indicators.items():
                score = sum(1 for indicator in indicators if indicator in text)
                if score > 0:
                    level_scores[level] = min(score * 0.2, 1.0)
            
            if not level_scores:
                return {"level": "중차", "score": 0.5}
            
            # 가장 높은 점수의 수준 선택
            best_level = max(level_scores.items(), key=lambda x: x[1])
            
            logger.info(f"✅ 통합 수준 분석 완료: {best_level[0]} ({best_level[1]:.2f})")
            return {
                "level": best_level[0],
                "score": best_level[1]
            }
            
        except Exception as e:
            logger.error(f"⚠️ 통합 수준 분석 실패: {str(e)}")
            return {"level": "중차", "score": 0.5}

    async def _analyze_integration_depth(self, text: str, embedding: List[float]) -> Dict[str, Any]:
        """통합 깊이 분석"""
        try:
            depth = {
                "wisdom": 0.5,
                "consciousness": 0.5
            }
            
            # 지혜 분석
            wisdom = await analyze_wisdom(text)
            if wisdom["depth"]["score"] > 0.7:
                depth["wisdom"] = 0.8
            
            # 의식 분석
            consciousness = await analyze_consciousness(text)
            if consciousness["integration"]["spiritual"] > 0.7:
                depth["consciousness"] = 0.8
            
            logger.info("✅ 통합 깊이 분석 완료")
            return depth
            
        except Exception as e:
            logger.error(f"⚠️ 통합 깊이 분석 실패: {str(e)}")
            return {"wisdom": 0.5, "consciousness": 0.5}

    def _update_integration_history(self, integration: Dict[str, Any]):
        """통합 이력 업데이트"""
        try:
            self._integration_history.append(integration)
            if len(self._integration_history) > self._max_history:
                self._integration_history.pop(0)
            logger.info("✅ 통합 이력 업데이트 완료")
        except Exception as e:
            logger.error(f"⚠️ 통합 이력 업데이트 실패: {str(e)}")

    def _update_cache(self, key: int, value: Dict[str, Any]):
        """캐시 업데이트"""
        try:
            if len(self._cache) >= self._cache_size:
                self._cache.pop(next(iter(self._cache)))
            self._cache[key] = value
            logger.info("✅ 통합 캐시 업데이트 완료")
        except Exception as e:
            logger.error(f"⚠️ 통합 캐시 업데이트 실패: {str(e)}")

    def _create_default_integration(self) -> Dict[str, Any]:
        """기본 통합 생성"""
        return {
            "category": {"name": "인지통합", "score": 0.5},
            "emotion": {
                "primary": "neutral",
                "intensity": 0.5,
                "scores": {"neutral": 1.0}
            },
            "belief": {},
            "level": {"level": "중차", "score": 0.5},
            "depth": {"wisdom": 0.5, "consciousness": 0.5},
            "context": {},
            "timestamp": datetime.now().isoformat()
        }

# 싱글톤 인스턴스
_integration_engine = None

def get_integration_engine():
    """통합 엔진 인스턴스 반환"""
    global _integration_engine
    if _integration_engine is None:
        _integration_engine = IntegrationEngine()
    return _integration_engine

async def analyze_integration(context: Dict[str, Any]) -> Dict[str, Any]:
    """통합 분석 수행"""
    engine = get_integration_engine()
    return await engine.process_integration(context) 