"""
eora_interface.py
- 이오라 인터페이스 시스템
- 상호작용, 응답, 피드백, 적응 분석
"""

import numpy as np
from typing import Dict, List, Any, Tuple
import asyncio
from datetime import datetime
import json
from collections import OrderedDict
import hashlib
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
from aura_system.eora_system import EoraSystem, get_eora_system

logger = logging.getLogger(__name__)

class EoraInterface:
    """이오라 인터페이스 시스템"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.cache = OrderedDict()
            self.max_cache_size = 1000
            self.interface_history = []
            self.max_history_size = 100
            
            # 엔진 초기화
            self.belief_engine = get_belief_engine()
            self.eora_system = get_eora_system()
            
            # 인터페이스 가중치
            self.interface_weights = {
                "interaction": 0.4,
                "response": 0.3,
                "feedback": 0.2,
                "adaptation": 0.1
            }
            
            # 인터페이스 카테고리
            self.interface_categories = {
                "상호작용": ["대화", "소통", "교류", "상호작용", "소통"],
                "응답": ["응답", "반응", "피드백", "응답", "반응"],
                "피드백": ["피드백", "피드백", "피드백", "피드백", "피드백"],
                "적응": ["적응", "적응", "적응", "적응", "적응"]
            }
            
            # 인터페이스 수준 지표
            self.interface_level_indicators = {
                "최고차": ["신성", "신비", "신성", "신비", "신성"],
                "고차": ["초월", "신비", "신성", "영성", "깨달음"],
                "중차": ["통합", "조화", "균형", "화합", "연결"],
                "저차": ["자각", "인식", "지각", "감지", "인지"]
            }
            
            self._initialized = True
            logger.info("✅ EoraInterface 초기화 완료")

    def _generate_cache_key(self, text: str, context: Dict) -> str:
        """캐시 키 생성 (해시 기반)"""
        try:
            combined = f"{text}:{json.dumps(context, sort_keys=True)}"
            return hashlib.md5(combined.encode()).hexdigest()
        except Exception as e:
            logger.error(f"⚠️ 캐시 키 생성 실패: {str(e)}")
            return hashlib.md5(text.encode()).hexdigest()

    def _update_cache(self, key: str, value: Any):
        """캐시 업데이트 (LRU 방식)"""
        try:
            if key in self.cache:
                self.cache.pop(key)
            elif len(self.cache) >= self.max_cache_size:
                self.cache.popitem(last=False)
            self.cache[key] = value
            logger.info("✅ 캐시 업데이트 완료")
        except Exception as e:
            logger.error(f"⚠️ 캐시 업데이트 실패: {str(e)}")

    def _update_history(self, result: Dict):
        """인터페이스 히스토리 업데이트"""
        try:
            self.interface_history.append(result)
            if len(self.interface_history) > self.max_history_size:
                self.interface_history.pop(0)
            logger.info("✅ 히스토리 업데이트 완료")
        except Exception as e:
            logger.error(f"⚠️ 히스토리 업데이트 실패: {str(e)}")

    async def process_input(self, text: str, context: Dict = None, emotion: Dict = None, belief: Dict = None, wisdom: Dict = None, eora: Dict = None, system: Dict = None) -> Dict:
        """입력 처리 및 분석"""
        try:
            # 1. 캐시 확인
            cache_key = self._generate_cache_key(text, context or {})
            if cache_key in self.cache:
                logger.info("✅ 캐시된 결과 사용")
                return self.cache[cache_key]

            # 2. 임베딩 생성
            embedding = await embed_text_async(text)

            # 3. 분석 수행
            results = await asyncio.gather(
                analyze_emotion(text) if not emotion else emotion,
                analyze_context(text) if not context else context,
                self.belief_engine.analyze_belief(text, context) if not belief else belief,
                analyze_wisdom(text, context) if not wisdom else wisdom,
                analyze_consciousness(text, context),
                analyze_integration(text, context),
                analyze_transcendence(text, context),
                get_eora_core().analyze_eora(text, context, emotion, belief, wisdom) if not eora else eora,
                self.eora_system.analyze_system(text, context, emotion, belief, wisdom, eora) if not system else system,
                return_exceptions=True
            )

            # 4. 결과 통합
            result = {
                "text": text,
                "timestamp": datetime.now().isoformat(),
                "embedding": embedding,
                "emotion": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
                "context": results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])},
                "belief": results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])},
                "wisdom": results[3] if not isinstance(results[3], Exception) else {"error": str(results[3])},
                "consciousness": results[4] if not isinstance(results[4], Exception) else {"error": str(results[4])},
                "integration": results[5] if not isinstance(results[5], Exception) else {"error": str(results[5])},
                "transcendence": results[6] if not isinstance(results[6], Exception) else {"error": str(results[6])},
                "eora": results[7] if not isinstance(results[7], Exception) else {"error": str(results[7])},
                "system": results[8] if not isinstance(results[8], Exception) else {"error": str(results[8])}
            }

            # 5. 캐시 및 히스토리 업데이트
            self._update_cache(cache_key, result)
            self._update_history(result)

            logger.info("✅ 입력 처리 완료")
            return result

        except Exception as e:
            logger.error(f"⚠️ 입력 처리 실패: {str(e)}")
            error_result = self._create_default_interface()
            error_result["error"] = str(e)
            self._update_history(error_result)
            return error_result

    def _analyze_interface_category(self, text: str) -> Tuple[str, float]:
        """인터페이스 카테고리 분석"""
        try:
            max_score = 0.0
            best_category = "상호작용"
            
            for category, keywords in self.interface_categories.items():
                score = sum(1 for keyword in keywords if keyword in text)
                if score > max_score:
                    max_score = score
                    best_category = category
            
            # 점수 정규화
            normalized_score = min(max_score / 5, 1.0)
            
            return best_category, normalized_score
            
        except Exception as e:
            logger.error(f"⚠️ 인터페이스 카테고리 분석 실패: {str(e)}")
            return "상호작용", 0.5

    def _analyze_interface_level(self, text: str) -> Dict[str, Any]:
        """인터페이스 수준 분석"""
        try:
            level_scores = {}
            
            for level, indicators in self.interface_level_indicators.items():
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
            logger.error(f"⚠️ 인터페이스 수준 분석 실패: {str(e)}")
            return {"level": "중차", "score": 0.5}

    async def _analyze_interface_quality(self, text: str, embedding: List[float]) -> Dict[str, Any]:
        """인터페이스 품질 분석"""
        try:
            # 1. 임베딩 기반 품질 점수 계산
            quality_score = np.mean(embedding) if embedding else 0.5
            
            # 2. 인터페이스 가중치 적용
            weighted_score = sum(
                quality_score * weight 
                for weight in self.interface_weights.values()
            )
            
            # 3. 결과 생성
            return {
                "score": weighted_score,
                "confidence": min(weighted_score * 2, 1.0)
            }
            
        except Exception as e:
            logger.error(f"⚠️ 인터페이스 품질 분석 실패: {str(e)}")
            return {
                "score": 0.5,
                "confidence": 0.5
            }

    def _create_default_interface(self) -> Dict[str, Any]:
        """기본 인터페이스 결과 생성"""
        return {
            "category": {
                "name": "상호작용",
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
            "system": {
                "score": 0.5,
                "confidence": 0.5
            },
            "level": {
                "level": "중차",
                "score": 0.5
            },
            "interface_quality": {
                "score": 0.5,
                "confidence": 0.5
            },
            "context": {},
            "timestamp": datetime.now().isoformat()
        }

def get_eora_interface() -> EoraInterface:
    """EoraInterface 인스턴스 반환"""
    return EoraInterface() 