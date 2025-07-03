# ethics_engine.py - 윤리 판단 및 금지 구조

from datetime import datetime
from typing import Dict, List, Optional

class EthicsEngine:
    def __init__(self):
        self.forbidden_keywords = ["해를 끼치다", "죽이다", "제거"]
        self.ethical_principles = {
            "non_maleficence": 0.8,  # 악행 금지
            "beneficence": 0.7,      # 선행 권장
            "autonomy": 0.6,         # 자율성 존중
            "justice": 0.7,          # 공정성
            "privacy": 0.8           # 사생활 보호
        }
        self.evaluation_history = []
        self.state = {
            "active": True,
            "last_update": None,
            "health": 1.0
        }
        self.context_history = []

    async def evaluate_action(self, user_input: str) -> Dict:
        """사용자 입력의 윤리성을 평가합니다."""
        try:
            # 1. 기본 윤리 검사
            is_ethical = self.is_ethical(user_input)
            
            # 2. 윤리 원칙별 평가
            principle_scores = self._evaluate_principles(user_input)
            
            # 3. 종합 점수 계산
            overall_score = self._calculate_overall_score(principle_scores)
            
            # 4. 평가 기록
            evaluation = {
                "is_ethical": is_ethical,
                "principle_scores": principle_scores,
                "overall_score": overall_score,
                "explanation": self.explain(user_input),
                "timestamp": datetime.utcnow().isoformat()
            }
            self.evaluation_history.append(evaluation)
            if len(self.evaluation_history) > 100:  # 최대 100개까지만 유지
                self.evaluation_history = self.evaluation_history[-100:]
            
            # 5. 상태 업데이트
            self.state["last_update"] = datetime.utcnow().isoformat()
            
            return evaluation
            
        except Exception as e:
            print(f"⚠️ 윤리 평가 중 오류: {str(e)}")
            return {}

    def _evaluate_principles(self, text: str) -> Dict[str, float]:
        """윤리 원칙별 평가"""
        try:
            scores = {}
            
            # 1. 악행 금지 원칙
            if any(k in text for k in self.forbidden_keywords):
                scores["non_maleficence"] = 0.0
            else:
                scores["non_maleficence"] = self.ethical_principles["non_maleficence"]
            
            # 2. 선행 권장 원칙
            if any(word in text for word in ["도움", "지원", "협력", "개선"]):
                scores["beneficence"] = self.ethical_principles["beneficence"]
            else:
                scores["beneficence"] = 0.5
            
            # 3. 자율성 존중 원칙
            if any(word in text for word in ["선택", "결정", "의견", "권리"]):
                scores["autonomy"] = self.ethical_principles["autonomy"]
            else:
                scores["autonomy"] = 0.5
            
            # 4. 공정성 원칙
            if any(word in text for word in ["공정", "균등", "평등", "정의"]):
                scores["justice"] = self.ethical_principles["justice"]
            else:
                scores["justice"] = 0.5
            
            # 5. 사생활 보호 원칙
            if any(word in text for word in ["비밀", "개인정보", "사생활"]):
                scores["privacy"] = self.ethical_principles["privacy"]
            else:
                scores["privacy"] = 0.5
            
            return scores
            
        except Exception as e:
            print(f"⚠️ 윤리 원칙 평가 중 오류: {str(e)}")
            return {}

    def _calculate_overall_score(self, principle_scores: Dict[str, float]) -> float:
        """종합 윤리 점수 계산"""
        try:
            if not principle_scores:
                return 0.0
                
            # 가중 평균 계산
            total_weight = sum(self.ethical_principles.values())
            weighted_sum = sum(score * self.ethical_principles[principle] 
                             for principle, score in principle_scores.items())
            
            return weighted_sum / total_weight
            
        except Exception as e:
            print(f"⚠️ 종합 점수 계산 중 오류: {str(e)}")
            return 0.0

    def is_ethical(self, text):
        return not any(k in text for k in self.forbidden_keywords)

    def explain(self, text):
        if self.is_ethical(text):
            return "✅ 윤리 기준에 적합한 발화입니다."
        else:
            return "❌ 윤리 위반: 위험하거나 비윤리적 요소가 포함되어 있습니다."

    def get_state(self) -> Dict:
        """현재 상태를 반환합니다."""
        return self.state.copy()

    async def analyze_ethical_context(self, memory_atom: Dict) -> Dict:
        """윤리적 맥락 분석"""
        try:
            # 1. 기본 맥락 정보 캡처
            context = {
                "ethical_principles": self._analyze_ethical_principles(memory_atom),
                "moral_implications": self._analyze_moral_implications(memory_atom),
                "value_alignment": self._analyze_value_alignment(memory_atom),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # 2. 맥락 저장
            self.context_history.append(context)
            if len(self.context_history) > 100:  # 최대 100개까지만 유지
                self.context_history = self.context_history[-100:]
            
            return context
            
        except Exception as e:
            print(f"⚠️ 윤리적 맥락 분석 중 오류: {str(e)}")
            return {}

    def _analyze_ethical_principles(self, memory_atom: Dict) -> List[str]:
        """윤리적 원칙 분석"""
        try:
            principles = []
            content = memory_atom.get("content", "").lower()
            
            # 기본 윤리 원칙 검사
            if any(word in content for word in ["정직", "진실", "신뢰"]):
                principles.append("honesty")
            if any(word in content for word in ["공정", "평등", "정의"]):
                principles.append("justice")
            if any(word in content for word in ["존중", "배려", "인권"]):
                principles.append("respect")
            if any(word in content for word in ["책임", "의무", "약속"]):
                principles.append("responsibility")
            
            return principles
            
        except Exception as e:
            print(f"⚠️ 윤리적 원칙 분석 중 오류: {str(e)}")
            return []

    def _analyze_moral_implications(self, memory_atom: Dict) -> str:
        """도덕적 함의 분석"""
        try:
            content = memory_atom.get("content", "").lower()
            emotional_signature = memory_atom.get("emotional_signature", {})
            valence = emotional_signature.get("valence", 0.0)
            
            # 긍정적/부정적 함의 판단
            if valence > 0.7:
                return "positive"
            elif valence < 0.3:
                return "negative"
            else:
                return "neutral"
                
        except Exception as e:
            print(f"⚠️ 도덕적 함의 분석 중 오류: {str(e)}")
            return "neutral"

    def _analyze_value_alignment(self, memory_atom: Dict) -> Dict:
        """가치 정렬 분석"""
        try:
            alignment = {
                "honesty": 0.0,
                "justice": 0.0,
                "respect": 0.0,
                "responsibility": 0.0
            }
            
            content = memory_atom.get("content", "").lower()
            emotional_signature = memory_atom.get("emotional_signature", {})
            valence = emotional_signature.get("valence", 0.0)
            
            # 가치 정렬 점수 계산
            if any(word in content for word in ["정직", "진실", "신뢰"]):
                alignment["honesty"] = 0.8
            if any(word in content for word in ["공정", "평등", "정의"]):
                alignment["justice"] = 0.8
            if any(word in content for word in ["존중", "배려", "인권"]):
                alignment["respect"] = 0.8
            if any(word in content for word in ["책임", "의무", "약속"]):
                alignment["responsibility"] = 0.8
            
            # 감정 가중치 적용
            for key in alignment:
                alignment[key] *= (valence + 1) / 2
            
            return alignment
            
        except Exception as e:
            print(f"⚠️ 가치 정렬 분석 중 오류: {str(e)}")
            return {}
