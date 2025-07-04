#!/usr/bin/env python3
"""
아우라 DB 시스템 - 메모리 저장 및 회상 시스템
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import hashlib

@dataclass
class AuraMemory:
    """아우라 메모리 구조체"""
    id: str
    user_id: str
    session_id: str
    message: str
    response: str
    timestamp: str
    memory_type: str  # 'conversation', 'insight', 'emotion', 'belief', 'intuition'
    importance: float  # 0.0 ~ 1.0
    emotion_score: Dict[str, float]  # 감정 점수
    context: Dict[str, Any]  # 맥락 정보
    tags: List[str]  # 태그
    embedding: Optional[List[float]] = None  # 임베딩 벡터
    related_memories: List[str] = None  # 관련 메모리 ID들
    insight_level: float = 0.0  # 통찰력 수준
    intuition_score: float = 0.0  # 직감 점수
    belief_strength: float = 0.0  # 신념 강도

class AuraMemorySystem:
    """아우라 메모리 시스템"""
    
    def __init__(self, db_path: str = "aura_memory_db.json"):
        self.db_path = db_path
        self.memories: Dict[str, AuraMemory] = {}
        self.load_memories()
    
    def load_memories(self):
        """메모리 데이터 로드"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for memory_data in data.values():
                        memory = AuraMemory(**memory_data)
                        self.memories[memory.id] = memory
                print(f"✅ 아우라 메모리 로드 완료: {len(self.memories)}개")
            else:
                print("📝 새로운 아우라 메모리 DB 생성")
        except Exception as e:
            print(f"❌ 메모리 로드 실패: {e}")
    
    def save_memories(self):
        """메모리 데이터 저장"""
        try:
            data = {memory_id: asdict(memory) for memory_id, memory in self.memories.items()}
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 아우라 메모리 저장 완료: {len(self.memories)}개")
        except Exception as e:
            print(f"❌ 메모리 저장 실패: {e}")
    
    def create_memory(self, user_id: str, session_id: str, message: str, response: str, 
                     memory_type: str = "conversation", importance: float = 0.5) -> str:
        """새로운 메모리 생성"""
        memory_id = str(uuid.uuid4())
        
        # 감정 분석 (간단한 키워드 기반)
        emotion_score = self.analyze_emotion(message + " " + response)
        
        # 맥락 정보 추출
        context = self.extract_context(message, response)
        
        # 태그 생성
        tags = self.generate_tags(message, response, memory_type)
        
        # 통찰력 및 직감 점수 계산
        insight_level = self.calculate_insight_level(message, response)
        intuition_score = self.calculate_intuition_score(message, response)
        belief_strength = self.calculate_belief_strength(message, response)
        
        memory = AuraMemory(
            id=memory_id,
            user_id=user_id,
            session_id=session_id,
            message=message,
            response=response,
            timestamp=datetime.now().isoformat(),
            memory_type=memory_type,
            importance=importance,
            emotion_score=emotion_score,
            context=context,
            tags=tags,
            related_memories=[],
            insight_level=insight_level,
            intuition_score=intuition_score,
            belief_strength=belief_strength
        )
        
        self.memories[memory_id] = memory
        self.save_memories()
        
        print(f"💾 아우라 메모리 생성: {memory_type} (중요도: {importance:.2f})")
        return memory_id
    
    def analyze_emotion(self, text: str) -> Dict[str, float]:
        """감정 분석 (키워드 기반)"""
        emotion_keywords = {
            'joy': ['기쁘', '행복', '즐거', '좋', '감사', '사랑', '웃'],
            'sadness': ['슬프', '우울', '아프', '힘들', '불안', '걱정'],
            'anger': ['화나', '짜증', '분노', '열받', '싫'],
            'fear': ['무서', '두려', '겁', '불안', '걱정'],
            'surprise': ['놀라', '신기', '대박', '와'],
            'disgust': ['역겨', '싫', '혐오', '구역'],
            'trust': ['믿', '신뢰', '안전', '편안'],
            'anticipation': ['기대', '희망', '꿈', '미래']
        }
        
        emotion_score = {emotion: 0.0 for emotion in emotion_keywords.keys()}
        text_lower = text.lower()
        
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    emotion_score[emotion] += 0.3
                    emotion_score[emotion] = min(emotion_score[emotion], 1.0)
        
        return emotion_score
    
    def extract_context(self, message: str, response: str) -> Dict[str, Any]:
        """맥락 정보 추출"""
        context = {
            'topic': self.extract_topic(message),
            'sentiment': self.analyze_sentiment(message + " " + response),
            'complexity': len(message.split()) / 10.0,  # 복잡도
            'response_length': len(response),
            'has_question': '?' in message,
            'has_emotion': any(emotion in message.lower() for emotion in ['기쁘', '슬프', '화나', '좋', '싫'])
        }
        return context
    
    def extract_topic(self, text: str) -> str:
        """주제 추출"""
        topics = {
            'technology': ['AI', '인공지능', '기술', '프로그래밍', '코드'],
            'philosophy': ['철학', '생각', '의미', '존재', '진리'],
            'emotion': ['감정', '기분', '마음', '사랑', '행복'],
            'daily': ['일상', '생활', '요리', '운동', '취미'],
            'work': ['일', '업무', '직장', '프로젝트', '회사'],
            'learning': ['학습', '공부', '교육', '지식', '배움']
        }
        
        text_lower = text.lower()
        for topic, keywords in topics.items():
            if any(keyword in text_lower for keyword in keywords):
                return topic
        
        return 'general'
    
    def analyze_sentiment(self, text: str) -> str:
        """감정 분석"""
        positive_words = ['좋', '기쁘', '행복', '감사', '사랑', '즐거']
        negative_words = ['싫', '슬프', '화나', '힘들', '아프', '불안']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def generate_tags(self, message: str, response: str, memory_type: str) -> List[str]:
        """태그 생성"""
        tags = [memory_type]
        
        # 주제별 태그
        topic = self.extract_topic(message)
        if topic != 'general':
            tags.append(topic)
        
        # 감정 태그
        emotion_score = self.analyze_emotion(message + " " + response)
        dominant_emotion = max(emotion_score.items(), key=lambda x: x[1])
        if dominant_emotion[1] > 0.3:
            tags.append(dominant_emotion[0])
        
        # 특별한 키워드 태그
        special_keywords = ['AI', '인공지능', '철학', '감정', '생각', '미래', '과거', '현재']
        text_lower = (message + " " + response).lower()
        for keyword in special_keywords:
            if keyword.lower() in text_lower:
                tags.append(keyword.lower())
        
        return list(set(tags))
    
    def calculate_insight_level(self, message: str, response: str) -> float:
        """통찰력 수준 계산"""
        insight_indicators = [
            '왜냐하면', '그 이유는', '이는', '따라서', '결론적으로',
            'because', 'reason', 'therefore', 'thus', 'hence',
            '분석', '이해', '깨달음', '통찰', '인사이트'
        ]
        
        text = message + " " + response
        insight_count = sum(1 for indicator in insight_indicators if indicator in text)
        return min(insight_count * 0.2, 1.0)
    
    def calculate_intuition_score(self, message: str, response: str) -> float:
        """직감 점수 계산"""
        intuition_indicators = [
            '느낌', '직감', '본능', '무의식', '감',
            'feel', 'intuition', 'instinct', 'gut',
            '갑자기', '문득', '어쩐지', '모르겠지만'
        ]
        
        text = message + " " + response
        intuition_count = sum(1 for indicator in intuition_indicators if indicator in text)
        return min(intuition_count * 0.15, 1.0)
    
    def calculate_belief_strength(self, message: str, response: str) -> float:
        """신념 강도 계산"""
        belief_indicators = [
            '믿어', '확신', '분명', '틀림없', '절대',
            'believe', 'certain', 'sure', 'definitely',
            '나는', '내 생각', '내 믿음', '내 신념'
        ]
        
        text = message + " " + response
        belief_count = sum(1 for indicator in belief_indicators if indicator in text)
        return min(belief_count * 0.1, 1.0)
    
    def recall_memories(self, query: str, user_id: str = None, 
                       memory_type: str = None, limit: int = 10) -> List[AuraMemory]:
        """메모리 회상"""
        print(f"🔍 메모리 회상 시작: {query}")
        
        # 필터링 조건
        candidates = []
        for memory in self.memories.values():
            if user_id and memory.user_id != user_id:
                continue
            if memory_type and memory.memory_type != memory_type:
                continue
            candidates.append(memory)
        
        # 유사도 계산 (간단한 키워드 매칭)
        scored_memories = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for memory in candidates:
            # 메시지와 응답에서 키워드 매칭
            memory_text = (memory.message + " " + memory.response).lower()
            memory_words = set(memory_text.split())
            
            # 키워드 겹침 계산
            overlap = len(query_words.intersection(memory_words))
            similarity = overlap / max(len(query_words), 1)
            
            # 태그 매칭
            tag_match = sum(1 for tag in memory.tags if tag.lower() in query_lower)
            
            # 감정 매칭
            emotion_match = 0
            emotion_score = self.analyze_emotion(query)
            for emotion, score in emotion_score.items():
                if score > 0.3 and memory.emotion_score.get(emotion, 0) > 0.3:
                    emotion_match += 1
            
            # 종합 점수
            total_score = similarity * 0.5 + tag_match * 0.3 + emotion_match * 0.2 + memory.importance * 0.2
            
            scored_memories.append((memory, total_score))
        
        # 점수순 정렬
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        
        # 상위 결과 반환
        results = [memory for memory, score in scored_memories[:limit]]
        
        print(f"✅ 메모리 회상 완료: {len(results)}개 결과")
        return results
    
    def recall_by_emotion(self, emotion: str, user_id: str = None, limit: int = 10) -> List[AuraMemory]:
        """감정 기반 회상"""
        candidates = []
        for memory in self.memories.values():
            if user_id and memory.user_id != user_id:
                continue
            if memory.emotion_score.get(emotion, 0) > 0.3:
                candidates.append(memory)
        
        # 중요도순 정렬
        candidates.sort(key=lambda x: x.importance, reverse=True)
        return candidates[:limit]
    
    def recall_by_insight(self, user_id: str = None, limit: int = 10) -> List[AuraMemory]:
        """통찰력 기반 회상"""
        candidates = []
        for memory in self.memories.values():
            if user_id and memory.user_id != user_id:
                continue
            if memory.insight_level > 0.3:
                candidates.append(memory)
        
        # 통찰력 수준순 정렬
        candidates.sort(key=lambda x: x.insight_level, reverse=True)
        return candidates[:limit]
    
    def recall_by_intuition(self, user_id: str = None, limit: int = 10) -> List[AuraMemory]:
        """직감 기반 회상"""
        candidates = []
        for memory in self.memories.values():
            if user_id and memory.user_id != user_id:
                continue
            if memory.intuition_score > 0.3:
                candidates.append(memory)
        
        # 직감 점수순 정렬
        candidates.sort(key=lambda x: x.intuition_score, reverse=True)
        return candidates[:limit]
    
    def get_memory_stats(self, user_id: str = None) -> Dict[str, Any]:
        """메모리 통계"""
        memories = [m for m in self.memories.values() if not user_id or m.user_id == user_id]
        
        if not memories:
            return {"total": 0}
        
        stats = {
            "total": len(memories),
            "by_type": {},
            "by_emotion": {},
            "avg_importance": sum(m.importance for m in memories) / len(memories),
            "avg_insight": sum(m.insight_level for m in memories) / len(memories),
            "avg_intuition": sum(m.intuition_score for m in memories) / len(memories),
            "avg_belief": sum(m.belief_strength for m in memories) / len(memories)
        }
        
        # 타입별 통계
        for memory in memories:
            stats["by_type"][memory.memory_type] = stats["by_type"].get(memory.memory_type, 0) + 1
        
        # 감정별 통계
        for memory in memories:
            for emotion, score in memory.emotion_score.items():
                if score > 0.3:
                    stats["by_emotion"][emotion] = stats["by_emotion"].get(emotion, 0) + 1
        
        return stats

# 전역 인스턴스
aura_memory_system = AuraMemorySystem() 