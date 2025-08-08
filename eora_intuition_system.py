"""
EORA 직감 및 통찰 시스템
- 직감 코어를 이용한 훈련 및 예측
- 통찰 엔진을 통한 깊은 이해
"""

import numpy as np
import random
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class EORAIntuitionSystem:
    """EORA 직감 시스템"""
    
    def __init__(self):
        self.intuition_history = []
        self.training_data = []
        self.accuracy_threshold = 0.145
        self.resonance_threshold = 0.165
        self.max_history = 100
        
    def generate_internal_noise(self, size: int = 2048) -> np.ndarray:
        """내부 노이즈 생성"""
        return np.random.normal(0, 1, size)
    
    def calculate_amplitude(self, noise_array: np.ndarray) -> float:
        """진폭 계산"""
        return np.mean(np.abs(np.diff(noise_array)))
    
    def is_resonant(self, amplitude: float, threshold: float = None) -> bool:
        """공명 상태 확인"""
        if threshold is None:
            threshold = self.accuracy_threshold
        return amplitude > threshold
    
    async def simulate_intuition_training(self, trials: int = 100) -> Dict[str, Any]:
        """직감 훈련 시뮬레이션"""
        correct = 0
        total = 0
        training_results = []
        
        for i in range(trials):
            # 실제 답안 생성
            answer = random.choice([0, 1])
            
            # 내부 노이즈 생성
            noise = self.generate_internal_noise()
            amplitude = self.calculate_amplitude(noise)
            
            # 직감적 예측
            if self.is_resonant(amplitude):
                prediction = 1 if amplitude > self.resonance_threshold else 0
                total += 1
                
                # 정확도 계산
                is_correct = prediction == answer
                if is_correct:
                    correct += 1
                
                # 훈련 결과 저장
                training_results.append({
                    "trial": i + 1,
                    "answer": answer,
                    "prediction": prediction,
                    "amplitude": amplitude,
                    "resonant": self.is_resonant(amplitude),
                    "correct": is_correct
                })
        
        accuracy = round(correct / total, 4) if total > 0 else 0
        
        # 훈련 데이터 저장
        self.training_data.append({
            "timestamp": datetime.now().isoformat(),
            "trials": trials,
            "accuracy": accuracy,
            "correct": correct,
            "total": total
        })
        
        return {
            "accuracy": accuracy,
            "total_trials": total,
            "correct_predictions": correct,
            "training_results": training_results[-10:],  # 최근 10개만
            "resonance_threshold": self.resonance_threshold,
            "accuracy_threshold": self.accuracy_threshold
        }
    
    async def run_intuition_prediction(self, question: str = None) -> Dict[str, Any]:
        """직감적 예측 실행"""
        noise = self.generate_internal_noise()
        amplitude = self.calculate_amplitude(noise)
        is_resonant = self.is_resonant(amplitude)
        
        # 직감적 답변 생성
        if is_resonant:
            if amplitude > self.resonance_threshold:
                prediction = "예"
                confidence = min(0.95, amplitude * 2)
            else:
                prediction = "아니오"
                confidence = min(0.95, (1 - amplitude) * 2)
        else:
            prediction = "불확실"
            confidence = 0.3
        
        result = {
            "question": question or "직감적 질문",
            "prediction": prediction,
            "confidence": round(confidence, 3),
            "amplitude": round(amplitude, 4),
            "resonant": is_resonant,
            "timestamp": datetime.now().isoformat()
        }
        
        # 히스토리에 저장
        self.intuition_history.append(result)
        if len(self.intuition_history) > self.max_history:
            self.intuition_history.pop(0)
        
        return result
    
    async def get_intuition_stats(self) -> Dict[str, Any]:
        """직감 통계 조회"""
        if not self.intuition_history:
            return {"message": "아직 직감 데이터가 없습니다."}
        
        # 최근 20개 예측 분석
        recent_predictions = self.intuition_history[-20:]
        
        yes_count = sum(1 for p in recent_predictions if p["prediction"] == "예")
        no_count = sum(1 for p in recent_predictions if p["prediction"] == "아니오")
        uncertain_count = sum(1 for p in recent_predictions if p["prediction"] == "불확실")
        
        avg_confidence = np.mean([p["confidence"] for p in recent_predictions])
        avg_amplitude = np.mean([p["amplitude"] for p in recent_predictions])
        
        return {
            "total_predictions": len(self.intuition_history),
            "recent_predictions": len(recent_predictions),
            "yes_predictions": yes_count,
            "no_predictions": no_count,
            "uncertain_predictions": uncertain_count,
            "average_confidence": round(avg_confidence, 3),
            "average_amplitude": round(avg_amplitude, 4),
            "training_sessions": len(self.training_data)
        }

