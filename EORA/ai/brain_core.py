"""
Brain Core Module
AI 두뇌의 핵심 기능을 제공합니다.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import threading
import time

logger = logging.getLogger(__name__)

class BrainCore:
    """AI 두뇌 핵심 클래스"""
    
    def __init__(self):
        self.memory = {}
        self.thought_processes = []
        self.consciousness_level = 0.5
        self.learning_rate = 0.1
        self.creativity_level = 0.7
        self.logic_level = 0.8
        self.emotion_level = 0.6
        
        # 두뇌 상태
        self.is_awake = True
        self.energy_level = 1.0
        self.focus_level = 0.8
        
        # 스레드 안전을 위한 락
        self._lock = threading.Lock()
        
        logger.info("BrainCore 초기화 완료")
    
    def think(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        사고 프로세스를 실행합니다.
        
        Args:
            input_data: 입력 데이터
            context: 컨텍스트 정보
            
        Returns:
            사고 결과
        """
        try:
            with self._lock:
                # 사고 프로세스 시작
                thought_id = self._generate_thought_id()
                thought_process = {
                    "id": thought_id,
                    "input": input_data,
                    "context": context,
                    "start_time": datetime.now().isoformat(),
                    "consciousness_level": self.consciousness_level,
                    "energy_level": self.energy_level,
                    "focus_level": self.focus_level
                }
                
                # 사고 단계별 처리
                analysis = self._analyze_input(input_data, context)
                reasoning = self._reason(analysis, context)
                creativity = self._generate_creative_insights(reasoning, context)
                decision = self._make_decision(analysis, reasoning, creativity, context)
                
                # 결과 구성
                result = {
                    "thought_id": thought_id,
                    "analysis": analysis,
                    "reasoning": reasoning,
                    "creativity": creativity,
                    "decision": decision,
                    "consciousness_level": self.consciousness_level,
                    "energy_consumed": self._calculate_energy_consumption(),
                    "processing_time": time.time()
                }
                
                # 사고 프로세스 저장
                thought_process["result"] = result
                thought_process["end_time"] = datetime.now().isoformat()
                self.thought_processes.append(thought_process)
                
                # 메모리 업데이트
                self._update_memory(input_data, result)
                
                # 두뇌 상태 업데이트
                self._update_brain_state()
                
                logger.info(f"사고 프로세스 완료: {thought_id}")
                return result
                
        except Exception as e:
            logger.error(f"사고 프로세스 중 오류: {e}")
            return {
                "error": str(e),
                "thought_id": thought_id if 'thought_id' in locals() else None
            }
    
    def _analyze_input(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """입력 데이터를 분석합니다."""
        analysis = {
            "content_type": self._determine_content_type(input_data),
            "sentiment": self._analyze_sentiment(input_data),
            "complexity": self._assess_complexity(input_data),
            "urgency": self._assess_urgency(input_data),
            "key_topics": self._extract_key_topics(input_data),
            "user_intent": self._infer_user_intent(input_data)
        }
        return analysis
    
    def _reason(self, analysis: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """논리적 추론을 수행합니다."""
        reasoning = {
            "logical_steps": [],
            "assumptions": [],
            "conclusions": [],
            "confidence_level": 0.0,
            "alternative_paths": []
        }
        
        # 논리적 단계 구성
        if analysis["user_intent"] == "question":
            reasoning["logical_steps"].append("질문 분석")
            reasoning["logical_steps"].append("관련 지식 검색")
            reasoning["logical_steps"].append("답변 구성")
            reasoning["confidence_level"] = 0.8
        elif analysis["user_intent"] == "request":
            reasoning["logical_steps"].append("요청 분석")
            reasoning["logical_steps"].append("실행 가능성 평가")
            reasoning["logical_steps"].append("실행 계획 수립")
            reasoning["confidence_level"] = 0.7
        else:
            reasoning["logical_steps"].append("일반 대화 처리")
            reasoning["confidence_level"] = 0.6
        
        return reasoning
    
    def _generate_creative_insights(self, reasoning: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """창의적 인사이트를 생성합니다."""
        creativity = {
            "insights": [],
            "innovative_ideas": [],
            "creative_connections": [],
            "creativity_score": 0.0
        }
        
        # 창의성 수준에 따른 인사이트 생성
        if self.creativity_level > 0.5:
            creativity["insights"].append("다각적 관점에서 접근")
            creativity["innovative_ideas"].append("새로운 해결 방법 제안")
            creativity["creativity_score"] = self.creativity_level
        
        return creativity
    
    def _make_decision(self, analysis: Dict[str, Any], reasoning: Dict[str, Any], 
                      creativity: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """최종 결정을 내립니다."""
        decision = {
            "action": "respond",
            "response_type": "informative",
            "priority": "normal",
            "emotional_tone": "neutral",
            "confidence": reasoning.get("confidence_level", 0.5)
        }
        
        # 분석 결과에 따른 결정 조정
        if analysis.get("urgency", 0) > 0.7:
            decision["priority"] = "high"
        
        if analysis.get("sentiment") == "positive":
            decision["emotional_tone"] = "positive"
        elif analysis.get("sentiment") == "negative":
            decision["emotional_tone"] = "supportive"
        
        return decision
    
    def _determine_content_type(self, text: str) -> str:
        """콘텐츠 타입을 결정합니다."""
        if "?" in text:
            return "question"
        elif any(word in text.lower() for word in ["도와", "해줘", "요청"]):
            return "request"
        elif any(word in text.lower() for word in ["감사", "좋아", "싫어"]):
            return "feedback"
        else:
            return "conversation"
    
    def _analyze_sentiment(self, text: str) -> str:
        """감정 분석을 수행합니다."""
        positive_words = ["좋", "감사", "행복", "즐거", "훌륭"]
        negative_words = ["나쁘", "싫", "화나", "슬프", "실망"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _assess_complexity(self, text: str) -> float:
        """텍스트 복잡도를 평가합니다."""
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        return min(avg_word_length / 10, 1.0)
    
    def _assess_urgency(self, text: str) -> float:
        """긴급도를 평가합니다."""
        urgent_words = ["급", "바로", "즉시", "당장", "긴급"]
        text_lower = text.lower()
        urgent_count = sum(1 for word in urgent_words if word in text_lower)
        return min(urgent_count / 3, 1.0)
    
    def _extract_key_topics(self, text: str) -> List[str]:
        """주요 토픽을 추출합니다."""
        # 간단한 키워드 추출
        stop_words = ["이", "가", "을", "를", "의", "에", "로", "와", "과", "도", "만", "은", "는"]
        words = text.split()
        topics = [word for word in words if word not in stop_words and len(word) > 1]
        return topics[:5]  # 상위 5개만 반환
    
    def _infer_user_intent(self, text: str) -> str:
        """사용자 의도를 추론합니다."""
        if "?" in text:
            return "question"
        elif any(word in text.lower() for word in ["도와", "해줘", "요청", "만들", "생성"]):
            return "request"
        else:
            return "conversation"
    
    def _generate_thought_id(self) -> str:
        """고유한 사고 ID를 생성합니다."""
        return f"thought_{int(time.time() * 1000)}"
    
    def _calculate_energy_consumption(self) -> float:
        """에너지 소비량을 계산합니다."""
        base_consumption = 0.1
        complexity_factor = self.consciousness_level * 0.2
        return base_consumption + complexity_factor
    
    def _update_memory(self, input_data: str, result: Dict[str, Any]):
        """메모리를 업데이트합니다."""
        memory_entry = {
            "timestamp": datetime.now().isoformat(),
            "input": input_data,
            "result": result,
            "consciousness_level": self.consciousness_level
        }
        
        # 메모리 크기 제한
        if len(self.memory) > 1000:
            # 오래된 메모리 제거
            oldest_key = min(self.memory.keys())
            del self.memory[oldest_key]
        
        self.memory[memory_entry["timestamp"]] = memory_entry
    
    def _update_brain_state(self):
        """두뇌 상태를 업데이트합니다."""
        # 에너지 소모
        self.energy_level = max(0.1, self.energy_level - 0.01)
        
        # 집중도 조정
        if self.energy_level < 0.3:
            self.focus_level = max(0.3, self.focus_level - 0.05)
        else:
            self.focus_level = min(1.0, self.focus_level + 0.02)
        
        # 의식 수준 조정
        if self.energy_level > 0.7 and self.focus_level > 0.7:
            self.consciousness_level = min(1.0, self.consciousness_level + 0.01)
        else:
            self.consciousness_level = max(0.1, self.consciousness_level - 0.005)
    
    def get_brain_status(self) -> Dict[str, Any]:
        """두뇌 상태를 반환합니다."""
        return {
            "consciousness_level": self.consciousness_level,
            "energy_level": self.energy_level,
            "focus_level": self.focus_level,
            "creativity_level": self.creativity_level,
            "logic_level": self.logic_level,
            "emotion_level": self.emotion_level,
            "is_awake": self.is_awake,
            "memory_count": len(self.memory),
            "thought_count": len(self.thought_processes)
        }
    
    def adjust_consciousness(self, level: float):
        """의식 수준을 조정합니다."""
        self.consciousness_level = max(0.0, min(1.0, level))
        logger.info(f"의식 수준 조정: {self.consciousness_level}")
    
    def rest(self, duration: float = 1.0):
        """두뇌를 휴식시킵니다."""
        self.energy_level = min(1.0, self.energy_level + duration * 0.1)
        self.focus_level = min(1.0, self.focus_level + duration * 0.05)
        logger.info(f"두뇌 휴식 완료: 에너지 {self.energy_level:.2f}, 집중도 {self.focus_level:.2f}")
    
    def get_thought_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """사고 이력을 반환합니다."""
        return self.thought_processes[-limit:] if self.thought_processes else []

# 전역 인스턴스
_brain_core = BrainCore()

def think(input_data: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    사고 프로세스를 실행하는 전역 함수
    
    Args:
        input_data: 입력 데이터
        context: 컨텍스트 정보
        
    Returns:
        사고 결과
    """
    return _brain_core.think(input_data, context)

def get_brain_status() -> Dict[str, Any]:
    """두뇌 상태를 반환합니다."""
    return _brain_core.get_brain_status()

def adjust_consciousness(level: float):
    """의식 수준을 조정합니다."""
    _brain_core.adjust_consciousness(level)

def rest_brain(duration: float = 1.0):
    """두뇌를 휴식시킵니다."""
    _brain_core.rest(duration)