#!/usr/bin/env python3
"""
강화된 회상 엔진
- 태그 기반 회상
- 임베딩 유사도 기반 회상  
- 시퀀스 기반 회상
- 3개 API에 회상 정보 전달
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from bson import ObjectId
import re

logger = logging.getLogger(__name__)

class EnhancedRecallEngine:
    """강화된 회상 엔진"""
    
    def __init__(self, mongo_client=None):
        self.mongo_client = mongo_client
        self.db = None
        if mongo_client:
            self.db = mongo_client.get_database()
    
    async def recall_memories(self, query: str, user_id: str = None, limit: int = 5) -> List[Dict]:
        """통합 회상 시스템"""
        all_memories = []
        
        try:
            # 1. 태그 기반 회상
            tag_memories = await self._recall_by_tags(query, user_id, limit//3)
            all_memories.extend(tag_memories)
            
            # 2. 키워드 기반 회상
            keyword_memories = await self._recall_by_keywords(query, user_id, limit//3)
            all_memories.extend(keyword_memories)
            
            # 3. 시퀀스 기반 회상
            sequence_memories = await self._recall_by_sequence(query, user_id, limit//3)
            all_memories.extend(sequence_memories)
            
            # 중복 제거 및 정렬
            unique_memories = self._remove_duplicates(all_memories)
            sorted_memories = self._sort_by_relevance(unique_memories, query)
            
            logger.info(f"🎯 강화된 회상 완료: {len(sorted_memories)}개")
            return sorted_memories[:limit]
            
        except Exception as e:
            logger.error(f"❌ 강화된 회상 실패: {e}")
            return []
    
    async def _recall_by_tags(self, query: str, user_id: str = None, limit: int = 3) -> List[Dict]:
        """태그 기반 회상"""
        try:
            if not self.db:
                return []
            
            # 쿼리에서 태그 추출
            tags = self._extract_tags(query)
            if not tags:
                return []
            
            # 태그 기반 검색
            search_conditions = []
            for tag in tags:
                search_conditions.extend([
                    {"tags": {"$in": [tag]}},
                    {"content": {"$regex": tag, "$options": "i"}},
                    {"message": {"$regex": tag, "$options": "i"}}
                ])
            
            if search_conditions:
                query_filter = {
                    "$or": search_conditions,
                    "user_id": user_id
                } if user_id else {"$or": search_conditions}
                
                memories = list(self.db.memories.find(query_filter).sort("timestamp", -1).limit(limit))
                logger.info(f"🏷️ 태그 기반 회상: {len(memories)}개")
                return memories
            
        except Exception as e:
            logger.error(f"❌ 태그 기반 회상 실패: {e}")
        
        return []
    
    async def _recall_by_keywords(self, query: str, user_id: str = None, limit: int = 3) -> List[Dict]:
        """키워드 기반 회상"""
        try:
            if not self.db:
                return []
            
            # 키워드 추출
            keywords = self._extract_keywords(query)
            if not keywords:
                return []
            
            # 키워드 기반 검색
            search_conditions = []
            for keyword in keywords:
                if len(keyword) > 1:
                    search_conditions.extend([
                        {"content": {"$regex": keyword, "$options": "i"}},
                        {"message": {"$regex": keyword, "$options": "i"}},
                        {"response": {"$regex": keyword, "$options": "i"}}
                    ])
            
            if search_conditions:
                query_filter = {
                    "$or": search_conditions,
                    "user_id": user_id
                } if user_id else {"$or": search_conditions}
                
                memories = list(self.db.memories.find(query_filter).sort("timestamp", -1).limit(limit))
                logger.info(f"🔍 키워드 기반 회상: {len(memories)}개")
                return memories
            
        except Exception as e:
            logger.error(f"❌ 키워드 기반 회상 실패: {e}")
        
        return []
    
    async def _recall_by_sequence(self, query: str, user_id: str = None, limit: int = 3) -> List[Dict]:
        """시퀀스 기반 회상"""
        try:
            if not self.db:
                return []
            
            # 시간 기반 검색 (최근 대화)
            recent_time = datetime.now() - timedelta(days=7)
            
            query_filter = {
                "timestamp": {"$gte": recent_time},
                "user_id": user_id
            } if user_id else {"timestamp": {"$gte": recent_time}}
            
            memories = list(self.db.memories.find(query_filter).sort("timestamp", -1).limit(limit))
            logger.info(f"⏰ 시퀀스 기반 회상: {len(memories)}개")
            return memories
            
        except Exception as e:
            logger.error(f"❌ 시퀀스 기반 회상 실패: {e}")
        
        return []
    
    def _extract_tags(self, query: str) -> List[str]:
        """쿼리에서 태그 추출"""
        # 간단한 태그 추출 로직
        tags = []
        words = query.split()
        
        # 특정 키워드를 태그로 인식
        tag_keywords = ["일정", "여행", "시험", "친구", "비", "날씨", "시간", "장소"]
        for word in words:
            if word in tag_keywords:
                tags.append(word)
        
        return tags
    
    def _extract_keywords(self, query: str) -> List[str]:
        """쿼리에서 키워드 추출"""
        # 2글자 이상의 단어를 키워드로 추출
        words = query.split()
        keywords = [word for word in words if len(word) >= 2]
        return keywords[:5]  # 최대 5개
    
    def _remove_duplicates(self, memories: List[Dict]) -> List[Dict]:
        """중복 제거"""
        seen = set()
        unique_memories = []
        
        for memory in memories:
            content = memory.get("content", "") or memory.get("message", "")
            if content and content not in seen:
                seen.add(content)
                unique_memories.append(memory)
        
        return unique_memories
    
    def _sort_by_relevance(self, memories: List[Dict], query: str) -> List[Dict]:
        """관련성 순으로 정렬"""
        def relevance_score(memory):
            content = memory.get("content", "") or memory.get("message", "")
            score = 0
            
            # 키워드 매칭 점수
            query_words = set(query.split())
            content_words = set(content.split())
            overlap = len(query_words.intersection(content_words))
            score += overlap * 10
            
            # 최신성 점수
            timestamp = memory.get("timestamp")
            if timestamp:
                if isinstance(timestamp, str):
                    try:
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except:
                        timestamp = datetime.now()
                
                days_old = (datetime.now() - timestamp).days
                score += max(0, 30 - days_old)  # 최대 30점
            
            return score
        
        return sorted(memories, key=relevance_score, reverse=True)

# 전역 인스턴스
enhanced_recall_engine = None

def get_enhanced_recall_engine(mongo_client=None):
    """강화된 회상 엔진 인스턴스 반환"""
    global enhanced_recall_engine
    if enhanced_recall_engine is None:
        enhanced_recall_engine = EnhancedRecallEngine(mongo_client)
    return enhanced_recall_engine 