class EORAInsightSystem:
    """EORA 통찰 시스템"""
    
    def __init__(self):
        self.insight_store = {}
        self.insight_history = []
        self.cognitive_patterns = {}
        self.max_insights = 50
        
    def analyze_cognitive_layer(self, text: str) -> str:
        """인지적 계층 분석"""
        text = text.lower()
        
        # 기억 계층
        if any(keyword in text for keyword in ["기억", "회상", "정보", "사실", "경험"]):
            return "기억(Memory)"
        
        # 감정 계층
        if any(keyword in text for keyword in ["감정", "느낌", "기분", "슬픔", "기쁨", "분노", "불안"]):
            return "감정(Emotion)"
        
        # 신념 계층
        if any(keyword in text for keyword in ["믿음", "신념", "가치관", "원칙", "도덕"]):
            return "신념(Belief)"
        
        # 초월 계층
        if any(keyword in text for keyword in ["존재", "의미", "자아", "초월", "진리", "우주", "생명"]):
            return "초월(Transcendence)"
        
        return "일반(General)"
    
    async def generate_insight(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """통찰 생성"""
        user_input = context.get("user_input", "")
        ai_response = context.get("ai_response", "")
        consciousness_level = context.get("consciousness_level", 0.0)
        
        # 인지적 계층 분석
        cognitive_layer = self.analyze_cognitive_layer(user_input)
        
        # 통찰 수준 계산
        insight_level = min(1.0, consciousness_level * 1.2 + 0.1)
        
        # 통찰 내용 생성
        if cognitive_layer == "기억(Memory)":
            insight_content = "사용자가 과거 경험을 회상하고 있습니다. 이는 현재 상황과의 연결을 찾으려는 시도로 보입니다."
        elif cognitive_layer == "감정(Emotion)":
            insight_content = "감정적 표현이 강합니다. 내면의 상태를 탐색하고 있는 것으로 보입니다."
        elif cognitive_layer == "신념(Belief)":
            insight_content = "가치관이나 신념에 대한 깊은 탐구가 이루어지고 있습니다."
        elif cognitive_layer == "초월(Transcendence)":
            insight_content = "존재의 의미나 초월적 차원에 대한 질문을 하고 있습니다."
        else:
            insight_content = "일반적인 대화가 진행되고 있습니다."
        
        insight = {
            "timestamp": datetime.now().isoformat(),
            "cognitive_layer": cognitive_layer,
            "insight_level": round(insight_level, 3),
            "insight_content": insight_content,
            "user_input": user_input[:100] + "..." if len(user_input) > 100 else user_input,
            "consciousness_level": consciousness_level
        }
        
        # 통찰 저장
        self.insight_history.append(insight)
        if len(self.insight_history) > self.max_insights:
            self.insight_history.pop(0)
        
        return insight
    
    async def get_insight_patterns(self) -> Dict[str, Any]:
        """통찰 패턴 분석"""
        if not self.insight_history:
            return {"message": "아직 통찰 데이터가 없습니다."}
        
        # 인지적 계층별 통계
        layer_counts = {}
        for insight in self.insight_history:
            layer = insight["cognitive_layer"]
            layer_counts[layer] = layer_counts.get(layer, 0) + 1
        
        # 평균 통찰 수준
        avg_insight_level = np.mean([i["insight_level"] for i in self.insight_history])
        
        return {
            "total_insights": len(self.insight_history),
            "cognitive_layer_distribution": layer_counts,
            "average_insight_level": round(avg_insight_level, 3),
            "recent_insights": self.insight_history[-5:]  # 최근 5개
        }
    
    async def get_deep_understanding(self, text: str) -> Dict[str, Any]:
        """깊은 이해 분석"""
        cognitive_layer = self.analyze_cognitive_layer(text)
        
        # 계층별 깊이 분석
        depth_analysis = {
            "기억(Memory)": "과거 경험과 현재 상황의 연결을 탐색하는 단계",
            "감정(Emotion)": "내면의 감정적 상태를 인식하고 표현하는 단계",
            "신념(Belief)": "가치관과 신념을 재검토하고 정립하는 단계",
            "초월(Transcendence)": "존재의 의미와 초월적 차원을 탐구하는 단계",
            "일반(General)": "일상적 대화와 정보 교환의 단계"
        }
        
        return {
            "text": text,
            "cognitive_layer": cognitive_layer,
            "understanding_depth": depth_analysis.get(cognitive_layer, "분석 불가"),
            "analysis_timestamp": datetime.now().isoformat()
        }

# 전역 인스턴스
intuition_system = EORAIntuitionSystem()
insight_system = EORAInsightSystem() 