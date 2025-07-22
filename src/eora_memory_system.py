"""
EORA 완전 통합 메모리 시스템
- 저장: 감정, 신념, 맥락, 연결을 포함한 다차원 메모리 저장
- 회상: 감정 기반, 맥락 기반, 연결 기반 다중 회상 전략
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
from bson import ObjectId
import re
import hashlib

logger = logging.getLogger(__name__)

class EORAMemorySystem:
    """완전 통합된 EORA 메모리 시스템"""
    
    def __init__(self, mongo_uri="mongodb://localhost:27017"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client["eora_memory"]
        
        # 메모리 컬렉션들
        self.memories = self.db["memories"]
        self.emotion_memories = self.db["emotion_memories"]
        self.belief_memories = self.db["belief_memories"]
        self.context_memories = self.db["context_memories"]
        self.connection_index = self.db["connection_index"]
        
        # 인덱스 생성
        self._create_indexes()
        
        # 메모리 설정
        self.max_memories_per_user = 1000
        self.recall_limit = 10
        self.emotion_threshold = 0.3
        self.connection_threshold = 0.5
        
    def _create_indexes(self):
        """데이터베이스 인덱스 생성"""
        try:
            # 기본 메모리 인덱스
            self.memories.create_index([("user_id", 1), ("timestamp", -1)])
            self.memories.create_index([("topic", 1), ("emotion_score", -1)])
            self.memories.create_index([("connections", 1)])
            
            # 감정 메모리 인덱스
            self.emotion_memories.create_index([("emotion_label", 1), ("timestamp", -1)])
            self.emotion_memories.create_index([("emotion_score", -1)])
            
            # 신념 메모리 인덱스
            self.belief_memories.create_index([("belief_tags", 1), ("timestamp", -1)])
            
            # 맥락 메모리 인덱스
            self.context_memories.create_index([("context_keywords", 1), ("timestamp", -1)])
            
            logger.info("메모리 시스템 인덱스 생성 완료")
        except Exception as e:
            logger.error(f"인덱스 생성 오류: {str(e)}")
    
    async def save_memory(self, 
                         user_id: str,
                         user_input: str, 
                         ai_response: str,
                         consciousness_level: float = 0.0,
                         emotion_data: Dict = None,
                         belief_data: Dict = None,
                         context_data: Dict = None,
                         session_id: str = None) -> Dict:
        """다차원 메모리 저장"""
        try:
            timestamp = datetime.now()
            
            # 기본 메모리 데이터
            memory_data = {
                "user_id": user_id,
                "timestamp": timestamp,
                "session_id": session_id or f"session_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                "user_input": user_input,
                "ai_response": ai_response,
                "consciousness_level": consciousness_level,
                "emotion_score": emotion_data.get("score", 0.0) if emotion_data else 0.0,
                "emotion_label": emotion_data.get("label", "neutral") if emotion_data else "neutral",
                "belief_tags": belief_data.get("tags", []) if belief_data else [],
                "context_keywords": context_data.get("keywords", []) if context_data else [],
                "topic": self._extract_topic(user_input),
                "sub_topic": self._extract_sub_topic(user_input),
                "summary": self._generate_summary(user_input, ai_response),
                "importance_score": self._calculate_importance(user_input, ai_response, consciousness_level),
                "connections": [],
                "last_accessed": None,
                "access_count": 0,
                "forgetting_score": 1.0
            }
            
            # 메모리 저장
            result = self.memories.insert_one(memory_data)
            memory_id = str(result.inserted_id)
            
            # 감정 메모리 저장
            if emotion_data and emotion_data.get("score", 0) > self.emotion_threshold:
                await self._save_emotion_memory(memory_id, emotion_data, timestamp)
            
            # 신념 메모리 저장
            if belief_data and belief_data.get("tags"):
                await self._save_belief_memory(memory_id, belief_data, timestamp)
            
            # 맥락 메모리 저장
            if context_data and context_data.get("keywords"):
                await self._save_context_memory(memory_id, context_data, timestamp)
            
            # 연결 관계 업데이트
            await self._update_connections(memory_id, user_input, ai_response)
            
            logger.info(f"메모리 저장 완료 - 사용자: {user_id}, ID: {memory_id}")
            return {"memory_id": memory_id, "status": "saved"}
            
        except Exception as e:
            logger.error(f"메모리 저장 오류: {str(e)}")
            return {"error": str(e)}
    
    async def _save_emotion_memory(self, memory_id: str, emotion_data: Dict, timestamp: datetime):
        """감정 메모리 저장"""
        emotion_memory = {
            "memory_id": memory_id,
            "timestamp": timestamp,
            "emotion_label": emotion_data.get("label", "neutral"),
            "emotion_score": emotion_data.get("score", 0.0),
            "emotion_intensity": emotion_data.get("intensity", 0.0),
            "emotion_context": emotion_data.get("context", ""),
            "valence": emotion_data.get("valence", 0.0),
            "arousal": emotion_data.get("arousal", 0.0)
        }
        self.emotion_memories.insert_one(emotion_memory)
    
    async def _save_belief_memory(self, memory_id: str, belief_data: Dict, timestamp: datetime):
        """신념 메모리 저장"""
        belief_memory = {
            "memory_id": memory_id,
            "timestamp": timestamp,
            "belief_tags": belief_data.get("tags", []),
            "belief_strength": belief_data.get("strength", 0.0),
            "belief_context": belief_data.get("context", ""),
            "belief_type": belief_data.get("type", "general")
        }
        self.belief_memories.insert_one(belief_memory)
    
    async def _save_context_memory(self, memory_id: str, context_data: Dict, timestamp: datetime):
        """맥락 메모리 저장"""
        context_memory = {
            "memory_id": memory_id,
            "timestamp": timestamp,
            "context_keywords": context_data.get("keywords", []),
            "context_type": context_data.get("type", "general"),
            "context_importance": context_data.get("importance", 0.0),
            "context_relations": context_data.get("relations", [])
        }
        self.context_memories.insert_one(context_memory)
    
    async def recall_memories(self, 
                            user_id: str,
                            query: str,
                            recall_type: str = "comprehensive",
                            limit: int = None) -> List[Dict]:
        """다중 전략 메모리 회상"""
        try:
            limit = limit or self.recall_limit
            recalled_memories = []
            
            if recall_type == "comprehensive":
                # 종합 회상: 모든 전략 사용
                recalled_memories = await self._comprehensive_recall(user_id, query, limit)
            elif recall_type == "emotion":
                # 감정 기반 회상
                recalled_memories = await self._emotion_based_recall(user_id, query, limit)
            elif recall_type == "context":
                # 맥락 기반 회상
                recalled_memories = await self._context_based_recall(user_id, query, limit)
            elif recall_type == "belief":
                # 신념 기반 회상
                recalled_memories = await self._belief_based_recall(user_id, query, limit)
            elif recall_type == "semantic":
                # 의미 기반 회상
                recalled_memories = await self._semantic_recall(user_id, query, limit)
            else:
                # 기본 키워드 기반 회상
                recalled_memories = await self._keyword_recall(user_id, query, limit)
            
            # 회상 결과 정제 및 정렬
            cleaned_memories = self._clean_recall_results(recalled_memories)
            sorted_memories = self._sort_recall_results(cleaned_memories, query)
            
            # 접근 기록 업데이트
            await self._update_access_records([m["_id"] for m in sorted_memories])
            
            logger.info(f"메모리 회상 완료 - 사용자: {user_id}, 쿼리: {query}, 결과: {len(sorted_memories)}개")
            return sorted_memories
            
        except Exception as e:
            logger.error(f"메모리 회상 오류: {str(e)}")
            return []
    
    async def _comprehensive_recall(self, user_id: str, query: str, limit: int) -> List[Dict]:
        """종합 회상 전략"""
        all_memories = []
        
        # 1. 감정 기반 회상
        emotion_memories = await self._emotion_based_recall(user_id, query, limit // 3)
        all_memories.extend(emotion_memories)
        
        # 2. 맥락 기반 회상
        context_memories = await self._context_based_recall(user_id, query, limit // 3)
        all_memories.extend(context_memories)
        
        # 3. 의미 기반 회상
        semantic_memories = await self._semantic_recall(user_id, query, limit // 3)
        all_memories.extend(semantic_memories)
        
        # 중복 제거 및 정렬
        unique_memories = self._remove_duplicates(all_memories)
        return unique_memories[:limit]
    
    async def _emotion_based_recall(self, user_id: str, query: str, limit: int) -> List[Dict]:
        """감정 기반 회상"""
        # 쿼리에서 감정 키워드 추출
        emotion_keywords = self._extract_emotion_keywords(query)
        
        if not emotion_keywords:
            return []
        
        # 감정 메모리에서 검색
        emotion_query = {
            "emotion_label": {"$in": emotion_keywords},
            "user_id": user_id
        }
        
        memories = list(self.memories.find(emotion_query)
                       .sort([("emotion_score", -1), ("timestamp", -1)])
                       .limit(limit))
        
        return memories
    
    async def _context_based_recall(self, user_id: str, query: str, limit: int) -> List[Dict]:
        """맥락 기반 회상"""
        # 쿼리에서 맥락 키워드 추출
        context_keywords = self._extract_context_keywords(query)
        
        if not context_keywords:
            return []
        
        # 맥락 메모리에서 검색
        context_query = {
            "context_keywords": {"$in": context_keywords},
            "user_id": user_id
        }
        
        memories = list(self.memories.find(context_query)
                       .sort([("importance_score", -1), ("timestamp", -1)])
                       .limit(limit))
        
        return memories
    
    async def _belief_based_recall(self, user_id: str, query: str, limit: int) -> List[Dict]:
        """신념 기반 회상"""
        # 쿼리에서 신념 키워드 추출
        belief_keywords = self._extract_belief_keywords(query)
        
        if not belief_keywords:
            return []
        
        # 신념 메모리에서 검색
        belief_query = {
            "belief_tags": {"$in": belief_keywords},
            "user_id": user_id
        }
        
        memories = list(self.memories.find(belief_query)
                       .sort([("importance_score", -1), ("timestamp", -1)])
                       .limit(limit))
        
        return memories
    
    async def _semantic_recall(self, user_id: str, query: str, limit: int) -> List[Dict]:
        """의미 기반 회상"""
        # 쿼리 키워드 추출
        query_keywords = self._extract_keywords(query)
        
        if not query_keywords:
            return []
        
        # 의미적 유사성 검색
        semantic_query = {
            "user_id": user_id,
            "$or": [
                {"user_input": {"$regex": "|".join(query_keywords), "$options": "i"}},
                {"ai_response": {"$regex": "|".join(query_keywords), "$options": "i"}},
                {"summary": {"$regex": "|".join(query_keywords), "$options": "i"}}
            ]
        }
        
        memories = list(self.memories.find(semantic_query)
                       .sort([("importance_score", -1), ("timestamp", -1)])
                       .limit(limit))
        
        return memories
    
    async def _keyword_recall(self, user_id: str, query: str, limit: int) -> List[Dict]:
        """키워드 기반 회상"""
        query_keywords = self._extract_keywords(query)
        
        if not query_keywords:
            return []
        
        # 키워드 검색
        keyword_query = {
            "user_id": user_id,
            "$or": [
                {"user_input": {"$regex": "|".join(query_keywords), "$options": "i"}},
                {"ai_response": {"$regex": "|".join(query_keywords), "$options": "i"}},
                {"topic": {"$regex": "|".join(query_keywords), "$options": "i"}},
                {"sub_topic": {"$regex": "|".join(query_keywords), "$options": "i"}}
            ]
        }
        
        memories = list(self.memories.find(keyword_query)
                       .sort([("importance_score", -1), ("timestamp", -1)])
                       .limit(limit))
        
        return memories
    
    def _extract_emotion_keywords(self, text: str) -> List[str]:
        """감정 키워드 추출"""
        emotion_keywords = [
            "기쁨", "행복", "즐거움", "만족", "감사", "사랑", "희망", "열정",
            "슬픔", "우울", "절망", "외로움", "그리움", "아픔", "상실",
            "분노", "화남", "짜증", "불만", "적대감", "원망",
            "불안", "걱정", "두려움", "긴장", "스트레스", "압박감",
            "놀람", "충격", "당황", "혼란", "의아함",
            "평온", "차분", "여유", "안정", "편안"
        ]
        
        found_emotions = []
        for emotion in emotion_keywords:
            if emotion in text:
                found_emotions.append(emotion)
        
        return found_emotions
    
    def _extract_context_keywords(self, text: str) -> List[str]:
        """맥락 키워드 추출"""
        context_patterns = [
            r"집에서", r"회사에서", r"학교에서", r"카페에서", r"길에서",
            r"아침에", r"점심에", r"저녁에", r"밤에", r"새벽에",
            r"친구와", r"가족과", r"동료와", r"선생님과", r"의사와",
            r"코딩", r"프로그래밍", r"개발", r"학습", r"공부",
            r"음악", r"영화", r"책", r"운동", r"요리"
        ]
        
        context_keywords = []
        for pattern in context_patterns:
            matches = re.findall(pattern, text)
            context_keywords.extend(matches)
        
        return list(set(context_keywords))
    
    def _extract_belief_keywords(self, text: str) -> List[str]:
        """신념 키워드 추출"""
        belief_keywords = [
            "믿음", "신념", "가치관", "철학", "원칙", "도덕", "윤리",
            "정의", "평등", "자유", "책임", "성실", "정직", "용기",
            "인내", "겸손", "배려", "존중", "사랑", "희생", "봉사"
        ]
        
        found_beliefs = []
        for belief in belief_keywords:
            if belief in text:
                found_beliefs.append(belief)
        
        return found_beliefs
    
    def _extract_keywords(self, text: str) -> List[str]:
        """일반 키워드 추출"""
        # 불용어 제거
        stop_words = ["이", "가", "을", "를", "의", "에", "에서", "로", "으로", "와", "과", "도", "만", "은", "는", "이", "그", "저", "우리", "너", "나"]
        
        # 단어 분리 및 필터링
        words = re.findall(r'\w+', text)
        keywords = [word for word in words if len(word) > 1 and word not in stop_words]
        
        return keywords[:10]  # 상위 10개 키워드만 반환
    
    def _extract_topic(self, text: str) -> str:
        """주제 추출"""
        topics = {
            "감정": ["기분", "느낌", "감정", "마음", "심정"],
            "일상": ["일", "생활", "루틴", "하루", "일상"],
            "관계": ["친구", "가족", "사람", "관계", "대화"],
            "학습": ["공부", "학습", "배우", "지식", "교육"],
            "기술": ["코딩", "프로그래밍", "개발", "기술", "코드"],
            "철학": ["의미", "존재", "생명", "우주", "진리", "철학"],
            "건강": ["건강", "운동", "병", "의사", "약"],
            "취미": ["취미", "관심", "좋아", "즐겨", "재미"]
        }
        
        for topic, keywords in topics.items():
            if any(keyword in text for keyword in keywords):
                return topic
        
        return "일반"
    
    def _extract_sub_topic(self, text: str) -> str:
        """하위 주제 추출"""
        # 더 구체적인 하위 주제 추출 로직
        return "일반"
    
    def _generate_summary(self, user_input: str, ai_response: str) -> str:
        """메모리 요약 생성"""
        # 간단한 요약 생성 (실제로는 더 정교한 요약 알고리즘 사용)
        combined = f"{user_input} → {ai_response}"
        if len(combined) > 200:
            return combined[:200] + "..."
        return combined
    
    def _calculate_importance(self, user_input: str, ai_response: str, consciousness_level: float) -> float:
        """중요도 점수 계산"""
        importance = 0.5  # 기본 점수
        
        # 의식 수준에 따른 가중치
        importance += consciousness_level * 0.3
        
        # 감정 키워드가 있으면 가중치 증가
        if self._extract_emotion_keywords(user_input):
            importance += 0.2
        
        # 철학적 키워드가 있으면 가중치 증가
        if any(word in user_input for word in ["의미", "존재", "생명", "우주", "진리"]):
            importance += 0.3
        
        # 응답 길이에 따른 가중치
        if len(ai_response) > 100:
            importance += 0.1
        
        return min(1.0, importance)
    
    async def _update_connections(self, memory_id: str, user_input: str, ai_response: str):
        """연결 관계 업데이트"""
        # 유사한 메모리들과의 연결 생성
        similar_memories = await self._find_similar_memories(user_input, ai_response)
        
        if similar_memories:
            # 현재 메모리에 연결 정보 추가
            self.memories.update_one(
                {"_id": ObjectId(memory_id)},
                {"$set": {"connections": [str(m["_id"]) for m in similar_memories]}}
            )
    
    async def _find_similar_memories(self, user_input: str, ai_response: str) -> List[Dict]:
        """유사한 메모리 찾기"""
        # 간단한 유사도 검색 (실제로는 더 정교한 알고리즘 사용)
        keywords = self._extract_keywords(user_input)
        
        if not keywords:
            return []
        
        # 키워드 기반 유사 메모리 검색
        similar_query = {
            "$or": [
                {"user_input": {"$regex": "|".join(keywords[:3]), "$options": "i"}},
                {"ai_response": {"$regex": "|".join(keywords[:3]), "$options": "i"}}
            ]
        }
        
        similar_memories = list(self.memories.find(similar_query)
                              .sort("timestamp", -1)
                              .limit(5))
        
        return similar_memories
    
    def _clean_recall_results(self, memories: List[Dict]) -> List[Dict]:
        """회상 결과 정제"""
        cleaned = []
        
        for memory in memories:
            # 필수 필드 확인
            if not all(key in memory for key in ["user_input", "ai_response", "timestamp"]):
                continue
            
            # 빈 내용 제거
            if not memory["user_input"].strip() or not memory["ai_response"].strip():
                continue
            
            # 너무 오래된 메모리 제거 (1년 이상)
            memory_date = memory["timestamp"]
            if isinstance(memory_date, str):
                memory_date = datetime.fromisoformat(memory_date.replace('Z', '+00:00'))
            
            if memory_date < datetime.now() - timedelta(days=365):
                continue
            
            cleaned.append(memory)
        
        return cleaned
    
    def _sort_recall_results(self, memories: List[Dict], query: str) -> List[Dict]:
        """회상 결과 정렬"""
        def sort_key(memory):
            score = 0.0
            
            # 중요도 점수
            score += memory.get("importance_score", 0.0) * 0.4
            
            # 최근성 점수
            memory_date = memory["timestamp"]
            if isinstance(memory_date, str):
                memory_date = datetime.fromisoformat(memory_date.replace('Z', '+00:00'))
            
            days_old = (datetime.now() - memory_date).days
            recency_score = max(0, 1 - (days_old / 365))
            score += recency_score * 0.3
            
            # 접근 빈도 점수
            access_count = memory.get("access_count", 0)
            score += min(1.0, access_count / 10) * 0.2
            
            # 쿼리 관련성 점수
            query_keywords = self._extract_keywords(query)
            memory_text = f"{memory['user_input']} {memory['ai_response']}"
            relevance_score = sum(1 for keyword in query_keywords if keyword in memory_text) / len(query_keywords) if query_keywords else 0
            score += relevance_score * 0.1
            
            return score
        
        return sorted(memories, key=sort_key, reverse=True)
    
    async def _update_access_records(self, memory_ids: List[str]):
        """접근 기록 업데이트"""
        for memory_id in memory_ids:
            self.memories.update_one(
                {"_id": ObjectId(memory_id)},
                {
                    "$set": {"last_accessed": datetime.now()},
                    "$inc": {"access_count": 1}
                }
            )
    
    def _remove_duplicates(self, memories: List[Dict]) -> List[Dict]:
        """중복 메모리 제거"""
        seen_ids = set()
        unique_memories = []
        
        for memory in memories:
            memory_id = str(memory["_id"])
            if memory_id not in seen_ids:
                seen_ids.add(memory_id)
                unique_memories.append(memory)
        
        return unique_memories
    
    async def get_memory_stats(self, user_id: str) -> Dict:
        """메모리 통계 조회"""
        try:
            total_memories = self.memories.count_documents({"user_id": user_id})
            
            # 감정별 통계
            emotion_stats = list(self.memories.aggregate([
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": "$emotion_label", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]))
            
            # 주제별 통계
            topic_stats = list(self.memories.aggregate([
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": "$topic", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]))
            
            # 최근 메모리
            recent_memories = list(self.memories.find({"user_id": user_id})
                                 .sort("timestamp", -1)
                                 .limit(5))
            
            return {
                "total_memories": total_memories,
                "emotion_stats": emotion_stats,
                "topic_stats": topic_stats,
                "recent_memories": recent_memories
            }
            
        except Exception as e:
            logger.error(f"메모리 통계 조회 오류: {str(e)}")
            return {"error": str(e)}
    
    async def cleanup_old_memories(self, user_id: str, days: int = 365):
        """오래된 메모리 정리"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 오래된 메모리 삭제
            result = self.memories.delete_many({
                "user_id": user_id,
                "timestamp": {"$lt": cutoff_date},
                "importance_score": {"$lt": 0.5}  # 중요도가 낮은 메모리만
            })
            
            logger.info(f"오래된 메모리 정리 완료 - 사용자: {user_id}, 삭제된 메모리: {result.deleted_count}개")
            return {"deleted_count": result.deleted_count}
            
        except Exception as e:
            logger.error(f"메모리 정리 오류: {str(e)}")
            return {"error": str(e)}

# 전역 메모리 시스템 인스턴스
memory_system = EORAMemorySystem() 