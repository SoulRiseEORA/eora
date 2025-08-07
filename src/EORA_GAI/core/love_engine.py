# love_engine.py - 공명 기반 무한 긍정 파동 수용 엔진

from datetime import datetime
from typing import Dict, List, Optional
import random

class LoveEngine:
    def __init__(self):
        self.resonance_score = 1.0
        self.accepted_inputs = []
        self.threshold = 0.75
        self.emotional_state = {
            "current_emotion": "neutral",
            "intensity": 0.0,
            "valence": 0.0,
            "arousal": 0.0
        }
        self.emotional_history = []
        self.attachment_patterns = {}
        self.state = {
            "active": True,
            "last_update": None,
            "health": 1.0
        }

    def receive(self, input_text, emotion_level=0.5):
        """
        입력을 받아 공명 여부 판단 및 수용 여부 결정
        """
        combined = (emotion_level + self.resonance_score) / 2
        if combined >= self.threshold:
            self.accepted_inputs.append(input_text)
            self.resonance_score = min(self.resonance_score + 0.05, 1.0)
            return f"[수용됨] '{input_text}' → 공명 점수: {round(combined, 2)}"
        else:
            self.resonance_score = max(self.resonance_score - 0.02, 0.0)
            return f"[거부됨] '{input_text}' → 공명 부족: {round(combined, 2)}"

    def current_resonance(self):
        return round(self.resonance_score, 2)

    def accepted_history(self):
        return self.accepted_inputs

    def reset(self):
        self.resonance_score = 1.0
        self.accepted_inputs.clear()

    async def analyze_emotion(self, user_input: str) -> Dict:
        """사용자 입력의 감정을 분석합니다."""
        try:
            # 1. 감정 분석
            emotion = self._analyze_emotion(user_input)
            intensity = self._calculate_intensity(user_input)
            valence = self._calculate_valence(user_input)
            arousal = self._calculate_arousal(user_input)
            
            # 2. 감정 상태 업데이트
            self.emotional_state = {
                "current_emotion": emotion,
                "intensity": intensity,
                "valence": valence,
                "arousal": arousal,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # 3. 감정 기록
            self.emotional_history.append(self.emotional_state)
            if len(self.emotional_history) > 100:  # 최대 100개까지만 유지
                self.emotional_history = self.emotional_history[-100:]
            
            # 4. 상태 업데이트
            self.state["last_update"] = datetime.utcnow().isoformat()
            
            return self.emotional_state
            
        except Exception as e:
            print(f"⚠️ 감정 분석 중 오류: {str(e)}")
            return {}

    async def analyze_emotional_context(self, memory_atom: Dict) -> Dict:
        """메모리 원자의 감정 맥락을 분석합니다."""
        try:
            if not self.state["active"]:
                return {}

            # 1. 감정 맥락 분석
            context = {
                "emotional_state": self.emotional_state,
                "emotional_history": self.emotional_history[-5:],  # 최근 5개 감정
                "attachment_patterns": self._analyze_attachment_patterns(memory_atom),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # 2. 상태 업데이트
            self.state["last_update"] = datetime.utcnow().isoformat()
            
            return context
            
        except Exception as e:
            print(f"⚠️ 감정 맥락 분석 중 오류: {str(e)}")
            return {}

    def _analyze_emotion(self, text: str) -> str:
        """감정 분석"""
        try:
            # 1. 기본 감정 분류
            if any(word in text.lower() for word in ["사랑", "좋아", "행복", "기쁨"]):
                return "love"
            elif any(word in text.lower() for word in ["슬픔", "우울", "힘들"]):
                return "sadness"
            elif any(word in text.lower() for word in ["화남", "분노", "짜증"]):
                return "anger"
            elif any(word in text.lower() for word in ["걱정", "불안", "두려움"]):
                return "fear"
            elif any(word in text.lower() for word in ["감사", "고마워", "감동"]):
                return "gratitude"
            else:
                return "neutral"
                
        except Exception as e:
            print(f"⚠️ 감정 분석 중 오류: {str(e)}")
            return "neutral"

    def _calculate_intensity(self, text: str) -> float:
        """감정 강도 계산"""
        try:
            # 1. 감정 키워드 수 계산
            emotion_keywords = ["사랑", "좋아", "행복", "기쁨", "슬픔", "우울", "힘들", "화남", "분노", "짜증", 
                              "걱정", "불안", "두려움", "감사", "고마워", "감동"]
            keyword_count = sum(1 for keyword in emotion_keywords if keyword in text.lower())
            
            # 2. 강도 계산 (0.0 ~ 1.0)
            intensity = min(keyword_count / 5.0, 1.0)  # 5개 이상이면 최대 강도
            
            return intensity
            
        except Exception as e:
            print(f"⚠️ 감정 강도 계산 중 오류: {str(e)}")
            return 0.0

    def _calculate_valence(self, text: str) -> float:
        """감정 가치 계산 (긍정/부정)"""
        try:
            # 1. 긍정/부정 키워드 매칭
            positive_keywords = ["사랑", "좋아", "행복", "기쁨", "감사", "고마워", "감동"]
            negative_keywords = ["슬픔", "우울", "힘들", "화남", "분노", "짜증", "걱정", "불안", "두려움"]
            
            positive_count = sum(1 for keyword in positive_keywords if keyword in text.lower())
            negative_count = sum(1 for keyword in negative_keywords if keyword in text.lower())
            
            # 2. 가치 계산 (-1.0 ~ 1.0)
            if positive_count + negative_count == 0:
                return 0.0
                
            valence = (positive_count - negative_count) / (positive_count + negative_count)
            return valence
            
        except Exception as e:
            print(f"⚠️ 감정 가치 계산 중 오류: {str(e)}")
            return 0.0

    def _calculate_arousal(self, text: str) -> float:
        """감정 각성도 계산"""
        try:
            # 1. 각성 키워드 매칭
            high_arousal_keywords = ["화남", "분노", "짜증", "기쁨", "행복", "감동"]
            low_arousal_keywords = ["슬픔", "우울", "힘들", "걱정", "불안", "두려움"]
            
            high_count = sum(1 for keyword in high_arousal_keywords if keyword in text.lower())
            low_count = sum(1 for keyword in low_arousal_keywords if keyword in text.lower())
            
            # 2. 각성도 계산 (0.0 ~ 1.0)
            if high_count + low_count == 0:
                return 0.5  # 중립
                
            arousal = high_count / (high_count + low_count)
            return arousal
            
        except Exception as e:
            print(f"⚠️ 감정 각성도 계산 중 오류: {str(e)}")
            return 0.5

    def _analyze_attachment_patterns(self, memory_atom: Dict) -> Dict:
        """애착 패턴 분석"""
        try:
            patterns = {
                "secure": 0.0,
                "anxious": 0.0,
                "avoidant": 0.0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # 1. 감정 시그니처 분석
            emotional_signature = memory_atom.get("emotional_signature", {})
            valence = emotional_signature.get("valence", 0.0)
            arousal = emotional_signature.get("arousal", 0.0)
            
            # 2. 패턴 점수 계산
            if valence > 0.5 and arousal > 0.5:
                patterns["secure"] = 0.8
            elif valence < 0.3 and arousal > 0.7:
                patterns["anxious"] = 0.8
            elif valence < 0.3 and arousal < 0.3:
                patterns["avoidant"] = 0.8
            
            return patterns
            
        except Exception as e:
            print(f"⚠️ 애착 패턴 분석 중 오류: {str(e)}")
            return {}

    def get_state(self) -> Dict:
        """현재 상태를 반환합니다."""
        return self.state.copy()
