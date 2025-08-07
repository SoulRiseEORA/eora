# stress_monitor.py - 스트레스 감지 및 임계값 경보

from datetime import datetime
from typing import Dict, List, Optional

class StressMonitor:
    def __init__(self):
        self.stress_level = 0.0
        self.history = []
        self.stress_thresholds = {
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

    async def analyze_stress(self, user_input: str) -> Dict:
        """사용자 입력에서 스트레스 요소를 분석합니다."""
        try:
            # 1. 스트레스 키워드 분석
            stress_keywords = self._extract_stress_keywords(user_input)
            
            # 2. 스트레스 강도 계산
            intensity = self._calculate_stress_intensity(stress_keywords)
            
            # 3. 스트레스 유형 분류
            stress_type = self._classify_stress_type(stress_keywords)
            
            # 4. 스트레스 수준 업데이트
            self.stress_level = min(1.0, self.stress_level + intensity)
            
            # 5. 분석 결과 기록
            analysis = {
                "stress_keywords": stress_keywords,
                "intensity": intensity,
                "stress_type": stress_type,
                "current_level": self.stress_level,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.history.append(analysis)
            if len(self.history) > 100:  # 최대 100개까지만 유지
                self.history = self.history[-100:]
            
            # 6. 상태 업데이트
            self.state["last_update"] = datetime.utcnow().isoformat()
            
            return analysis
            
        except Exception as e:
            print(f"⚠️ 스트레스 분석 중 오류: {str(e)}")
            return {}

    def _extract_stress_keywords(self, text: str) -> List[str]:
        """스트레스 관련 키워드를 추출합니다."""
        stress_keywords = {
            "압박", "지연", "실패", "부담", "걱정",
            "불안", "긴장", "피로", "스트레스", "불편",
            "어려움", "문제", "위기", "위험", "불안정"
        }
        return [word for word in stress_keywords if word in text]

    def _calculate_stress_intensity(self, stress_keywords: List[str]) -> float:
        """스트레스 강도를 계산합니다."""
        if not stress_keywords:
            return 0.0
            
        # 키워드 수에 따른 기본 강도
        base_intensity = len(stress_keywords) * 0.1
        
        # 강도 조정
        intensity = min(1.0, base_intensity)
        
        return round(intensity, 2)

    def _classify_stress_type(self, stress_keywords: List[str]) -> str:
        """스트레스 유형을 분류합니다."""
        if not stress_keywords:
            return "none"
            
        if self.stress_level >= self.stress_thresholds["high"]:
            return "severe"
        elif self.stress_level >= self.stress_thresholds["medium"]:
            return "moderate"
        elif self.stress_level >= self.stress_thresholds["low"]:
            return "mild"
        else:
            return "minimal"

    def trigger(self, event):
        if "압박" in event or "지연" in event or "실패" in event:
            self.stress_level += 0.1
        elif "성공" in event or "편안" in event:
            self.stress_level = max(0.0, self.stress_level - 0.05)
        self.history.append((event, self.stress_level))
        return self.alert()

    def alert(self):
        if self.stress_level > 0.7:
            return f"⚠️ 스트레스 과다 ({round(self.stress_level,2)}). 자율 조정 필요."
        return f"스트레스 정상 범위 ({round(self.stress_level,2)})"

    def status(self):
        return self.stress_level

    def history(self):
        return self.history[-5:]

    def get_state(self) -> Dict:
        """현재 상태를 반환합니다."""
        return self.state.copy()
