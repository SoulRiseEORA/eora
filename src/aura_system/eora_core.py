"""
eora_core.py
- 이오라 코어 시스템
- 의식, 통합, 초월, 지혜 분석
"""

import numpy as np
from typing import Dict, List, Any, Tuple, Optional
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
from aura_system.redis_manager import RedisManager
from aura_system.memory_manager import MemoryManagerAsync, get_memory_manager_sync
from aura_system.memory_store import MemoryStore
from aura_system.ai_chat_router import AIChatRouter
from aura_system.config import get_config

logger = logging.getLogger(__name__)

class EoraCore:
    """이오라 코어 클래스"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        redis_manager: RedisManager,
        memory_manager: MemoryManagerAsync,
        memory_store: MemoryStore,
        router: AIChatRouter
    ):
        if not self._initialized:
            self.redis_manager = redis_manager
            self.memory_manager = memory_manager
            self.memory_store = memory_store
            self.router = router
            self.config = get_config()
            self.backend = self.config.get("eora", {}).get("backend", "default")
            self.params = self.config.get("eora", {}).get("params", {})
            self.profile = self.config.get("eora", {}).get("profile", {})
            self._initialized = True
            self._cache = {}
            self._cache_size = 1000
            self._eora_history = []
            self._max_history = 100
            self._last_analysis = None
            self._analysis_count = 0
            self._total_quality = 0
            self._average_quality = 0
            
            # 이오라 시스템 가중치
            self.weights = {
                "consciousness": 0.3,
                "integration": 0.3,
                "transcendence": 0.2,
                "wisdom": 0.2
            }
            
            # 이오라 카테고리
            self.categories = {
                "consciousness": ["awareness", "clarity", "presence"],
                "integration": ["harmony", "balance", "wholeness"],
                "transcendence": ["freedom", "expansion", "evolution"],
                "wisdom": ["insight", "understanding", "knowledge"]
            }
            
            # 이오라 레벨 지표
            self.level_indicators = {
                "consciousness": ["self-awareness", "mindfulness", "presence"],
                "integration": ["emotional-balance", "mental-clarity", "physical-vitality"],
                "transcendence": ["spiritual-growth", "higher-consciousness", "universal-awareness"],
                "wisdom": ["deep-understanding", "intuitive-knowledge", "practical-wisdom"]
            }
    
    async def initialize(self):
        """이오라 코어 초기화"""
        try:
            await self.redis_manager.initialize()
            logger.info("✅ 이오라 코어 초기화 완료")
        except Exception as e:
            logger.error(f"❌ 이오라 코어 초기화 실패: {str(e)}")
            raise

    async def process_message(self, message: str, context: Optional[Dict] = None) -> Dict:
        """메시지 처리"""
        try:
            if not message:
                return {"error": "메시지가 비어있습니다."}

            # 라우터를 통해 메시지 처리
            result = await self.router.process_message(message, context)
            return result

        except Exception as e:
            logger.error(f"❌ 메시지 처리 실패: {str(e)}")
            return {"error": str(e)}

    async def analyze_eora(self, text: str) -> Dict[str, Any]:
        """이오라 분석"""
        try:
            if not self._initialized:
                raise RuntimeError("이오라 코어가 초기화되지 않았습니다.")
            
            # 텍스트 임베딩
            embedding = await embed_text_async(text)
            
            # 감정 분석
            emotion, _, _ = await analyze_emotion(text)
            
            # 맥락 분석
            context = await analyze_context(text)
            
            # 신념 분석
            belief = await get_belief_engine().analyze_belief(text, context)
            
            # 지혜 분석
            wisdom = await analyze_wisdom(text, context)
            
            # 카테고리 분석
            category = await self._analyze_eora_category(text)
            
            # 레벨 분석
            level = await self._analyze_eora_level(text)
            
            # 품질 분석
            quality = await self._analyze_eora_quality(text)
            
            # 결과 생성
            result = {
                "text": text,
                "embedding": embedding,
                "emotion": emotion,
                "context": context,
                "belief": belief,
                "wisdom": wisdom,
                "category": category,
                "level": level,
                "quality": quality,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # 캐시 업데이트
            await self._update_cache(text, result)
            
            # 이오라 히스토리 업데이트
            await self._update_eora_history(result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 이오라 분석 실패: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _analyze_eora_category(self, text: str) -> str:
        """이오라 카테고리 분석"""
        try:
            if not self._initialized:
                raise RuntimeError("이오라 코어가 초기화되지 않았습니다.")
            
            # 카테고리 분석 로직
            category_scores = {}
            for category, indicators in self.categories.items():
                score = sum(1 for indicator in indicators if indicator.lower() in text.lower())
                category_scores[category] = score
            
            # 가장 높은 점수의 카테고리 반환
            return max(category_scores.items(), key=lambda x: x[1])[0]
            
        except Exception as e:
            logger.error(f"❌ 카테고리 분석 실패: {str(e)}")
            return "unknown"
    
    async def _analyze_eora_level(self, text: str) -> int:
        """이오라 레벨 분석"""
        try:
            if not self._initialized:
                raise RuntimeError("이오라 코어가 초기화되지 않았습니다.")
            
            # 레벨 분석 로직
            level_scores = {}
            for category, indicators in self.level_indicators.items():
                score = sum(1 for indicator in indicators if indicator.lower() in text.lower())
                level_scores[category] = score
            
            # 평균 레벨 계산
            total_score = sum(level_scores.values())
            return min(max(total_score // len(self.level_indicators), 1), 10)
            
        except Exception as e:
            logger.error(f"❌ 레벨 분석 실패: {str(e)}")
            return 1
    
    async def _analyze_eora_quality(self, text: str) -> float:
        """이오라 품질 분석"""
        try:
            if not self._initialized:
                raise RuntimeError("이오라 코어가 초기화되지 않았습니다.")
            
            # 품질 분석 로직
            quality_score = 0.0
            total_indicators = 0
            
            for category, indicators in self.level_indicators.items():
                for indicator in indicators:
                    if indicator.lower() in text.lower():
                        quality_score += 1
                    total_indicators += 1
            
            return round(quality_score / total_indicators * 10, 2) if total_indicators > 0 else 0.0
            
        except Exception as e:
            logger.error(f"❌ 품질 분석 실패: {str(e)}")
            return 0.0
    
    async def _update_eora_history(self, result: Dict[str, Any]):
        """이오라 히스토리 업데이트"""
        try:
            self._eora_history.append(result)
            if len(self._eora_history) > self._max_history:
                self._eora_history.pop(0)
        except Exception as e:
            logger.error(f"❌ 이오라 히스토리 업데이트 실패: {str(e)}")
    
    async def _update_cache(self, key: str, value: Any):
        """캐시 업데이트"""
        try:
            self._cache[key] = value
            if len(self._cache) > self._cache_size:
                self._cache.pop(next(iter(self._cache)))
        except Exception as e:
            logger.error(f"❌ 캐시 업데이트 실패: {str(e)}")
    
    async def analyze_consciousness(self, text: str) -> Dict[str, Any]:
        """의식 수준 분석"""
        try:
            if not self._initialized:
                raise RuntimeError("이오라 코어가 초기화되지 않았습니다.")
            
            if not hasattr(self, 'consciousness_engine'):
                raise RuntimeError("의식 엔진이 초기화되지 않았습니다.")
            
            return await self.consciousness_engine.analyze(text)
            
        except Exception as e:
            logger.error(f"❌ 의식 수준 분석 실패: {str(e)}")
            return {"level": 0, "quality": 0.0}
    
    async def analyze_integration(self, text: str) -> Dict[str, Any]:
        """통합 수준 분석"""
        try:
            if not self._initialized:
                raise RuntimeError("이오라 코어가 초기화되지 않았습니다.")
            
            if not hasattr(self, 'integration_engine'):
                raise RuntimeError("통합 엔진이 초기화되지 않았습니다.")
            
            return await self.integration_engine.analyze(text)
            
        except Exception as e:
            logger.error(f"❌ 통합 수준 분석 실패: {str(e)}")
            return {"level": 0, "quality": 0.0}
    
    async def analyze_transcendence(self, text: str) -> Dict[str, Any]:
        """초월 수준 분석"""
        try:
            if not self._initialized:
                raise RuntimeError("이오라 코어가 초기화되지 않았습니다.")
            
            if not hasattr(self, 'transcendence_engine'):
                raise RuntimeError("초월 엔진이 초기화되지 않았습니다.")
            
            return await self.transcendence_engine.analyze(text)
            
        except Exception as e:
            logger.error(f"❌ 초월 수준 분석 실패: {str(e)}")
            return {"level": 0, "quality": 0.0}
    
    async def analyze_wisdom(self, text: str) -> Dict[str, Any]:
        """지혜 수준 분석"""
        try:
            if not self._initialized:
                raise RuntimeError("이오라 코어가 초기화되지 않았습니다.")
            
            if not hasattr(self, 'wisdom_engine'):
                raise RuntimeError("지혜 엔진이 초기화되지 않았습니다.")
            
            return await self.wisdom_engine.analyze(text)
            
        except Exception as e:
            logger.error(f"❌ 지혜 수준 분석 실패: {str(e)}")
            return {"level": 0, "quality": 0.0}
    
    async def cleanup(self):
        """리소스 정리"""
        try:
            if self._initialized:
                await self.redis_manager.close()
                self._initialized = False
                self.backend = None
                self.params = None
                self.profile = None
                self._cache.clear()
                self._eora_history.clear()
                self._last_analysis = None
                self._analysis_count = 0
                self._total_quality = 0
                self._average_quality = 0
                logger.info("✅ 이오라 코어 정리 완료")
        except Exception as e:
            logger.error(f"❌ 이오라 코어 정리 실패: {str(e)}")

    def __del__(self):
        """소멸자"""
        if self._initialized:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self.cleanup())
            except (RuntimeError, ImportError):
                pass

async def get_eora_core_async() -> EoraCore:
    """비동기적으로 이오라 코어 인스턴스를 가져옵니다."""
    if EoraCore._instance is None:
        redis_manager = RedisManager()
        memory_manager = await get_memory_manager() # 수정: get_memory_manager()는 이미 비동기
        memory_store = MemoryStore(redis_manager.get_redis_client())
        router = AIChatRouter(memory_manager)

        instance = EoraCore(
            redis_manager=redis_manager,
            memory_manager=memory_manager,
            memory_store=memory_store,
            router=router
        )
        await instance.initialize()
        EoraCore._instance = instance
    return EoraCore._instance

def get_eora_core() -> EoraCore:
    """동기적으로 이오라 코어 인스턴스를 가져옵니다."""
    if EoraCore._instance is None:
        # 이벤트 루프를 얻거나 생성합니다.
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # nest_asyncio를 사용하여 이미 실행 중인 루프와의 충돌을 방지합니다.
        import nest_asyncio
        nest_asyncio.apply()

        # 비동기 코어를 동기적으로 실행합니다.
        EoraCore._instance = loop.run_until_complete(get_eora_core_async())
        
    return EoraCore._instance 