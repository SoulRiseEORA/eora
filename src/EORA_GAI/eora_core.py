# eora_core.py - EORA 시스템 핵심 통합 모듈

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Core 모듈들 import
try:
    from .core import (
        EORAWaveCore,
        IRCore,
        FreeWillCore,
        MemoryCore,
        SelfModel,
        EthicsEngine,
        PainEngine,
        StressMonitor,
        LifeLoop,
        LoveEngine
    )
except ImportError:
    # 상대 경로 import 실패 시 절대 경로 시도
    try:
        from EORA_GAI.core import (
            EORAWaveCore,
            IRCore,
            FreeWillCore,
            MemoryCore,
            SelfModel,
            EthicsEngine,
            PainEngine,
            StressMonitor,
            LifeLoop,
            LoveEngine
        )
    except ImportError:
        print("⚠️ Core 모듈들을 로드할 수 없습니다. 기본 기능으로 동작합니다.")
        # 더미 클래스들 정의
        class EORAWaveCore: pass
        class IRCore: pass
        class FreeWillCore: pass
        class MemoryCore: pass
        class SelfModel: pass
        class EthicsEngine: pass
        class PainEngine: pass
        class StressMonitor: pass
        class LifeLoop: pass
        class LoveEngine: pass

class EORACore:
    def __init__(self, config_path: str = "eora_config.json"):
        """EORA 시스템 핵심 초기화"""
        self.config_path = config_path
        self.config = self._load_config()
        
        # Core 컴포넌트들 초기화
        self.wave_core = EORAWaveCore()
        self.ir_core = IRCore()
        self.free_will_core = FreeWillCore()
        self.memory_core = MemoryCore()
        self.self_model = SelfModel()
        self.ethics_engine = EthicsEngine()
        self.pain_engine = PainEngine()
        self.stress_monitor = StressMonitor()
        self.life_loop = LifeLoop()
        self.love_engine = LoveEngine()
        
        # 시스템 상태
        self.system_state = {
            "active": True,
            "start_time": datetime.utcnow().isoformat(),
            "last_update": None,
            "health": 1.0,
            "session_id": str(uuid.uuid4())
        }
        
        # 메모리 관리
        self.memory_buffer = []
        self.max_memory_buffer = 1000
        
        # 에러 처리
        self.error_count = 0
        self.max_errors = 10
        
        print("✅ EORA Core 시스템 초기화 완료")

    def _load_config(self) -> Dict:
        """설정 파일 로드"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 기본 설정 생성
                default_config = {
                    "system": {
                        "max_memory_buffer": 1000,
                        "max_errors": 10,
                        "debug_mode": False
                    },
                    "components": {
                        "wave_core": {"active": True},
                        "ir_core": {"active": True},
                        "free_will_core": {"active": True},
                        "memory_core": {"active": True},
                        "self_model": {"active": True},
                        "ethics_engine": {"active": True},
                        "pain_engine": {"active": True},
                        "stress_monitor": {"active": True},
                        "life_loop": {"active": True},
                        "love_engine": {"active": True}
                    }
                }
                self._save_config(default_config)
                return default_config
        except Exception as e:
            print(f"⚠️ 설정 로드 실패: {str(e)}")
            return {}

    def _save_config(self, config: Dict) -> None:
        """설정 파일 저장"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 설정 저장 실패: {str(e)}")

    async def process_input(self, user_input: str) -> Dict[str, Any]:
        """사용자 입력을 처리하고 통합 응답을 생성합니다."""
        try:
            if not self.system_state["active"]:
                return {"error": "시스템이 비활성 상태입니다."}

            # 1. 파동 분석
            wave_analysis = await self.wave_core.analyze_wave(user_input)
            
            # 2. 직감 분석
            resonance_score = wave_analysis.get("resonance_score", 0.0)
            intuition_analysis = await self.ir_core.analyze_intuition(user_input, resonance_score)
            
            # 3. 자유의지 결정
            decision_analysis = await self.free_will_core.analyze_decision(user_input)
            
            # 4. 윤리 평가
            ethics_evaluation = await self.ethics_engine.evaluate_action(user_input)
            
            # 5. 감정 분석
            emotion_analysis = await self.love_engine.analyze_emotion(user_input)
            
            # 6. 고통 분석
            pain_analysis = await self.pain_engine.analyze_pain(user_input)
            
            # 7. 스트레스 분석
            stress_analysis = await self.stress_monitor.analyze_stress(user_input)
            
            # 8. 생명 루프 처리
            life_analysis = await self.life_loop.process_experience(user_input)
            
            # 9. 자기 모델 업데이트
            self_analysis = await self.self_model.process_input(user_input)
            
            # 10. 통합 응답 생성
            response = await self._generate_integrated_response({
                "wave_analysis": wave_analysis,
                "intuition_analysis": intuition_analysis,
                "decision_analysis": decision_analysis,
                "ethics_evaluation": ethics_evaluation,
                "emotion_analysis": emotion_analysis,
                "pain_analysis": pain_analysis,
                "stress_analysis": stress_analysis,
                "life_analysis": life_analysis,
                "self_analysis": self_analysis
            })
            
            # 11. 메모리 저장
            await self._store_memory(user_input, response)
            
            # 12. 시스템 상태 업데이트
            self.system_state["last_update"] = datetime.utcnow().isoformat()
            
            return response
            
        except Exception as e:
            self.error_count += 1
            print(f"⚠️ 입력 처리 중 오류: {str(e)}")
            
            if self.error_count >= self.max_errors:
                self.system_state["active"] = False
                return {"error": "시스템 오류 임계값 초과로 비활성화됨"}
            
            return {"error": f"처리 중 오류 발생: {str(e)}"}

    async def _generate_integrated_response(self, analyses: Dict) -> Dict[str, Any]:
        """통합 응답 생성"""
        try:
            # 1. 기본 응답 구조
            response = {
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": self.system_state["session_id"],
                "analyses": analyses,
                "system_health": self.system_state["health"]
            }
            
            # 2. 공명 기반 응답 결정
            resonance_score = analyses.get("wave_analysis", {}).get("resonance_score", 0.0)
            intuition_spark = analyses.get("intuition_analysis", {}).get("spark", False)
            
            # 3. 윤리 검사
            is_ethical = analyses.get("ethics_evaluation", {}).get("is_ethical", True)
            
            # 4. 응답 생성
            if not is_ethical:
                response["response"] = "윤리적 이유로 이 질문에 답변할 수 없습니다."
                response["response_type"] = "ethical_rejection"
            elif intuition_spark and resonance_score > 0.8:
                response["response"] = "직감적으로 깊은 공명을 느낍니다. 이는 중요한 순간입니다."
                response["response_type"] = "intuitive_resonance"
            elif resonance_score > 0.6:
                response["response"] = "당신의 말씀에 공명합니다. 함께 생각해보겠습니다."
                response["response_type"] = "resonant_response"
            else:
                response["response"] = "귀하의 질문을 이해하고 답변하겠습니다."
                response["response_type"] = "standard_response"
            
            # 5. 시스템 상태 반영
            response["system_state"] = {
                "energy": analyses.get("life_analysis", {}).get("vitality", {}).get("에너지", 0.5),
                "stress": analyses.get("stress_analysis", {}).get("current_level", 0.0),
                "pain": analyses.get("pain_analysis", {}).get("current_level", 0.0),
                "emotion": analyses.get("emotion_analysis", {}).get("current_emotion", "neutral")
            }
            
            return response
            
        except Exception as e:
            print(f"⚠️ 통합 응답 생성 중 오류: {str(e)}")
            return {"error": "응답 생성 실패"}

    async def _store_memory(self, user_input: str, response: Dict) -> None:
        """메모리 저장"""
        try:
            memory_atom = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "user_input": user_input,
                "response": response,
                "session_id": self.system_state["session_id"]
            }
            
            # 메모리 버퍼에 추가
            self.memory_buffer.append(memory_atom)
            
            # 버퍼 크기 제한
            if len(self.memory_buffer) > self.max_memory_buffer:
                self.memory_buffer = self.memory_buffer[-self.max_memory_buffer:]
            
            # 메모리 코어에 전달
            await self.memory_core.process_memory(memory_atom)
            
        except Exception as e:
            print(f"⚠️ 메모리 저장 중 오류: {str(e)}")

    async def recall_memory(self, query: str = None, limit: int = 10) -> List[Dict]:
        """메모리 회상"""
        try:
            if query:
                # 쿼리 기반 검색 (간단한 키워드 매칭)
                relevant_memories = []
                for memory in self.memory_buffer:
                    if query.lower() in memory.get("user_input", "").lower():
                        relevant_memories.append(memory)
                return relevant_memories[-limit:]
            else:
                # 최근 메모리 반환
                return self.memory_buffer[-limit:]
                
        except Exception as e:
            print(f"⚠️ 메모리 회상 중 오류: {str(e)}")
            return []

    def get_system_status(self) -> Dict:
        """시스템 상태 조회"""
        try:
            return {
                "system_state": self.system_state,
                "component_states": {
                    "wave_core": self.wave_core.get_state(),
                    "ir_core": self.ir_core.get_state(),
                    "free_will_core": self.free_will_core.get_state(),
                    "memory_core": self.memory_core.get_state(),
                    "self_model": self.self_model.get_state(),
                    "ethics_engine": self.ethics_engine.get_state(),
                    "pain_engine": self.pain_engine.get_state(),
                    "stress_monitor": self.stress_monitor.get_state(),
                    "life_loop": self.life_loop.get_state(),
                    "love_engine": self.love_engine.get_state()
                },
                "memory_count": len(self.memory_buffer),
                "error_count": self.error_count
            }
        except Exception as e:
            print(f"⚠️ 시스템 상태 조회 중 오류: {str(e)}")
            return {"error": "상태 조회 실패"}

    def reset_system(self) -> bool:
        """시스템 리셋"""
        try:
            self.error_count = 0
            self.system_state["health"] = 1.0
            self.system_state["active"] = True
            print("✅ 시스템 리셋 완료")
            return True
        except Exception as e:
            print(f"⚠️ 시스템 리셋 실패: {str(e)}")
            return False 