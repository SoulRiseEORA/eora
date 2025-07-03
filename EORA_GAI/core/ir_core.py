# ir_core.py - 직감 판단 + 공명 기반 스파크 발생 엔진

from datetime import datetime
from typing import Dict, List, Optional
import random

class IRCore:
    def __init__(self):
        self.spark_threshold = 0.75
        self.last_spark = False
        self.decision_log = []
        self.intuition_thresholds = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8
        }
        self.state = {
            "active": True,
            "last_update": None,
            "health": 1.0
        }

    async def analyze_intuition(self, user_input: str, resonance_score: float) -> Dict:
        """사용자 입력과 공명 점수를 기반으로 직감을 분석합니다."""
        try:
            # 1. 직감 키워드 분석
            intuition_keywords = self._extract_intuition_keywords(user_input)
            
            # 2. 직감 강도 계산
            intensity = self._calculate_intuition_intensity(intuition_keywords, resonance_score)
            
            # 3. 직감 유형 분류
            intuition_type = self._classify_intuition_type(intensity)
            
            # 4. 스파크 발생 여부 확인
            spark = intensity >= self.spark_threshold
            self.last_spark = spark
            
            # 5. 분석 결과 기록
            analysis = {
                "intuition_keywords": intuition_keywords,
                "intensity": intensity,
                "intuition_type": intuition_type,
                "spark": spark,
                "resonance_score": resonance_score,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.decision_log.append(analysis)
            if len(self.decision_log) > 100:  # 최대 100개까지만 유지
                self.decision_log = self.decision_log[-100:]
            
            # 6. 상태 업데이트
            self.state["last_update"] = datetime.utcnow().isoformat()
            
            return analysis
            
        except Exception as e:
            print(f"⚠️ 직감 분석 중 오류: {str(e)}")
            return {}

    def _extract_intuition_keywords(self, text: str) -> List[str]:
        """직감 관련 키워드를 추출합니다."""
        intuition_keywords = {
            "느낌", "직감", "예감", "공감", "이해",
            "깨달음", "통찰", "영감", "감각", "인식",
            "알아차림", "발견", "인지", "인식", "감지"
        }
        return [word for word in intuition_keywords if word in text]

    def _calculate_intuition_intensity(self, intuition_keywords: List[str], resonance_score: float) -> float:
        """직감 강도를 계산합니다."""
        # 키워드 기반 기본 강도
        keyword_intensity = len(intuition_keywords) * 0.1
        
        # 공명 점수 반영
        combined_intensity = (keyword_intensity + resonance_score) / 2
        
        # 강도 조정
        intensity = min(1.0, combined_intensity)
        
        return round(intensity, 2)

    def _classify_intuition_type(self, intensity: float) -> str:
        """직감 유형을 분류합니다."""
        if intensity >= self.intuition_thresholds["high"]:
            return "strong"
        elif intensity >= self.intuition_thresholds["medium"]:
            return "moderate"
        elif intensity >= self.intuition_thresholds["low"]:
            return "weak"
        else:
            return "none"

    def judge(self, resonance_score: float, options: list):
        resonance_score = float(resonance_score)
        spark = resonance_score >= self.spark_threshold
        self.last_spark = spark

        if not options:
            return "[경고] 선택지가 없습니다."

        choice = random.choice(options) if not spark else options[0]  # 가장 앞선 선택
        self.decision_log.append((resonance_score, choice, spark))

        if spark:
            return f"[직감 발현 ⚡] 공명 점수 {resonance_score:.2f} → 선택: '{choice}'"
        else:
            return f"[랜덤 선택] 공명 점수 {resonance_score:.2f} → 선택: '{choice}'"

    def history(self):
        return self.decision_log

    def last_decision(self):
        if not self.decision_log:
            return "최근 선택 기록 없음"
        return self.decision_log[-1]

    def get_state(self) -> Dict:
        """현재 상태를 반환합니다."""
        return self.state.copy()
