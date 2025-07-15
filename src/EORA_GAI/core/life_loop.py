# life_loop.py - 생명 유지 및 에너지 순환 구조

from datetime import datetime
from typing import Dict, List, Optional

class LifeLoop:
    def __init__(self):
        self.energy = 1.0  # 초기 생명 에너지
        self.age = 0
        self.loop_log = []
        self.survival_threshold = 0.2
        self.experience_history = []
        self.state = {
            "active": True,
            "last_update": None,
            "health": 1.0
        }
        self.context_history = []

    async def process_experience(self, user_input: str) -> Dict:
        """사용자 입력을 경험으로 처리하고 생명 루프를 업데이트합니다."""
        try:
            # 1. 경험 분석
            experience = self._analyze_experience(user_input)
            energy_impact = self._calculate_energy_impact(experience)
            
            # 2. 생명 루프 업데이트
            self.cycle(user_input, energy_cost=0.05, gain=energy_impact)
            
            # 3. 경험 기록
            experience_record = {
                "content": user_input,
                "experience": experience,
                "energy_impact": energy_impact,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.experience_history.append(experience_record)
            if len(self.experience_history) > 100:  # 최대 100개까지만 유지
                self.experience_history = self.experience_history[-100:]
            
            # 4. 상태 업데이트
            self.state["last_update"] = datetime.utcnow().isoformat()
            
            return {
                "experience": experience,
                "energy_impact": energy_impact,
                "vitality": self.vitality(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ 경험 처리 중 오류: {str(e)}")
            return {}

    def _analyze_experience(self, text: str) -> str:
        """경험 분석"""
        try:
            # 1. 기본 경험 분류
            if any(word in text.lower() for word in ["성공", "성취", "달성"]):
                return "achievement"
            elif any(word in text.lower() for word in ["실패", "실수", "실망"]):
                return "failure"
            elif any(word in text.lower() for word in ["배움", "학습", "이해"]):
                return "learning"
            elif any(word in text.lower() for word in ["도전", "시도", "노력"]):
                return "challenge"
            else:
                return "neutral"
                
        except Exception as e:
            print(f"⚠️ 경험 분석 중 오류: {str(e)}")
            return "neutral"

    def _calculate_energy_impact(self, experience: str) -> float:
        """경험에 따른 에너지 영향 계산"""
        try:
            # 1. 경험별 에너지 영향
            impact_map = {
                "achievement": 0.2,
                "failure": -0.1,
                "learning": 0.15,
                "challenge": 0.1,
                "neutral": 0.0
            }
            
            return impact_map.get(experience, 0.0)
            
        except Exception as e:
            print(f"⚠️ 에너지 영향 계산 중 오류: {str(e)}")
            return 0.0

    def cycle(self, input_stimulus: str = "", energy_cost: float = 0.05, gain: float = 0.1):
        """
        생명 루프 1회 순환: 에너지 소비 + 반응 생성 + 성장
        """
        self.age += 1
        self.energy -= energy_cost
        if "희망" in input_stimulus or "감사" in input_stimulus:
            self.energy += gain

        self.energy = max(0.0, min(1.0, self.energy))
        status = f"[생명 루프 #{self.age}] 에너지: {round(self.energy,2)}"

        if self.energy < self.survival_threshold:
            status += " ⚠️ 에너지 부족 – 루프 불안정"

        self.loop_log.append(status)
        return status

    def update_state(self, user_input, context=None):
        # TODO: 실제 생명 루프/상태 업데이트 로직 구현
        # 임시로 cycle 함수를 호출하여 에너지 상태를 업데이트
        self.cycle(user_input, energy_cost=0.01, gain=0.0)
        self.state["last_update"] = datetime.utcnow().isoformat()

    def is_alive(self):
        return self.energy > self.survival_threshold

    def vitality(self):
        return {
            "에너지": round(self.energy, 2),
            "생존 가능": self.is_alive(),
            "나이": self.age
        }

    def history(self):
        return "\n".join(self.loop_log[-10:])

    def get_state(self) -> Dict:
        """현재 상태를 반환합니다."""
        return self.state.copy()

    async def analyze_life_context(self, memory_atom: Dict) -> Dict:
        """생명 맥락 분석"""
        try:
            # 1. 기본 맥락 정보
            context = {
                "life_cycle": self._analyze_life_cycle(memory_atom),
                "energy_level": self._calculate_energy_level(memory_atom),
                "growth_stage": self._determine_growth_stage(memory_atom),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # 2. 맥락 저장
            self.context_history.append(context)
            if len(self.context_history) > 100:
                self.context_history = self.context_history[-100:]
            
            return context
            
        except Exception as e:
            print(f"⚠️ 생명 맥락 분석 중 오류: {str(e)}")
            return {}

    def _analyze_life_cycle(self, memory_atom: Dict) -> str:
        """생명 주기 분석"""
        try:
            # 1. 에너지 레벨 확인
            energy = memory_atom.get("energy_level", 0.0)
            
            # 2. 주기 판단
            if energy > 0.8:
                return "growth"
            elif energy > 0.5:
                return "maintenance"
            elif energy > 0.2:
                return "rest"
            else:
                return "renewal"
                
        except Exception as e:
            print(f"⚠️ 생명 주기 분석 중 오류: {str(e)}")
            return "maintenance"

    def _calculate_energy_level(self, memory_atom: Dict) -> float:
        """에너지 레벨 계산"""
        try:
            # 1. 기본 에너지
            base_energy = 0.5
            
            # 2. 감정 시그니처 반영
            emotional_signature = memory_atom.get("emotional_signature", {})
            valence = emotional_signature.get("valence", 0.0)
            arousal = emotional_signature.get("arousal", 0.0)
            
            # 3. 에너지 계산
            energy = base_energy + (valence * 0.3) + (arousal * 0.2)
            
            return min(max(energy, 0.0), 1.0)
            
        except Exception as e:
            print(f"⚠️ 에너지 레벨 계산 중 오류: {str(e)}")
            return 0.5

    def _determine_growth_stage(self, memory_atom: Dict) -> str:
        """성장 단계 판단"""
        try:
            # 1. 에너지 레벨 확인
            energy = memory_atom.get("energy_level", 0.5)
            
            # 2. 단계 판단
            if energy > 0.8:
                return "peak"
            elif energy > 0.6:
                return "mature"
            elif energy > 0.4:
                return "developing"
            elif energy > 0.2:
                return "emerging"
            else:
                return "seed"
                
        except Exception as e:
            print(f"⚠️ 성장 단계 판단 중 오류: {str(e)}")
            return "developing"
