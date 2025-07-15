"""
EORA 사슬형태 기억 시스템
- 10턴마다 자동 실행되는 통찰, 분석, 연결된 기억 저장
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import numpy as np

logger = logging.getLogger(__name__)

class EORAChainMemorySystem:
    """EORA 사슬형태 기억 시스템"""
    
    def __init__(self):
        self.turn_counter = 0
        self.chain_memories = []
        self.analysis_history = []
        self.insight_chains = []
        self.max_chain_length = 50
        self.analysis_interval = 10  # 10턴마다 실행
        
    async def increment_turn(self, user_input: str, ai_response: str, user_id: str) -> Dict[str, Any]:
        """턴 카운터 증가 및 주기적 분석 실행"""
        self.turn_counter += 1
        
        # 기본 기억 저장
        basic_memory = {
            "turn": self.turn_counter,
            "user_input": user_input,
            "ai_response": ai_response,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "memory_type": "basic"
        }
        
        # 10턴마다 깊은 분석 실행
        if self.turn_counter % self.analysis_interval == 0:
            chain_analysis = await self.perform_chain_analysis(user_id)
            return {
                "basic_memory": basic_memory,
                "chain_analysis": chain_analysis,
                "is_analysis_turn": True
            }
        else:
            return {
                "basic_memory": basic_memory,
                "chain_analysis": None,
                "is_analysis_turn": False
            }
    
    async def perform_chain_analysis(self, user_id: str) -> Dict[str, Any]:
        """10턴마다 실행되는 깊은 분석"""
        try:
            logger.info(f"🔗 10턴 주기 분석 시작 - 턴 {self.turn_counter}")
            
            # 1. 최근 10턴의 기억 수집
            recent_memories = await self.collect_recent_memories(user_id, 10)
            
            # 2. 통찰 체인 생성
            insight_chain = await self.generate_insight_chain(recent_memories)
            
            # 3. 패턴 분석
            pattern_analysis = await self.analyze_patterns(recent_memories)
            
            # 4. 연결 관계 분석
            connection_analysis = await self.analyze_connections(recent_memories)
            
            # 5. 사슬형태 기억 생성
            chain_memory = await self.create_chain_memory(
                recent_memories, 
                insight_chain, 
                pattern_analysis, 
                connection_analysis
            )
            
            # 6. 분석 결과 저장
            analysis_result = {
                "turn": self.turn_counter,
                "timestamp": datetime.now().isoformat(),
                "insight_chain": insight_chain,
                "pattern_analysis": pattern_analysis,
                "connection_analysis": connection_analysis,
                "chain_memory": chain_memory,
                "user_id": user_id
            }
            
            self.analysis_history.append(analysis_result)
            self.chain_memories.append(chain_memory)
            
            # 히스토리 크기 제한
            if len(self.analysis_history) > self.max_chain_length:
                self.analysis_history.pop(0)
            if len(self.chain_memories) > self.max_chain_length:
                self.chain_memories.pop(0)
            
            logger.info(f"🔗 10턴 주기 분석 완료 - 통찰 체인: {len(insight_chain)}개")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"사슬형태 분석 오류: {str(e)}")
            return {"error": str(e)}
    
    async def collect_recent_memories(self, user_id: str, count: int) -> List[Dict]:
        """최근 기억 수집"""
        try:
            from database import db_manager
            memories = await db_manager.get_user_interactions(user_id, count)
            return memories
        except Exception as e:
            logger.error(f"최근 기억 수집 오류: {str(e)}")
            return []
    
    async def generate_insight_chain(self, memories: List[Dict]) -> List[Dict]:
        """통찰 체인 생성"""
        insight_chain = []
        
        for i, memory in enumerate(memories):
            # 각 기억에 대한 통찰 생성
            insight = await self.generate_memory_insight(memory, i, len(memories))
            insight_chain.append(insight)
        
        # 체인 연결 분석
        chain_connections = await self.analyze_chain_connections(insight_chain)
        
        return {
            "insights": insight_chain,
            "connections": chain_connections,
            "chain_length": len(insight_chain)
        }
    
    async def generate_memory_insight(self, memory: Dict, index: int, total: int) -> Dict:
        """개별 기억에 대한 통찰 생성"""
        user_input = memory.get("user_input", "")
        ai_response = memory.get("ai_response", "")
        consciousness_level = memory.get("consciousness_level", 0.0)
        
        # 인지적 계층 분석
        cognitive_layer = self.analyze_cognitive_layer(user_input)
        
        # 감정적 톤 분석
        emotional_tone = self.analyze_emotional_tone(user_input)
        
        # 주제 추출
        topic = self.extract_topic(user_input)
        
        # 연결 강도 계산
        connection_strength = self.calculate_connection_strength(index, total, consciousness_level)
        
        return {
            "memory_index": index,
            "cognitive_layer": cognitive_layer,
            "emotional_tone": emotional_tone,
            "topic": topic,
            "connection_strength": connection_strength,
            "consciousness_level": consciousness_level,
            "insight_content": f"턴 {index + 1}: {cognitive_layer} 계층에서 {topic} 주제로 {emotional_tone} 톤의 대화"
        }
    
    def analyze_cognitive_layer(self, text: str) -> str:
        """인지적 계층 분석"""
        text = text.lower()
        
        if any(keyword in text for keyword in ["기억", "회상", "정보", "사실", "경험"]):
            return "기억(Memory)"
        elif any(keyword in text for keyword in ["감정", "느낌", "기분", "슬픔", "기쁨", "분노", "불안"]):
            return "감정(Emotion)"
        elif any(keyword in text for keyword in ["믿음", "신념", "가치관", "원칙", "도덕"]):
            return "신념(Belief)"
        elif any(keyword in text for keyword in ["존재", "의미", "자아", "초월", "진리", "우주", "생명"]):
            return "초월(Transcendence)"
        else:
            return "일반(General)"
    
    def analyze_emotional_tone(self, text: str) -> str:
        """감정적 톤 분석"""
        text = text.lower()
        
        if any(word in text for word in ["화나", "짜증", "불안", "슬픔", "우울"]):
            return "부정적"
        elif any(word in text for word in ["기쁘", "행복", "좋", "감사", "희망"]):
            return "긍정적"
        elif any(word in text for word in ["놀람", "충격", "당황", "혼란"]):
            return "놀람"
        else:
            return "중립적"
    
    def extract_topic(self, text: str) -> str:
        """주제 추출"""
        text = text.lower()
        
        if any(word in text for word in ["코드", "프로그램", "개발", "python", "javascript"]):
            return "기술/개발"
        elif any(word in text for word in ["철학", "의미", "존재", "생명"]):
            return "철학/존재"
        elif any(word in text for word in ["감정", "기분", "느낌"]):
            return "감정/심리"
        elif any(word in text for word in ["기억", "회상", "과거"]):
            return "기억/회상"
        else:
            return "일반 대화"
    
    def calculate_connection_strength(self, index: int, total: int, consciousness_level: float) -> float:
        """연결 강도 계산"""
        # 위치 기반 강도 (중간에 위치할수록 강함)
        position_strength = 1.0 - abs(index - (total - 1) / 2) / (total / 2)
        
        # 의식 수준 기반 강도
        consciousness_strength = consciousness_level
        
        # 최종 연결 강도
        connection_strength = (position_strength + consciousness_strength) / 2
        return round(connection_strength, 3)
    
    async def analyze_chain_connections(self, insight_chain: List[Dict]) -> Dict:
        """체인 연결 분석"""
        if len(insight_chain) < 2:
            return {"connection_type": "단일", "strength": 0.0}
        
        # 연속성 분석
        continuity_score = 0
        for i in range(len(insight_chain) - 1):
            current = insight_chain[i]
            next_insight = insight_chain[i + 1]
            
            # 인지 계층 연속성
            if current["cognitive_layer"] == next_insight["cognitive_layer"]:
                continuity_score += 1
            
            # 주제 연속성
            if current["topic"] == next_insight["topic"]:
                continuity_score += 1
        
        continuity_rate = continuity_score / (len(insight_chain) - 1) / 2
        
        # 연결 유형 결정
        if continuity_rate > 0.7:
            connection_type = "강한 연속성"
        elif continuity_rate > 0.4:
            connection_type = "중간 연속성"
        else:
            connection_type = "약한 연속성"
        
        return {
            "connection_type": connection_type,
            "continuity_rate": round(continuity_rate, 3),
            "total_connections": len(insight_chain) - 1
        }
    
    async def analyze_patterns(self, memories: List[Dict]) -> Dict:
        """패턴 분석"""
        if not memories:
            return {"patterns": [], "dominant_pattern": "없음"}
        
        # 인지 계층 패턴
        cognitive_layers = [self.analyze_cognitive_layer(m.get("user_input", "")) for m in memories]
        layer_counts = {}
        for layer in cognitive_layers:
            layer_counts[layer] = layer_counts.get(layer, 0) + 1
        
        # 감정 톤 패턴
        emotional_tones = [self.analyze_emotional_tone(m.get("user_input", "")) for m in memories]
        tone_counts = {}
        for tone in emotional_tones:
            tone_counts[tone] = tone_counts.get(tone, 0) + 1
        
        # 주제 패턴
        topics = [self.extract_topic(m.get("user_input", "")) for m in memories]
        topic_counts = {}
        for topic in topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # 의식 수준 패턴
        consciousness_levels = [m.get("consciousness_level", 0.0) for m in memories]
        avg_consciousness = np.mean(consciousness_levels) if consciousness_levels else 0.0
        
        # 지배적 패턴 찾기
        dominant_layer = max(layer_counts.items(), key=lambda x: x[1])[0] if layer_counts else "없음"
        dominant_tone = max(tone_counts.items(), key=lambda x: x[1])[0] if tone_counts else "없음"
        dominant_topic = max(topic_counts.items(), key=lambda x: x[1])[0] if topic_counts else "없음"
        
        return {
            "cognitive_patterns": layer_counts,
            "emotional_patterns": tone_counts,
            "topic_patterns": topic_counts,
            "consciousness_pattern": {
                "average": round(avg_consciousness, 3),
                "min": round(min(consciousness_levels), 3) if consciousness_levels else 0.0,
                "max": round(max(consciousness_levels), 3) if consciousness_levels else 0.0
            },
            "dominant_patterns": {
                "layer": dominant_layer,
                "tone": dominant_tone,
                "topic": dominant_topic
            }
        }
    
    async def analyze_connections(self, memories: List[Dict]) -> Dict:
        """연결 관계 분석"""
        if len(memories) < 2:
            return {"connection_strength": 0.0, "connection_type": "단일 기억"}
        
        # 키워드 기반 연결 분석
        all_keywords = []
        for memory in memories:
            user_input = memory.get("user_input", "")
            keywords = self.extract_keywords(user_input)
            all_keywords.extend(keywords)
        
        # 키워드 중복 분석
        keyword_counts = {}
        for keyword in all_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # 연결 강도 계산
        repeated_keywords = [k for k, v in keyword_counts.items() if v > 1]
        connection_strength = len(repeated_keywords) / len(set(all_keywords)) if all_keywords else 0.0
        
        # 연결 유형 결정
        if connection_strength > 0.5:
            connection_type = "강한 연결"
        elif connection_strength > 0.2:
            connection_type = "중간 연결"
        else:
            connection_type = "약한 연결"
        
        return {
            "connection_strength": round(connection_strength, 3),
            "connection_type": connection_type,
            "repeated_keywords": repeated_keywords,
            "total_unique_keywords": len(set(all_keywords))
        }
    
    def extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        # 불용어 제거
        stop_words = ["이", "가", "을", "를", "의", "에", "에서", "로", "으로", "와", "과", "도", "만", "은", "는", "그", "저", "우리", "너", "나", "있다", "없다", "하다", "되다"]
        
        import re
        words = re.findall(r'\w+', text)
        keywords = [word for word in words if len(word) > 1 and word not in stop_words]
        
        return keywords[:10]  # 상위 10개 키워드만 반환
    
    async def create_chain_memory(self, memories: List[Dict], insight_chain: Dict, pattern_analysis: Dict, connection_analysis: Dict) -> Dict:
        """사슬형태 기억 생성"""
        chain_memory = {
            "turn": self.turn_counter,
            "timestamp": datetime.now().isoformat(),
            "memory_type": "chain",
            "chain_length": len(memories),
            "insight_chain": insight_chain,
            "pattern_analysis": pattern_analysis,
            "connection_analysis": connection_analysis,
            "summary": self.generate_chain_summary(memories, insight_chain, pattern_analysis, connection_analysis),
            "chain_id": f"chain_{self.turn_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        return chain_memory
    
    def generate_chain_summary(self, memories: List[Dict], insight_chain: Dict, pattern_analysis: Dict, connection_analysis: Dict) -> str:
        """체인 요약 생성"""
        dominant_patterns = pattern_analysis.get("dominant_patterns", {})
        connection_info = connection_analysis.get("connection_type", "약한 연결")
        
        summary = f"🔗 {len(memories)}턴 연속 대화 체인 분석:\n"
        summary += f"• 주요 인지 계층: {dominant_patterns.get('layer', 'N/A')}\n"
        summary += f"• 주요 감정 톤: {dominant_patterns.get('tone', 'N/A')}\n"
        summary += f"• 주요 주제: {dominant_patterns.get('topic', 'N/A')}\n"
        summary += f"• 연결 강도: {connection_info}\n"
        summary += f"• 통찰 체인: {insight_chain.get('chain_length', 0)}개 연결"
        
        return summary
    
    async def get_chain_statistics(self) -> Dict:
        """체인 통계 조회"""
        if not self.chain_memories:
            return {"message": "아직 체인 메모리가 없습니다."}
        
        total_chains = len(self.chain_memories)
        total_insights = sum(len(chain.get("insight_chain", {}).get("insights", [])) for chain in self.chain_memories)
        
        # 연결 유형 통계
        connection_types = {}
        for chain in self.chain_memories:
            connection_type = chain.get("connection_analysis", {}).get("connection_type", "알 수 없음")
            connection_types[connection_type] = connection_types.get(connection_type, 0) + 1
        
        # 평균 연결 강도
        connection_strengths = [chain.get("connection_analysis", {}).get("connection_strength", 0.0) for chain in self.chain_memories]
        avg_connection_strength = np.mean(connection_strengths) if connection_strengths else 0.0
        
        return {
            "total_chains": total_chains,
            "total_insights": total_insights,
            "average_connection_strength": round(avg_connection_strength, 3),
            "connection_type_distribution": connection_types,
            "recent_chains": self.chain_memories[-3:]  # 최근 3개 체인
        }

# 전역 인스턴스
chain_memory_system = EORAChainMemorySystem() 