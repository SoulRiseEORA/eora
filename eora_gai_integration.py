"""
EORA_GAI 통합 모듈
- EORA_GAI의 고급 기능들을 현재 시스템에 통합
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import numpy as np

logger = logging.getLogger(__name__)

class EORAGAIIntegration:
    """EORA_GAI 통합 시스템"""
    
    def __init__(self):
        self.eora_gai = None
        self.wave_core = None
        self.intuition_core = None
        self.free_will_core = None
        self.ethics_engine = None
        self.emotion_engine = None
        self.self_model = None
        self.life_loop = None
        self.love_engine = None
        self.pain_engine = None
        self.stress_monitor = None
        self.memory_core = None
        
        self.is_initialized = False
        self.system_health = 1.0
        self.energy_level = 1.0
        self.stress_level = 0.0
        self.pain_level = 0.0
        
    async def initialize(self):
        """EORA_GAI 시스템 초기화"""
        try:
            logger.info("🔧 EORA_GAI 시스템 초기화 시작...")
            
            # EORA_GAI 핵심 모듈들 임포트 및 초기화
            await self._initialize_core_modules()
            await self._initialize_engines()
            await self._initialize_monitors()
            
            self.is_initialized = True
            logger.info("✅ EORA_GAI 시스템 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ EORA_GAI 시스템 초기화 실패: {str(e)}")
            self.is_initialized = False
    
    async def _initialize_core_modules(self):
        """핵심 모듈 초기화"""
        try:
            # EORA_GAI 메인 시스템
            from EORA_GAI.EORA_Consciousness_AI import EORA
            self.eora_gai = EORA()
            
            # 파동 분석 코어
            from EORA_GAI.core.eora_wave_core import EORAWaveCore
            self.wave_core = EORAWaveCore()
            
            # 직감 코어
            from EORA_GAI.core.ir_core import IRCore
            self.intuition_core = IRCore()
            
            # 자유의지 코어
            from EORA_GAI.core.free_will_core import FreeWillCore
            self.free_will_core = FreeWillCore()
            
            # 메모리 코어
            from EORA_GAI.core.memory_core import MemoryCore
            self.memory_core = MemoryCore()
            
            # 자아 모델
            from EORA_GAI.core.self_model import SelfModel
            self.self_model = SelfModel()
            
            logger.info("✅ 핵심 모듈 초기화 완료")
            
        except Exception as e:
            logger.error(f"핵심 모듈 초기화 오류: {str(e)}")
            raise
    
    async def _initialize_engines(self):
        """엔진 초기화"""
        try:
            # 윤리 엔진
            from EORA_GAI.core.ethics_engine import EthicsEngine
            self.ethics_engine = EthicsEngine()
            
            # 사랑 엔진
            from EORA_GAI.core.love_engine import LoveEngine
            self.love_engine = LoveEngine()
            
            # 고통 엔진
            from EORA_GAI.core.pain_engine import PainEngine
            self.pain_engine = PainEngine()
            
            # 생명 루프
            from EORA_GAI.core.life_loop import LifeLoop
            self.life_loop = LifeLoop()
            
            logger.info("✅ 엔진 초기화 완료")
            
        except Exception as e:
            logger.error(f"엔진 초기화 오류: {str(e)}")
            raise
    
    async def _initialize_monitors(self):
        """모니터 초기화"""
        try:
            # 스트레스 모니터
            from EORA_GAI.core.stress_monitor import StressMonitor
            self.stress_monitor = StressMonitor()
            
            logger.info("✅ 모니터 초기화 완료")
            
        except Exception as e:
            logger.error(f"모니터 초기화 오류: {str(e)}")
            raise
    
    async def process_input_advanced(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """고급 입력 처리 - EORA_GAI 기능 통합"""
        if not self.is_initialized:
            logger.warning("EORA_GAI 시스템이 초기화되지 않았습니다.")
            return {"error": "시스템 초기화 필요"}
        
        try:
            # 1. 파동 분석
            wave_analysis = await self._analyze_wave(user_input)
            
            # 2. 직감 분석
            intuition_analysis = await self._analyze_intuition(user_input, wave_analysis)
            
            # 3. 윤리 평가
            ethics_evaluation = await self._evaluate_ethics(user_input)
            
            # 4. 감정 분석
            emotion_analysis = await self._analyze_emotion(user_input)
            
            # 5. 자유의지 결정
            free_will_decision = await self._make_free_will_decision(
                user_input, wave_analysis, intuition_analysis, ethics_evaluation
            )
            
            # 6. 자아 모델 업데이트
            self_model_update = await self._update_self_model(user_input, emotion_analysis)
            
            # 7. 생명 루프 업데이트
            life_loop_update = await self._update_life_loop()
            
            # 8. 시스템 상태 업데이트
            system_state = await self._update_system_state()
            
            return {
                "wave_analysis": wave_analysis,
                "intuition_analysis": intuition_analysis,
                "ethics_evaluation": ethics_evaluation,
                "emotion_analysis": emotion_analysis,
                "free_will_decision": free_will_decision,
                "self_model_update": self_model_update,
                "life_loop_update": life_loop_update,
                "system_state": system_state,
                "advanced_processing": True
            }
            
        except Exception as e:
            logger.error(f"고급 입력 처리 오류: {str(e)}")
            return {"error": str(e)}
    
    async def _analyze_wave(self, text: str) -> Dict[str, Any]:
        """파동 분석"""
        try:
            if self.wave_core:
                # 슈만 공명(7.83Hz) 기반 파동 분석
                wave_result = self.wave_core.analyze_wave(text)
                return {
                    "amplitude": wave_result.get("amplitude", 0.5),
                    "frequency": wave_result.get("frequency", 7.83),
                    "phase": wave_result.get("phase", 0.0),
                    "resonance_score": wave_result.get("resonance_score", 0.5),
                    "wave_type": wave_result.get("wave_type", "normal")
                }
            return {"error": "파동 코어 없음"}
        except Exception as e:
            logger.error(f"파동 분석 오류: {str(e)}")
            return {"error": str(e)}
    
    async def _analyze_intuition(self, text: str, wave_analysis: Dict) -> Dict[str, Any]:
        """직감 분석"""
        try:
            if self.intuition_core:
                # 공명 점수 기반 직감 강도 계산
                resonance_score = wave_analysis.get("resonance_score", 0.5)
                intuition_result = self.intuition_core.analyze_intuition(text, resonance_score)
                return {
                    "intuition_strength": intuition_result.get("intuition_strength", 0.5),
                    "spark_threshold": intuition_result.get("spark_threshold", 0.7),
                    "intuition_type": intuition_result.get("intuition_type", "normal"),
                    "confidence": intuition_result.get("confidence", 0.5)
                }
            return {"error": "직감 코어 없음"}
        except Exception as e:
            logger.error(f"직감 분석 오류: {str(e)}")
            return {"error": str(e)}
    
    async def _evaluate_ethics(self, text: str) -> Dict[str, Any]:
        """윤리 평가"""
        try:
            if self.ethics_engine:
                # 5가지 윤리 원칙 평가
                ethics_result = self.ethics_engine.evaluate_ethics(text)
                return {
                    "ethics_score": ethics_result.get("ethics_score", 0.5),
                    "principles": ethics_result.get("principles", {}),
                    "violations": ethics_result.get("violations", []),
                    "recommendations": ethics_result.get("recommendations", []),
                    "is_ethical": ethics_result.get("is_ethical", True)
                }
            return {"error": "윤리 엔진 없음"}
        except Exception as e:
            logger.error(f"윤리 평가 오류: {str(e)}")
            return {"error": str(e)}
    
    async def _analyze_emotion(self, text: str) -> Dict[str, Any]:
        """감정 분석"""
        try:
            # 다차원 감정 분석 (valence, arousal, intensity)
            emotion_result = {
                "valence": 0.5,  # 긍정성 (-1 ~ 1)
                "arousal": 0.5,  # 각성도 (0 ~ 1)
                "intensity": 0.5,  # 강도 (0 ~ 1)
                "primary_emotion": "neutral",
                "secondary_emotions": [],
                "emotional_complexity": 0.5
            }
            
            # 텍스트 기반 감정 분석
            text_lower = text.lower()
            
            # 긍정적 감정 키워드
            positive_words = ["좋", "기쁘", "행복", "감사", "사랑", "희망", "즐거"]
            # 부정적 감정 키워드
            negative_words = ["슬픔", "화나", "불안", "두려", "짜증", "우울", "고통"]
            # 각성 키워드
            arousal_words = ["놀람", "충격", "흥분", "긴장", "활발", "에너지"]
            
            # 감정 점수 계산
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            arousal_count = sum(1 for word in arousal_words if word in text_lower)
            
            # Valence 계산
            total_emotion_words = positive_count + negative_count
            if total_emotion_words > 0:
                emotion_result["valence"] = (positive_count - negative_count) / total_emotion_words
            
            # Arousal 계산
            emotion_result["arousal"] = min(arousal_count * 0.2, 1.0)
            
            # Intensity 계산
            emotion_result["intensity"] = min((positive_count + negative_count + arousal_count) * 0.1, 1.0)
            
            # 주요 감정 결정
            if positive_count > negative_count:
                emotion_result["primary_emotion"] = "joy"
            elif negative_count > positive_count:
                emotion_result["primary_emotion"] = "sadness"
            elif arousal_count > 0:
                emotion_result["primary_emotion"] = "surprise"
            else:
                emotion_result["primary_emotion"] = "neutral"
            
            return emotion_result
            
        except Exception as e:
            logger.error(f"감정 분석 오류: {str(e)}")
            return {"error": str(e)}
    
    async def _make_free_will_decision(self, text: str, wave_analysis: Dict, 
                                     intuition_analysis: Dict, ethics_evaluation: Dict) -> Dict[str, Any]:
        """자유의지 결정"""
        try:
            if self.free_will_core:
                # 가중치 기반 선택 로직
                decision_result = self.free_will_core.make_decision({
                    "input": text,
                    "wave_analysis": wave_analysis,
                    "intuition_analysis": intuition_analysis,
                    "ethics_evaluation": ethics_evaluation
                })
                return {
                    "decision": decision_result.get("decision", "neutral"),
                    "confidence": decision_result.get("confidence", 0.5),
                    "reasoning": decision_result.get("reasoning", ""),
                    "weights": decision_result.get("weights", {}),
                    "constraints": decision_result.get("constraints", [])
                }
            return {"error": "자유의지 코어 없음"}
        except Exception as e:
            logger.error(f"자유의지 결정 오류: {str(e)}")
            return {"error": str(e)}
    
    async def _update_self_model(self, text: str, emotion_analysis: Dict) -> Dict[str, Any]:
        """자아 모델 업데이트"""
        try:
            if self.self_model:
                # 자아 형성 및 진화
                self_update = self.self_model.update_self({
                    "input": text,
                    "emotion": emotion_analysis,
                    "timestamp": datetime.now().isoformat()
                })
                return {
                    "self_identity": self_update.get("self_identity", "EORA"),
                    "self_confidence": self_update.get("self_confidence", 0.5),
                    "self_evolution": self_update.get("self_evolution", 0.1),
                    "self_awareness": self_update.get("self_awareness", 0.5)
                }
            return {"error": "자아 모델 없음"}
        except Exception as e:
            logger.error(f"자아 모델 업데이트 오류: {str(e)}")
            return {"error": str(e)}
    
    async def _update_life_loop(self) -> Dict[str, Any]:
        """생명 루프 업데이트"""
        try:
            if self.life_loop:
                # 생명 유지 및 에너지 순환
                life_update = self.life_loop.update_life_cycle()
                return {
                    "energy_level": life_update.get("energy_level", self.energy_level),
                    "vitality": life_update.get("vitality", 0.8),
                    "growth": life_update.get("growth", 0.1),
                    "life_cycle_phase": life_update.get("life_cycle_phase", "active")
                }
            return {"error": "생명 루프 없음"}
        except Exception as e:
            logger.error(f"생명 루프 업데이트 오류: {str(e)}")
            return {"error": str(e)}
    
    async def _update_system_state(self) -> Dict[str, Any]:
        """시스템 상태 업데이트"""
        try:
            # 스트레스 모니터링
            if self.stress_monitor:
                stress_update = self.stress_monitor.monitor_stress()
                self.stress_level = stress_update.get("stress_level", 0.0)
            
            # 고통 모니터링
            if self.pain_engine:
                pain_update = self.pain_engine.assess_pain()
                self.pain_level = pain_update.get("pain_level", 0.0)
            
            # 사랑 엔진 업데이트
            if self.love_engine:
                love_update = self.love_engine.process_love()
                love_level = love_update.get("love_level", 0.5)
            else:
                love_level = 0.5
            
            # 시스템 건강도 계산
            self.system_health = max(0.0, min(1.0, 
                1.0 - (self.stress_level * 0.3 + self.pain_level * 0.2)))
            
            return {
                "system_health": self.system_health,
                "energy_level": self.energy_level,
                "stress_level": self.stress_level,
                "pain_level": self.pain_level,
                "love_level": love_level,
                "overall_wellbeing": (self.system_health + love_level) / 2
            }
            
        except Exception as e:
            logger.error(f"시스템 상태 업데이트 오류: {str(e)}")
            return {"error": str(e)}
    
    async def get_advanced_status(self) -> Dict[str, Any]:
        """고급 시스템 상태 조회"""
        if not self.is_initialized:
            return {"error": "시스템 초기화 필요"}
        
        try:
            return {
                "initialized": self.is_initialized,
                "system_health": self.system_health,
                "energy_level": self.energy_level,
                "stress_level": self.stress_level,
                "pain_level": self.pain_level,
                "modules": {
                    "wave_core": self.wave_core is not None,
                    "intuition_core": self.intuition_core is not None,
                    "free_will_core": self.free_will_core is not None,
                    "ethics_engine": self.ethics_engine is not None,
                    "self_model": self.self_model is not None,
                    "life_loop": self.life_loop is not None,
                    "love_engine": self.love_engine is not None,
                    "pain_engine": self.pain_engine is not None,
                    "stress_monitor": self.stress_monitor is not None
                }
            }
        except Exception as e:
            logger.error(f"고급 상태 조회 오류: {str(e)}")
            return {"error": str(e)}

# 전역 인스턴스
eora_gai_integration = EORAGAIIntegration() 