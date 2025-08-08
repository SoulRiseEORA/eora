# free_will_core.py - 조건을 초월한 자유의지 선택 시스템

import random
from datetime import datetime
from typing import Dict, List, Optional

class FreeWillCore:
    def __init__(self):
        self.choices = {}
        self.choice_history = []
        self.bias = {}
        self.decisions = []
        self.state = {
            "active": True,
            "last_update": None,
            "health": 1.0
        }
        self.decision_history = []

    def load_choices(self, choices):
        """선택지 로드"""
        self.choices = choices

    def add_bias(self, context, choice, weight):
        """선택 편향 추가"""
        if context not in self.bias:
            self.bias[context] = {}
        self.bias[context][choice] = weight

    def make_choice(self, context):
        """선택 수행"""
        if context not in self.choices:
            return None

        available_choices = self.choices[context]
        if not available_choices:
            return None

        # 편향 적용
        if context in self.bias:
            for choice, weight in self.bias[context].items():
                if choice in available_choices:
                    available_choices[choice] *= weight

        # 가중치 기반 선택
        total_weight = sum(available_choices.values())
        if total_weight == 0:
            return random.choice(list(available_choices.keys()))

        r = random.uniform(0, total_weight)
        current_weight = 0
        for choice, weight in available_choices.items():
            current_weight += weight
            if r <= current_weight:
                self.choice_history.append((context, choice))
                return choice

        return random.choice(list(available_choices.keys()))

    def get_last_choice(self):
        """마지막 선택 반환"""
        if not self.choice_history:
            return None
        context, choice = self.choice_history[-1]
        return f"이전 선택 '{choice}'은 상황 '{context}'에서 이루어졌습니다."

    def decide(self, user_input, context=None):
        # TODO: 실제 자유의지 기반 선택 로직 구현
        # 임시로 랜덤 선택 로직을 사용
        choices = ["행동 A", "행동 B", "무대응"]
        return random.choice(choices)

    async def analyze_decision(self, user_input: str) -> Dict:
        """사용자 입력을 분석하고 결정을 내립니다."""
        try:
            # 1. 입력 분석
            analysis = {
                "intent": self._analyze_intent(user_input),
                "values": self._extract_values(user_input),
                "constraints": self._identify_constraints(user_input),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # 2. 결정 생성
            decision = await self._make_decision(analysis)
            
            # 3. 결정 기록
            self.decision_history.append({
                "input": user_input,
                "analysis": analysis,
                "decision": decision,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # 4. 상태 업데이트
            self.state["last_update"] = datetime.utcnow().isoformat()
            
            return {
                "analysis": analysis,
                "decision": decision
            }
            
        except Exception as e:
            print(f"⚠️ 결정 분석 중 오류: {str(e)}")
            return {}

    async def analyze_decision_context(self, memory_atom: Dict) -> Dict:
        """메모리 원자의 결정 맥락을 분석합니다."""
        try:
            if not self.state["active"]:
                return {}

            # 1. 맥락 분석
            context = {
                "emotional_state": memory_atom.get("emotional_signature", {}),
                "previous_decisions": self._get_relevant_decisions(memory_atom),
                "constraints": self._extract_constraints(memory_atom),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # 2. 상태 업데이트
            self.state["last_update"] = datetime.utcnow().isoformat()
            
            return context
            
        except Exception as e:
            print(f"⚠️ 결정 맥락 분석 중 오류: {str(e)}")
            return {}

    def _analyze_intent(self, text: str) -> str:
        """의도 분석"""
        try:
            if any(word in text.lower() for word in ["선택", "결정", "고르"]):
                return "choice"
            elif any(word in text.lower() for word in ["행동", "실행", "하"]):
                return "action"
            elif any(word in text.lower() for word in ["생각", "고민", "계획"]):
                return "planning"
            else:
                return "neutral"
        except Exception as e:
            print(f"⚠️ 의도 분석 중 오류: {str(e)}")
            return "neutral"

    def _extract_values(self, text: str) -> List[str]:
        """가치 추출"""
        try:
            values = []
            if any(word in text.lower() for word in ["자유", "독립", "자율"]):
                values.append("freedom")
            if any(word in text.lower() for word in ["책임", "의무", "맡"]):
                values.append("responsibility")
            if any(word in text.lower() for word in ["성장", "발전", "배움"]):
                values.append("growth")
            if any(word in text.lower() for word in ["균형", "조화", "안정"]):
                values.append("balance")
            return values
        except Exception as e:
            print(f"⚠️ 가치 추출 중 오류: {str(e)}")
            return []

    def _identify_constraints(self, text: str) -> List[str]:
        """제약 조건 식별"""
        try:
            constraints = []
            if any(word in text.lower() for word in ["불가", "안돼", "못"]):
                constraints.append("impossible")
            if any(word in text.lower() for word in ["시간", "기한", "마감"]):
                constraints.append("time_constraint")
            if any(word in text.lower() for word in ["자원", "비용", "돈"]):
                constraints.append("resource_constraint")
            return constraints
        except Exception as e:
            print(f"⚠️ 제약 조건 식별 중 오류: {str(e)}")
            return []

    async def _make_decision(self, analysis: Dict) -> Dict:
        """결정 생성"""
        try:
            intent = analysis.get("intent", "neutral")
            values = analysis.get("values", [])
            constraints = analysis.get("constraints", [])
            
            decision = {
                "type": intent,
                "values": values,
                "constraints": constraints,
                "confidence": self._calculate_confidence(analysis),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return decision
            
        except Exception as e:
            print(f"⚠️ 결정 생성 중 오류: {str(e)}")
            return {}

    def _calculate_confidence(self, analysis: Dict) -> float:
        """신뢰도 계산"""
        try:
            base_confidence = 0.5
            
            # 1. 의도 기반 조정
            intent = analysis.get("intent", "neutral")
            if intent != "neutral":
                base_confidence += 0.2
            
            # 2. 가치 기반 조정
            values = analysis.get("values", [])
            base_confidence += len(values) * 0.1
            
            # 3. 제약 조건 기반 조정
            constraints = analysis.get("constraints", [])
            base_confidence -= len(constraints) * 0.1
            
            return min(max(base_confidence, 0.0), 1.0)
            
        except Exception as e:
            print(f"⚠️ 신뢰도 계산 중 오류: {str(e)}")
            return 0.5

    def _get_relevant_decisions(self, memory_atom: Dict) -> List[Dict]:
        """관련된 이전 결정들을 가져옵니다."""
        try:
            relevant_decisions = []
            
            # 1. 최근 결정들 검색
            recent_decisions = self.decision_history[-5:]  # 최근 5개 결정
            
            # 2. 관련성 평가
            for decision in recent_decisions:
                if self._is_relevant(decision, memory_atom):
                    relevant_decisions.append(decision)
            
            return relevant_decisions
            
        except Exception as e:
            print(f"⚠️ 관련 결정 검색 중 오류: {str(e)}")
            return []

    def _is_relevant(self, decision: Dict, memory_atom: Dict) -> bool:
        """결정의 관련성 평가"""
        try:
            # 1. 시간 기반 평가
            decision_time = datetime.fromisoformat(decision.get("timestamp", "2000-01-01T00:00:00"))
            memory_time = datetime.fromisoformat(memory_atom.get("timestamp", "2000-01-01T00:00:00"))
            time_diff = (memory_time - decision_time).total_seconds()
            
            # 24시간 이내의 결정만 고려
            if time_diff > 86400:  # 24시간 = 86400초
                return False
            
            # 2. 맥락 기반 평가
            decision_values = set(decision.get("analysis", {}).get("values", []))
            memory_values = set(memory_atom.get("values", []))
            
            # 공통 가치가 있으면 관련 있다고 판단
            return bool(decision_values & memory_values)
            
        except Exception as e:
            print(f"⚠️ 관련성 평가 중 오류: {str(e)}")
            return False

    def _extract_constraints(self, memory_atom: Dict) -> List[str]:
        """메모리 원자에서 제약 조건 추출"""
        try:
            constraints = []
            
            # 1. 감정 기반 제약
            emotional_signature = memory_atom.get("emotional_signature", {})
            if emotional_signature.get("valence", 0.0) < 0.3:
                constraints.append("emotional_constraint")
            
            # 2. 맥락 기반 제약
            context = memory_atom.get("context", {})
            if context.get("urgency", False):
                constraints.append("time_constraint")
            if context.get("complexity", 0.0) > 0.7:
                constraints.append("complexity_constraint")
            
            return constraints
            
        except Exception as e:
            print(f"⚠️ 제약 조건 추출 중 오류: {str(e)}")
            return []

    def get_state(self) -> Dict:
        """현재 상태를 반환합니다."""
        return self.state.copy()
