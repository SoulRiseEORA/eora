"""
transcendence_engine.py
- 초월 분석 엔진
- 초월 수준, 깊이, 통찰력 분석
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
from aura_system.integration_engine import analyze_integration
from ai_core.base import BaseEngine

logger = logging.getLogger(__name__)

class TranscendenceEngine(BaseEngine):
    """초월 엔진 클래스"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.transcendence_store = {}
        self._cache = {}
        self._cache_size = 1000
        self._transcendence_history = []
        self._max_history = 50
        
        # 엔진 초기화
        self.belief_engine = get_belief_engine()
        
        # 초월 가중치
        self.transcendence_weights = {
            "spiritual": 1.2,
            "mystical": 1.2,
            "divine": 1.1,
            "sacred": 1.1,
            "transcendent": 1.0,
            "ordinary": 0.8
        }
        
        # 초월 카테고리
        self.transcendence_categories = {
            "영성": ["영성", "신비", "신성", "신비", "신성"],
            "초월": ["초월", "초월", "초월", "초월", "초월"],
            "깨달음": ["깨달음", "각성", "계시", "통찰", "이해"],
            "신비": ["신비", "신비", "신비", "신비", "신비"]
        }
        
        # 초월 수준 지표
        self.transcendence_level_indicators = {
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
            
            # 4. 의식 분석
            consciousness = await analyze_consciousness(input_data, context)
            
            # 5. 통합 분석
            integration = await analyze_integration(input_data, context)
            
            # 6. 초월 점수 계산
            transcendence_score = await self.calculate_transcendence(
                embedding,
                consciousness,
                integration
            )
            
            # 7. 초월 가중치 적용
            weighted_score = transcendence_score * self.transcendence_weights.get(
                consciousness.get("level", {}).get("level", "ordinary"),
                1.0
            )
            
            result = {
                "transcendence_score": weighted_score,
                "consciousness": consciousness,
                "integration": integration,
                "emotion": {
                    "primary": emotion,
                    "intensity": intensity,
                    "scores": emotion_scores
                },
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ 초월 분석 완료: {weighted_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"⚠️ 초월 분석 실패: {str(e)}")
            return {
                "transcendence_score": 0.0,
                "consciousness": {},
                "integration": {},
                "emotion": {
                    "primary": "neutral",
                    "intensity": 0.0,
                    "scores": {"neutral": 1.0}
                },
                "context": {},
                "timestamp": datetime.now().isoformat()
            }

    async def calculate_transcendence(
        self,
        embedding: List[float],
        consciousness: Dict[str, Any],
        integration: Dict[str, Any]
    ) -> float:
        """초월 점수 계산"""
        try:
            # 1. 의식 수준 점수
            consciousness_score = consciousness.get("level", {}).get("score", 0.5)
            
            # 2. 통합 점수
            integration_score = integration.get("integration_score", 0.5)
            
            # 3. 임베딩 복잡도 점수
            complexity_score = np.std(embedding) / np.mean(np.abs(embedding))
            normalized_complexity = min(complexity_score, 1.0)
            
            # 4. 종합 점수 계산
            transcendence_score = (
                consciousness_score * 0.4 +
                integration_score * 0.3 +
                normalized_complexity * 0.3
            )
            
            return transcendence_score
            
        except Exception as e:
            logger.error(f"⚠️ 초월 점수 계산 실패: {str(e)}")
            return 0.0

    def add_transcendence(self, key: str, transcendence: Any) -> bool:
        """초월 데이터 추가
        
        Args:
            key (str): 키
            transcendence (Any): 초월 데이터
            
        Returns:
            bool: 성공 여부
        """
        try:
            self.transcendence_store[key] = transcendence
            return True
        except Exception as e:
            logger.error(f"⚠️ 초월 데이터 추가 실패: {str(e)}")
            return False

    def get_transcendence(self, key: str) -> Optional[Any]:
        """초월 데이터 조회
        
        Args:
            key (str): 키
            
        Returns:
            Any: 초월 데이터
        """
        return self.transcendence_store.get(key)

    async def analyze_transcendence(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """초월 분석 수행"""
        try:
            # 1. 캐시 확인
            cache_key = hash(text + str(context))
            if cache_key in self._cache:
                logger.info("✅ 캐시된 초월 분석 결과 사용")
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
            
            # 6. 초월 카테고리 분석
            category, category_score = self._analyze_transcendence_category(text)
            
            # 7. 초월 수준 분석
            level = self._analyze_transcendence_level(text)
            
            # 8. 초월 깊이 분석
            depth = await self._analyze_transcendence_depth(text, embedding)
            
            # 9. 초월 통합
            transcendence = {
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
            
            # 10. 초월 이력 업데이트
            self._update_transcendence_history(transcendence)
            
            # 11. 결과 캐싱
            self._update_cache(cache_key, transcendence)
            
            logger.info("✅ 초월 분석 완료")
            return transcendence
            
        except Exception as e:
            logger.error(f"⚠️ 초월 분석 실패: {str(e)}")
            return self._create_default_transcendence()

    def _analyze_transcendence_category(self, text: str) -> Tuple[str, float]:
        """초월 카테고리 분석"""
        try:
            max_score = 0.0
            best_category = "영성"
            
            for category, keywords in self.transcendence_categories.items():
                score = sum(1 for keyword in keywords if keyword in text)
                if score > max_score:
                    max_score = score
                    best_category = category
            
            # 점수 정규화
            normalized_score = min(max_score / 5, 1.0)
            
            logger.info(f"✅ 초월 카테고리 분석 완료: {best_category} ({normalized_score:.2f})")
            return best_category, normalized_score
            
        except Exception as e:
            logger.error(f"⚠️ 초월 카테고리 분석 실패: {str(e)}")
            return "영성", 0.5

    def _analyze_transcendence_level(self, text: str) -> Dict[str, Any]:
        """초월 수준 분석"""
        try:
            level_scores = {}
            
            for level, indicators in self.transcendence_level_indicators.items():
                score = sum(1 for indicator in indicators if indicator in text)
                if score > 0:
                    level_scores[level] = min(score * 0.2, 1.0)
            
            if not level_scores:
                return {"level": "중차", "score": 0.5}
            
            # 가장 높은 점수의 수준 선택
            best_level = max(level_scores.items(), key=lambda x: x[1])
            
            logger.info(f"✅ 초월 수준 분석 완료: {best_level[0]} ({best_level[1]:.2f})")
            return {
                "level": best_level[0],
                "score": best_level[1]
            }
            
        except Exception as e:
            logger.error(f"⚠️ 초월 수준 분석 실패: {str(e)}")
            return {"level": "중차", "score": 0.5}

    async def _analyze_transcendence_depth(self, text: str, embedding: List[float]) -> Dict[str, Any]:
        """초월 깊이 분석"""
        try:
            depth = {
                "depth": 0.5,
                "wisdom": 0.5,
                "consciousness": 0.5
            }
            
            # 초월 깊이 계산
            depth["depth"] = min(embedding[0] * 0.2 + embedding[1] * 0.2 + embedding[2] * 0.2 + embedding[3] * 0.2 + embedding[4] * 0.2, 1.0)
            
            # 지혜 분석
            wisdom = await analyze_wisdom(text)
            depth["wisdom"] = wisdom["depth"]["score"]
            
            # 의식 분석
            consciousness = await analyze_consciousness(text)
            depth["consciousness"] = consciousness["level"]["score"]
            
            logger.info("✅ 초월 깊이 분석 완료")
            return depth
            
        except Exception as e:
            logger.error(f"⚠️ 초월 깊이 분석 실패: {str(e)}")
            return {"depth": 0.5, "wisdom": 0.5, "consciousness": 0.5}

    def _update_transcendence_history(self, transcendence: Dict[str, Any]):
        """초월 이력 업데이트"""
        try:
            self._transcendence_history.append(transcendence)
            if len(self._transcendence_history) > self._max_history:
                self._transcendence_history.pop(0)
            logger.info("✅ 초월 이력 업데이트 완료")
        except Exception as e:
            logger.error(f"⚠️ 초월 이력 업데이트 실패: {str(e)}")

    def _update_cache(self, key: int, value: Dict[str, Any]):
        """캐시 업데이트"""
        try:
            if len(self._cache) >= self._cache_size:
                self._cache.pop(next(iter(self._cache)))
            self._cache[key] = value
            logger.info("✅ 초월 캐시 업데이트 완료")
        except Exception as e:
            logger.error(f"⚠️ 초월 캐시 업데이트 실패: {str(e)}")

    def _create_default_transcendence(self) -> Dict[str, Any]:
        """기본 초월 생성"""
        return {
            "category": {"name": "영성", "score": 0.5},
            "emotion": {
                "primary": "neutral",
                "intensity": 0.5,
                "scores": {"neutral": 1.0}
            },
            "belief": {},
            "level": {"level": "중차", "score": 0.5},
            "depth": {"depth": 0.5, "wisdom": 0.5, "consciousness": 0.5},
            "context": {},
            "timestamp": datetime.now().isoformat()
        }

# 싱글톤 인스턴스
_transcendence_engine = None

def get_transcendence_engine():
    """초월 엔진 인스턴스 반환"""
    global _transcendence_engine
    if _transcendence_engine is None:
        _transcendence_engine = TranscendenceEngine()
    return _transcendence_engine

async def analyze_transcendence(context: Dict[str, Any]) -> Dict[str, Any]:
    """초월 분석 수행"""
    engine = get_transcendence_engine()
    return await engine.process_transcendence(context) 