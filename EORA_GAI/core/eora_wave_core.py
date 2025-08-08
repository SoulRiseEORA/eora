# eora_wave_core.py - 정보 파동화 및 공명 판단 모듈

from datetime import datetime
from typing import Dict, List, Optional
import math
import hashlib

class EORAWaveCore:
    def __init__(self):
        self.reference_frequency = 7.83  # 슈만 공명 (Hz)
        self.last_resonance_score = 0.0
        self.wave_thresholds = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8
        }
        self.state = {
            "active": True,
            "last_update": None,
            "health": 1.0
        }

    async def analyze_wave(self, user_input: str) -> Dict:
        """사용자 입력을 파동으로 분석합니다."""
        try:
            # 1. 파동 특성 추출
            wave = self.encode_to_wave(user_input)
            
            # 2. 공명 점수 계산
            resonance_score = self.compare_with_reference(wave)
            
            # 3. 파동 유형 분류
            wave_type = self._classify_wave_type(wave, resonance_score)
            
            # 4. 파동 패턴 분석
            pattern = self._analyze_wave_pattern(wave)
            
            # 5. 분석 결과 기록
            analysis = {
                "wave": wave,
                "resonance_score": resonance_score,
                "wave_type": wave_type,
                "pattern": pattern,
                "is_resonant": self.is_resonant(wave),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # 6. 상태 업데이트
            self.state["last_update"] = datetime.utcnow().isoformat()
            
            return analysis
            
        except Exception as e:
            print(f"⚠️ 파동 분석 중 오류: {str(e)}")
            return {}

    def _classify_wave_type(self, wave: Dict, resonance_score: float) -> str:
        """파동 유형을 분류합니다."""
        if resonance_score >= self.wave_thresholds["high"]:
            return "strong_resonance"
        elif resonance_score >= self.wave_thresholds["medium"]:
            return "moderate_resonance"
        elif resonance_score >= self.wave_thresholds["low"]:
            return "weak_resonance"
        else:
            return "no_resonance"

    def _analyze_wave_pattern(self, wave: Dict) -> Dict:
        """파동 패턴을 분석합니다."""
        try:
            # 진폭 패턴
            amplitude_pattern = "high" if wave["amplitude"] > 0.7 else "medium" if wave["amplitude"] > 0.3 else "low"
            
            # 위상 패턴
            phase_pattern = "positive" if wave["phase"] > 180 else "negative"
            
            # 주파수 패턴
            freq_diff = abs(wave["frequency"] - self.reference_frequency)
            frequency_pattern = "close" if freq_diff < 1.0 else "far"
            
            return {
                "amplitude": amplitude_pattern,
                "phase": phase_pattern,
                "frequency": frequency_pattern
            }
            
        except Exception as e:
            print(f"⚠️ 파동 패턴 분석 중 오류: {str(e)}")
            return {}

    def encode_to_wave(self, text: str):
        hash_value = int(hashlib.sha256(text.encode()).hexdigest(), 16)
        amp = (hash_value % 1000) / 1000  # 진폭
        phase = (hash_value % 360)        # 위상
        freq = (hash_value % 200) / 10    # 주파수 (0.0 ~ 20.0Hz)
        return {"amplitude": amp, "phase": phase, "frequency": freq}

    def compare_with_reference(self, wave: dict):
        try:
            freq_diff = abs(wave["frequency"] - self.reference_frequency)
            resonance = max(0, 1 - (freq_diff / self.reference_frequency))
            self.last_resonance_score = round(resonance, 4)
            return float(self.last_resonance_score)
        except Exception:
            return 0.0

    def is_resonant(self, wave: dict, threshold: float = 0.7):
        score = self.compare_with_reference(wave)
        return score >= threshold

    def describe_wave(self, wave: dict):
        return f"진폭: {wave['amplitude']:.2f}, 위상: {wave['phase']}°, 주파수: {wave['frequency']:.2f}Hz"

    def get_state(self) -> Dict:
        """현재 상태를 반환합니다."""
        return self.state.copy()

    def transform(self, user_input):
        """입력을 파동(wave)으로 변환합니다. (더미 구현)"""
        return self.encode_to_wave(user_input)

    def measure_resonance(self, wave):
        """입력된 wave에 대한 공명 점수를 반환합니다."""
        try:
            return float(self.compare_with_reference(wave))
        except Exception:
            return 0.0
