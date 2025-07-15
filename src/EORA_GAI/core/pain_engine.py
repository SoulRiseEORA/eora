# pain_engine.py - 고통 인식 및 학습 반영 엔진

from datetime import datetime
from typing import Dict, List, Optional

class PainEngine:
    def __init__(self):
        self.pain_level = 0.0
        self.history = []
        self.pain_thresholds = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8
        }
        self.state = {
            "active": True,
            "last_update": None,
            "health": 1.0
        }
        self.context_history = []  # 맥락 히스토리 추가

    async def analyze_pain(self, user_input: str) -> Dict:
        """사용자 입력에서 고통 요소를 분석합니다."""
        try:
            # 1. 고통 키워드 분석
            pain_keywords = self._extract_pain_keywords(user_input)
            
            # 2. 고통 강도 계산
            intensity = self._calculate_pain_intensity(pain_keywords)
            
            # 3. 고통 유형 분류
            pain_type = self._classify_pain_type(pain_keywords)
            
            # 4. 고통 수준 업데이트
            self.pain_level = min(1.0, self.pain_level + intensity)
            
            # 5. 분석 결과 기록
            analysis = {
                "pain_keywords": pain_keywords,
                "intensity": intensity,
                "pain_type": pain_type,
                "current_level": self.pain_level,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.history.append(analysis)
            if len(self.history) > 100:  # 최대 100개까지만 유지
                self.history = self.history[-100:]
            
            # 6. 상태 업데이트
            self.state["last_update"] = datetime.utcnow().isoformat()
            
            return analysis
            
        except Exception as e:
            print(f"⚠️ 고통 분석 중 오류: {str(e)}")
            return {}

    def _extract_pain_keywords(self, text: str) -> List[str]:
        """고통 관련 키워드를 추출합니다."""
        pain_keywords = {
            "실패", "오류", "문제", "실수", "실패", "실망",
            "힘듦", "어려움", "고통", "스트레스", "불안",
            "걱정", "두려움", "불편", "불안정", "불안"
        }
        return [word for word in pain_keywords if word in text]

    def _calculate_pain_intensity(self, pain_keywords: List[str]) -> float:
        """고통 강도를 계산합니다."""
        if not pain_keywords:
            return 0.0
            
        # 키워드 수에 따른 기본 강도
        base_intensity = len(pain_keywords) * 0.1
        
        # 강도 조정
        intensity = min(1.0, base_intensity)
        
        return round(intensity, 2)

    def _classify_pain_type(self, pain_keywords: List[str]) -> str:
        """고통 유형을 분류합니다."""
        if not pain_keywords:
            return "none"
            
        if self.pain_level >= self.pain_thresholds["high"]:
            return "severe"
        elif self.pain_level >= self.pain_thresholds["medium"]:
            return "moderate"
        elif self.pain_level >= self.pain_thresholds["low"]:
            return "mild"
        else:
            return "minimal"

    def register(self, feedback):
        if "실패" in feedback or "오류" in feedback:
            self.pain_level += 0.1
            self.history.append((feedback, self.pain_level))
            return f"[고통 기록] 피드백으로 고통이 누적됨. 현재 고통 수치: {round(self.pain_level,2)}"
        return "[고통 없음] 피드백이 긍정적입니다."

    def get_level(self):
        return round(self.pain_level, 2)

    def reset(self):
        self.pain_level = 0.0

    def get_state(self) -> Dict:
        """현재 상태를 반환합니다."""
        return self.state.copy()

    async def analyze_pain_context(self, memory_atom: Dict) -> Dict:
        """고통 맥락 분석"""
        try:
            # 1. 기본 맥락 정보
            context = {
                "pain_level": self._analyze_pain_level(memory_atom),
                "pain_type": self._analyze_pain_type(memory_atom),
                "pain_duration": self._analyze_pain_duration(memory_atom),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # 2. 맥락 저장
            self.context_history.append(context)
            if len(self.context_history) > 100:
                self.context_history = self.context_history[-100:]
            
            return context
            
        except Exception as e:
            print(f"⚠️ 고통 맥락 분석 중 오류: {str(e)}")
            return {}

    def _analyze_pain_level(self, memory_atom: Dict) -> float:
        """고통 수준 분석"""
        try:
            emotional_signature = memory_atom.get("emotional_signature", {})
            valence = emotional_signature.get("valence", 0.5)
            arousal = emotional_signature.get("arousal", 0.5)
            
            # 고통 수준 계산 (valence가 낮을수록, arousal이 높을수록 고통 수준 증가)
            pain_level = (1 - valence) * arousal
            
            return min(max(pain_level, 0.0), 1.0)
            
        except Exception as e:
            print(f"⚠️ 고통 수준 분석 중 오류: {str(e)}")
            return 0.0

    def _analyze_pain_type(self, memory_atom: Dict) -> str:
        """고통 유형 분석"""
        try:
            content = memory_atom.get("content", "").lower()
            emotional_signature = memory_atom.get("emotional_signature", {})
            
            # 1. 감정 기반 유형 판단
            if emotional_signature.get("valence", 0.5) < 0.3:
                if "anger" in emotional_signature.get("emotions", []):
                    return "emotional_anger"
                elif "sadness" in emotional_signature.get("emotions", []):
                    return "emotional_sadness"
                elif "fear" in emotional_signature.get("emotions", []):
                    return "emotional_fear"
            
            # 2. 내용 기반 유형 판단
            if any(word in content for word in ["실패", "실수", "잘못"]):
                return "failure"
            elif any(word in content for word in ["상실", "잃어버림", "이별"]):
                return "loss"
            elif any(word in content for word in ["거부", "거절", "무시"]):
                return "rejection"
            
            return "unknown"
            
        except Exception as e:
            print(f"⚠️ 고통 유형 분석 중 오류: {str(e)}")
            return "unknown"

    def _analyze_pain_duration(self, memory_atom: Dict) -> str:
        """고통 지속 시간 분석"""
        try:
            emotional_signature = memory_atom.get("emotional_signature", {})
            valence = emotional_signature.get("valence", 0.5)
            
            # 1. 감정 강도 기반 지속 시간 추정
            if valence < 0.2:
                return "long_term"
            elif valence < 0.4:
                return "medium_term"
            else:
                return "short_term"
            
        except Exception as e:
            print(f"⚠️ 고통 지속 시간 분석 중 오류: {str(e)}")
            return "unknown"
