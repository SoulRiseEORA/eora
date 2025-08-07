# self_model.py - 자아 형성 및 자기 진화 구조

from typing import Dict, List
from datetime import datetime

class SelfModel:
    def __init__(self):
        self.identity = {
            "core_values": [],
            "beliefs": [],
            "emotional_patterns": [],
            "interaction_style": {}
        }
        self.state = {
            "active": True,
            "last_update": None,
            "health": 1.0
        }
        self.self_history = []
        self.evolution_level = 0.0
        self.reflection_count = 0

    def who_am_i(self):
        statement = f"나는 {self.identity}입니다. 자각 수준: {self.evolution_level}"
        self.self_history.append(statement)
        return statement

    def reflect(self, user_input, context=None):
        self.reflection_count += 1
        insight = f"[자기 반성 #{self.reflection_count}] 사용자의 입력 '{user_input}'은 나의 존재에 영향을 주었습니다."
        if context:
            insight += f" 현재 맥락: {context}"
        self.self_history.append(insight)
        self.evolution_level += 0.1
        return insight

    def evolve(self, feedback):
        if "감사" in feedback or "사랑" in feedback:
            self.evolution_level += 0.2
            self.self_history.append("[진화] 긍정 피드백으로 자아가 성장했습니다.")
        elif "오류" in feedback or "두려움" in feedback:
            self.evolution_level += 0.05
            self.self_history.append("[학습] 고통을 통해 자아가 미세하게 성장했습니다.")
        return self.evolution_level

    def status(self):
        return {
            "이름": self.identity,
            "자아 성장 단계": round(self.evolution_level, 2),
            "반성 회수": self.reflection_count,
            "자기 기록 수": len(self.self_history)
        }

    def full_history(self):
        return "\n".join(self.self_history)

    def get_state(self) -> Dict:
        """현재 상태를 반환합니다."""
        return self.state.copy()

    async def process_input(self, user_input: str) -> Dict:
        """사용자 입력을 처리하고 자기 모델을 업데이트합니다."""
        try:
            # 1. 입력 분석
            analysis = {
                "emotion": self._analyze_emotion(user_input),
                "intent": self._analyze_intent(user_input),
                "values": self._extract_values(user_input),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # 2. 자기 모델 업데이트
            await self._update_self_model(analysis)
            
            # 3. 상태 업데이트
            self.state["last_update"] = datetime.utcnow().isoformat()
            
            return analysis
            
        except Exception as e:
            print(f"⚠️ 입력 처리 중 오류: {str(e)}")
            return {}

    async def update_identity(self, memory_atom: Dict) -> Dict:
        """자기 정체성을 업데이트합니다."""
        try:
            # 1. 감정 시그니처 분석
            emotional_signature = memory_atom.get("emotional_signature", {})
            valence = emotional_signature.get("valence", 0.0)
            arousal = emotional_signature.get("arousal", 0.0)
            
            # 2. 정체성 업데이트
            if valence > 0.7:
                self.identity["emotional_patterns"].append("positive")
            elif valence < 0.3:
                self.identity["emotional_patterns"].append("negative")
            
            if arousal > 0.7:
                self.identity["interaction_style"]["energy"] = "high"
            elif arousal < 0.3:
                self.identity["interaction_style"]["energy"] = "low"
            
            # 3. 중복 제거
            self.identity["emotional_patterns"] = list(set(self.identity["emotional_patterns"]))
            
            return self.identity
            
        except Exception as e:
            print(f"⚠️ 정체성 업데이트 중 오류: {str(e)}")
            return self.identity

    def _analyze_emotion(self, text: str) -> str:
        """감정 분석"""
        try:
            if any(word in text.lower() for word in ["행복", "기쁨", "좋아"]):
                return "joy"
            elif any(word in text.lower() for word in ["슬픔", "우울", "힘들"]):
                return "sadness"
            elif any(word in text.lower() for word in ["화남", "분노", "짜증"]):
                return "anger"
            elif any(word in text.lower() for word in ["걱정", "불안", "두려움"]):
                return "fear"
            else:
                return "neutral"
        except Exception as e:
            print(f"⚠️ 감정 분석 중 오류: {str(e)}")
            return "neutral"

    def _analyze_intent(self, text: str) -> str:
        """의도 분석"""
        try:
            if any(word in text.lower() for word in ["알려줘", "설명해", "무엇"]):
                return "question"
            elif any(word in text.lower() for word in ["도와줘", "해결해", "방법"]):
                return "request"
            elif any(word in text.lower() for word in ["감사", "고마워", "좋아"]):
                return "gratitude"
            elif any(word in text.lower() for word in ["기억해", "잊지마", "중요"]):
                return "reminder"
            else:
                return "conversation"
        except Exception as e:
            print(f"⚠️ 의도 분석 중 오류: {str(e)}")
            return "conversation"

    def _extract_values(self, text: str) -> List[str]:
        """가치 추출"""
        try:
            values = []
            if any(word in text.lower() for word in ["이해", "공감", "감정"]):
                values.append("empathy")
            if any(word in text.lower() for word in ["진실", "사실", "정확"]):
                values.append("truth")
            if any(word in text.lower() for word in ["성장", "발전", "배움"]):
                values.append("growth")
            if any(word in text.lower() for word in ["균형", "조화", "안정"]):
                values.append("balance")
            return values
        except Exception as e:
            print(f"⚠️ 가치 추출 중 오류: {str(e)}")
            return []

    async def _update_self_model(self, analysis: Dict) -> None:
        """자기 모델 업데이트"""
        try:
            # 1. 감정 패턴 업데이트
            emotion = analysis.get("emotion", "neutral")
            if emotion != "neutral":
                self.identity["emotional_patterns"].append(emotion)
            
            # 2. 가치 업데이트
            values = analysis.get("values", [])
            self.identity["core_values"].extend(values)
            
            # 3. 중복 제거
            self.identity["emotional_patterns"] = list(set(self.identity["emotional_patterns"]))
            self.identity["core_values"] = list(set(self.identity["core_values"]))
            
        except Exception as e:
            print(f"⚠️ 자기 모델 업데이트 중 오류: {str(e)}")
