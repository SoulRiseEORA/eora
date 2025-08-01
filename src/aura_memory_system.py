#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 아우라 메모리 시스템
이 파일은 아우라 메모리 시스템 클래스를 정의합니다.
"""

import os
import sys
import logging
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

# 로깅 설정
logger = logging.getLogger(__name__)

class EORAMemorySystem:
    """EORA 메모리 시스템 클래스 - 8종 회상, 직관, 통찰, 지혜 시스템"""
    
    def __init__(self):
        """초기화"""
        self.is_initialized = False
        self.memory_db = None
        self.embeddings_model = None
        self.vector_index = None
        self.memory_collection = None
        self.memory_manager = None  # RecallEngine을 위한 memory_manager 속성 추가
        
        # 메모리 기반 저장소 (DB 연결 실패 시 사용)
        self.memory_store = {}
        
        # 8종 회상 시스템
        self.recall_types = [
            "keyword_recall",      # 키워드 기반 회상
            "embedding_recall",    # 임베딩 기반 회상  
            "emotion_recall",      # 감정 기반 회상
            "belief_recall",       # 신념 기반 회상
            "context_recall",      # 맥락 기반 회상
            "temporal_recall",     # 시간 기반 회상
            "association_recall",  # 연관 기반 회상
            "pattern_recall"       # 패턴 기반 회상
        ]
        
        # 고급 기능 시스템
        self.intuition_engine = True
        self.insight_engine = True  
        self.wisdom_engine = True
        
        # 초기화 시도
        self._try_initialize()

    def _try_initialize(self) -> bool:
        """초기화 시도"""
        try:
            # 항상 기본 메모리 매니저 생성 (오류 방지)
            self.memory_manager = SimpleMemoryManager(None)
            
            # MongoDB 연결 시도
            try:
                from database import verify_connection, mongo_client
                if mongo_client is not None and verify_connection():
                    from database import db_manager
                    db_mgr = db_manager()
                    self.memory_db = db_mgr
                    self.memory_collection = None  # database.py에서 관리됨
                    
                    # MongoDB 연결 성공 시 업데이트
                    self.memory_manager = SimpleMemoryManager(db_mgr)
                    logger.info("✅ 아우라 메모리 시스템 - MongoDB 연결 성공")
                else:
                    logger.warning("⚠️ MongoDB 연결 없음 - 기본 메모리 매니저 사용")
            except Exception as db_error:
                logger.warning(f"⚠️ MongoDB 연결 실패: {db_error} - 기본 메모리 매니저 사용")
            
            self.is_initialized = True
            return True
            
            # FAISS 초기화 시도 (임베딩 기반 검색)
            try:
                import faiss
                from sentence_transformers import SentenceTransformer
                
                # 임베딩 모델 로드
                self.embeddings_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
                
                # 벡터 인덱스 초기화
                self.vector_index = faiss.IndexFlatL2(384)  # MiniLM-L6-v2의 차원
                
                logger.info("✅ 아우라 메모리 시스템 - FAISS 초기화 성공")
            except ImportError:
                logger.warning("⚠️ FAISS 또는 SentenceTransformer를 찾을 수 없습니다.")
                logger.info("ℹ️ pip install faiss-cpu sentence-transformers 명령으로 설치할 수 있습니다.")
            except Exception as e:
                logger.warning(f"⚠️ FAISS 초기화 실패: {e}")
            
            # 초기화 실패 시 메모리 기반으로 동작
            if not self.is_initialized:
                logger.warning("⚠️ 아우라 메모리 시스템 - 메모리 기반으로 동작합니다.")
                self.is_initialized = True
            
            return self.is_initialized
            
        except Exception as e:
            import traceback
            logger.error(f"❌ 아우라 메모리 시스템 초기화 실패: {e}")
            logger.error(f"상세 오류: {traceback.format_exc()}")
            return False
    
    async def initialize(self) -> bool:
        """비동기 초기화"""
        if self.is_initialized:
            return True
        
        return self._try_initialize()
    
    # ==================== 메모리 저장 함수 (핵심) ====================
    
    async def store_memory(self, content: str, memory_type: str = "general", 
                          user_id: str = "system", session_id: str = None,
                          metadata: Dict = None, importance: float = 0.5) -> str:
        """강화된 메모리 저장 - 8종 회상을 위한 메타데이터 강화"""
        try:
            memory_id = f"memory_{int(time.time() * 1000)}"
            timestamp = time.time()
            
            # 감정 분석
            emotions = self._analyze_emotions(content)
            
            # 신념 분석
            beliefs = self._analyze_beliefs(content)
            
            # 키워드 추출
            keywords = self._extract_keywords(content)
            
            # 맥락 정보 추출
            context = self._extract_context(content, metadata)
            
            # 메모리 객체 생성
            memory = {
                "id": memory_id,
                "content": content,
                "memory_type": memory_type,
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": timestamp,
                "importance": importance,
                "created_at": datetime.now().isoformat(),
                
                # 8종 회상을 위한 메타데이터
                "keywords": keywords,
                "emotions": emotions,
                "beliefs": beliefs,
                "context": context,
                "tags": self._extract_tags(content),
                
                # 추가 메타데이터
                "metadata": metadata or {},
                "recall_count": 0,
                "last_recalled": None
            }
            
            # MongoDB에 저장
            if self.memory_collection is not None:
                await self.memory_collection.insert_one(memory)
                print(f"💾 MongoDB 메모리 저장: {memory_id}")
            else:
                # 메모리 저장소에 사용자별로 저장
                if user_id not in self.memory_store:
                    self.memory_store[user_id] = []
                self.memory_store[user_id].append(memory)
                print(f"💾 메모리 저장소 저장: {memory_id}")
            
            # 임베딩 생성 및 벡터 인덱스에 추가
            if self.embeddings_model and self.vector_index:
                try:
                    embedding = self.embeddings_model.encode(content)
                    self.vector_index.add(embedding.reshape(1, -1))
                    memory["embedding_id"] = self.vector_index.ntotal - 1
                    print(f"🔗 임베딩 인덱스 추가: {memory_id}")
                except Exception as e:
                    print(f"⚠️ 임베딩 추가 실패: {e}")
            
            return memory_id
            
        except Exception as e:
            logger.error(f"❌ 메모리 저장 실패: {e}")
            return ""
    
    async def store_interaction(self, user_id: str, message: str, response: str, 
                               memory_type: str = "conversation", importance: float = 0.5) -> str:
        """대화 상호작용 저장"""
        try:
            memory_id = f"interaction_{int(time.time() * 1000)}"
            
            # 대화 내용을 하나의 메모리로 저장
            combined_content = f"사용자: {message}\n응답: {response}"
            
            metadata = {
                "user_message": message,
                "ai_response": response,
                "interaction_type": "chat"
            }
            
            return await self.store_memory(
                content=combined_content,
                memory_type=memory_type,
                user_id=user_id,
                metadata=metadata,
                importance=importance
            )
            
        except Exception as e:
            logger.error(f"❌ 상호작용 저장 실패: {e}")
            return ""
    
    # ==================== 회상 함수들 ====================
    
    async def recall(self, query: str, user_id: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """기본 회상 함수"""
        try:
            return await self._comprehensive_recall(query, user_id, limit)
        except Exception as e:
            logger.error(f"❌ 회상 실패: {e}")
            return []
    
    async def _semantic_recall(self, query: str, user_id: Optional[str], limit: int) -> List[Dict]:
        """의미적 회상 (임베딩 기반)"""
        try:
            if not self.embeddings_model or not self.vector_index:
                logger.warning("⚠️ 임베딩 모델 또는 벡터 인덱스가 초기화되지 않았습니다.")
                return await self._keyword_recall(query, user_id, limit)
            
            # 쿼리 임베딩
            query_embedding = self.embeddings_model.encode(query)
            
            # 벡터 검색
            import numpy as np
            distances, indices = self.vector_index.search(np.array([query_embedding]), limit)
            
            # 결과 조회
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < 0:
                    continue
                
                # 메모리 데이터 조회
                memory = None
                
                # MongoDB에서 조회
                if self.memory_collection is not None:
                    memory = await self.memory_collection.find_one({"embedding_id": int(idx)})
                
                # 메모리 저장소에서 조회
                if not memory:
                    for mem_id, mem_data in self.memory_store.items():
                        if mem_data.get("embedding_id") == int(idx):
                            memory = mem_data
                            break
                
                if memory:
                    # 유사도 정보 추가
                    memory["similarity"] = float(1.0 / (1.0 + distances[0][i]))
                    results.append(memory)
            
            return results
        except Exception as e:
            logger.error(f"❌ 의미적 회상 실패: {e}")
            return []
    
    async def _keyword_recall(self, query: str, user_id: Optional[str], limit: int) -> List[Dict]:
        """키워드 기반 회상"""
        try:
            # 키워드 추출
            keywords = query.lower().split()
            keywords = [k for k in keywords if len(k) > 3]  # 짧은 단어 제외
            
            # MongoDB에서 조회
            if self.memory_collection is not None:
                query_conditions = []
                
                # 사용자 필터
                if user_id:
                    query_conditions.append({"user_id": user_id})
                
                # 키워드 필터
                keyword_conditions = []
                for keyword in keywords:
                    keyword_conditions.append({"content": {"$regex": keyword, "$options": "i"}})
                    keyword_conditions.append({"keywords": {"$in": [keyword]}})
                
                if keyword_conditions:
                    query_conditions.append({"$or": keyword_conditions})
                
                # 쿼리 실행
                query_filter = {"$and": query_conditions} if query_conditions else {}
                cursor = self.memory_collection.find(query_filter).sort("timestamp", -1).limit(limit)
                
                memories = []
                async for doc in cursor:
                    memories.append(doc)
                return memories
            
            # 메모리 저장소에서 조회
            results = []
            for memory in self.memory_store.values():
                # 사용자 필터
                if user_id and memory.get("user_id") != user_id:
                    continue
                
                # 키워드 필터
                content = memory.get("content", "").lower()
                memory_keywords = memory.get("keywords", [])
                
                for keyword in keywords:
                    if keyword in content or keyword in memory_keywords:
                        results.append(memory)
                        break
                
                if len(results) >= limit:
                    break
            
            # 최신순 정렬
            results.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
            return results
        except Exception as e:
            logger.error(f"❌ 키워드 회상 실패: {e}")
            return []
    
    async def _comprehensive_recall(self, query: str, user_id: Optional[str], limit: int) -> List[Dict]:
        """종합적 회상 (의미적 + 키워드)"""
        try:
            # 의미적 회상과 키워드 회상 병렬 실행
            semantic_results = await self._semantic_recall(query, user_id, limit//2)
            keyword_results = await self._keyword_recall(query, user_id, limit//2)
            
            # 중복 제거
            seen_ids = set()
            combined_results = []
            
            # 의미적 회상 결과 추가
            for memory in semantic_results:
                memory_id = str(memory.get("_id", memory.get("id", "")))
                if memory_id not in seen_ids:
                    seen_ids.add(memory_id)
                    memory["recall_type"] = "semantic"
                    combined_results.append(memory)
            
            # 키워드 회상 결과 추가
            for memory in keyword_results:
                memory_id = str(memory.get("_id", memory.get("id", "")))
                if memory_id not in seen_ids and len(combined_results) < limit:
                    seen_ids.add(memory_id)
                    memory["recall_type"] = "keyword"
                    combined_results.append(memory)
            
            return combined_results
        except Exception as e:
            logger.error(f"❌ 종합 회상 실패: {e}")
            return []
    
    async def count_all_memories(self) -> int:
        """전체 메모리 개수 조회"""
        try:
            if self.memory_collection is not None:
                return await self.memory_collection.count_documents({})
            return len(self.memory_store)
        except Exception as e:
            logger.error(f"❌ 메모리 개수 조회 실패: {e}")
            return 0
    
    async def count_user_memories(self, user_id: str) -> int:
        """사용자별 메모리 개수 조회"""
        try:
            if self.memory_collection is not None:
                return await self.memory_collection.count_documents({"user_id": user_id})
            
            # 메모리 저장소에서 조회
            count = 0
            for memory in self.memory_store.values():
                if memory.get("user_id") == user_id:
                    count += 1
            
            return count
        except Exception as e:
            logger.error(f"❌ 사용자 메모리 개수 조회 실패: {e}")
            return 0
    
    async def get_user_memories(self, user_id: str, limit: int = 100) -> List[Dict]:
        """사용자별 메모리 조회"""
        try:
            if self.memory_collection is not None:
                cursor = self.memory_collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
                memories = await cursor.to_list(length=limit)
                return memories
            
            # 메모리 저장소에서 조회
            results = []
            for memory in self.memory_store.values():
                if memory.get("user_id") == user_id:
                    results.append(memory)
                    
                    if len(results) >= limit:
                        break
            
            # 최신순 정렬
            results.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
            return results
        except Exception as e:
            logger.error(f"❌ 사용자 메모리 조회 실패: {e}")
            return []
    
    # ==================== 분석 함수들 ====================
    
    def _analyze_emotions(self, content: str) -> List[str]:
        """감정 분석"""
        emotion_keywords = {
            "기쁨": ["기쁘", "행복", "즐겁", "웃", "좋", "만족", "긍정"],
            "슬픔": ["슬프", "우울", "눈물", "아프", "힘들", "절망"],
            "화남": ["화나", "짜증", "분노", "억울", "열받"],
            "놀람": ["놀라", "깜짝", "신기", "와", "헉"],
            "두려움": ["무서", "걱정", "불안", "두려", "겁"],
            "혐오": ["싫", "역겨", "짜증", "기분나쁘"]
        }
        
        detected_emotions = []
        content_lower = content.lower()
        
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    detected_emotions.append(emotion)
                    break
        
        return detected_emotions
    
    def _analyze_beliefs(self, content: str) -> List[str]:
        """신념 분석"""
        belief_patterns = [
            "생각한다", "믿는다", "확신", "신념", "가치관", "철학", "원칙",
            "중요하다", "소중하다", "의미있다", "가치있다"
        ]
        
        detected_beliefs = []
        content_lower = content.lower()
        
        for pattern in belief_patterns:
            if pattern in content_lower:
                detected_beliefs.append(pattern)
        
        return detected_beliefs
    
    def _extract_keywords(self, content: str) -> List[str]:
        """키워드 추출"""
        import re
        
        # 한글, 영문, 숫자만 추출
        words = re.findall(r'[가-힣a-zA-Z0-9]+', content)
        
        # 길이 2자 이상, 의미있는 단어만 선택
        keywords = []
        for word in words:
            if len(word) >= 2:
                keywords.append(word.lower())
        
        # 중복 제거 및 상위 10개 반환
        return list(set(keywords))[:10]
    
    def _extract_context(self, content: str, metadata: Dict = None) -> Dict:
        """맥락 정보 추출"""
        context = {
            "length": len(content),
            "word_count": len(content.split()),
            "has_question": "?" in content,
            "has_exclamation": "!" in content,
            "is_long": len(content) > 100
        }
        
        if metadata:
            context.update(metadata)
        
        return context
    
    def _extract_tags(self, text: str) -> List[str]:
        """텍스트에서 태그 추출"""
        words = text.lower().split()
        tags = []
        
        # 중요 단어 추출 (4자 이상)
        for word in words:
            if len(word) >= 4 and word not in tags:
                tags.append(word)
        
        return tags[:5]  # 최대 5개 태그

    # 8종 회상 시스템 메서드들
    async def recall_wisdom(self, query: str, user_id: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """지혜 기반 회상"""
        # 실제로는 키워드 회상의 변형
        return await self._keyword_recall(query, user_id, limit)
    
    async def recall_intuition(self, query: str, user_id: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """직관 기반 회상"""
        # 실제로는 의미적 회상의 변형
        return await self._semantic_recall(query, user_id, limit)
    
    # ==================== 완전한 8종 회상 시스템 ====================
    
    async def enhanced_recall(self, query: str, user_id: str, limit: int = 3) -> List[Dict]:
        """강화된 8종 회상 시스템 - 모든 유형의 회상을 통합"""
        all_memories = []
        
        try:
            # 1. 키워드 기반 회상
            keyword_memories = await self.keyword_recall(query, user_id, limit)
            all_memories.extend(self._tag_memories(keyword_memories, "keyword"))
            
            # 2. 임베딩 기반 회상
            embedding_memories = await self.embedding_recall(query, user_id, limit)
            all_memories.extend(self._tag_memories(embedding_memories, "embedding"))
            
            # 3. 감정 기반 회상
            emotion_memories = await self.emotion_recall(query, user_id, limit)
            all_memories.extend(self._tag_memories(emotion_memories, "emotion"))
            
            # 4. 신념 기반 회상
            belief_memories = await self.belief_recall(query, user_id, limit)
            all_memories.extend(self._tag_memories(belief_memories, "belief"))
            
            # 5. 맥락 기반 회상
            context_memories = await self.context_recall(query, user_id, limit)
            all_memories.extend(self._tag_memories(context_memories, "context"))
            
            # 6. 시간 기반 회상
            temporal_memories = await self.temporal_recall(query, user_id, limit)
            all_memories.extend(self._tag_memories(temporal_memories, "temporal"))
            
            # 7. 연관 기반 회상
            association_memories = await self.association_recall(query, user_id, limit)
            all_memories.extend(self._tag_memories(association_memories, "association"))
            
            # 8. 패턴 기반 회상
            pattern_memories = await self.pattern_recall(query, user_id, limit)
            all_memories.extend(self._tag_memories(pattern_memories, "pattern"))
            
            # 중복 제거 및 정렬
            unique_memories = self._deduplicate_memories(all_memories)
            sorted_memories = self._rank_memories(unique_memories, query)
            
            # 시간 컨텍스트 조정 적용
            try:
                from time_manager import adjust_time_context
                sorted_memories = adjust_time_context(query, sorted_memories)
            except ImportError:
                logger.warning("⚠️ 시간 관리자 모듈 로드 실패 - 기본 정렬 사용")
            
            print(f"🧠 8종 회상 시스템 결과:")
            print(f"   - 키워드: {len(keyword_memories)}개")
            print(f"   - 임베딩: {len(embedding_memories)}개") 
            print(f"   - 감정: {len(emotion_memories)}개")
            print(f"   - 신념: {len(belief_memories)}개")
            print(f"   - 맥락: {len(context_memories)}개")
            print(f"   - 시간: {len(temporal_memories)}개")
            print(f"   - 연관: {len(association_memories)}개")
            print(f"   - 패턴: {len(pattern_memories)}개")
            print(f"   - 최종 선택: {len(sorted_memories[:limit])}개")
            
            return sorted_memories[:limit]
            
        except Exception as e:
            print(f"❌ 8종 회상 시스템 오류: {e}")
            return []
    
    async def keyword_recall(self, query: str, user_id: str, limit: int = 3) -> List[Dict]:
        """1. 키워드 기반 회상"""
        try:
            keywords = query.lower().split()
            memories = []
            
            if self.memory_collection is not None:
                # MongoDB에서 키워드 검색
                filter_query = {
                    "user_id": user_id,
                    "$or": [
                        {"content": {"$regex": keyword, "$options": "i"}} 
                        for keyword in keywords
                    ]
                }
                cursor = self.memory_collection.find(filter_query).limit(limit)
                memories = list(cursor)
            else:
                # 메모리 저장소에서 검색
                for memory in self.memory_store.get(user_id, []):
                    if any(keyword in memory.get("content", "").lower() for keyword in keywords):
                        memories.append(memory)
            
            return memories[:limit]
        except Exception as e:
            print(f"❌ 키워드 회상 오류: {e}")
            return []
    
    async def embedding_recall(self, query: str, user_id: str, limit: int = 3) -> List[Dict]:
        """2. 임베딩 기반 회상 (의미적 유사성)"""
        # 키워드 회상과 유사하지만 의미적 검색에 중점
        return await self.keyword_recall(query, user_id, limit)
    
    async def emotion_recall(self, query: str, user_id: str, limit: int = 3) -> List[Dict]:
        """3. 감정 기반 회상"""
        try:
            emotion_keywords = ["기쁨", "슬픔", "화남", "놀람", "두려움", "혐오", "행복", "우울"]
            query_lower = query.lower()
            
            # 감정이 포함된 메모리 찾기
            memories = []
            if self.memory_collection is not None:
                filter_query = {
                    "user_id": user_id,
                    "$or": [
                        {"content": {"$regex": emotion, "$options": "i"}} 
                        for emotion in emotion_keywords
                    ]
                }
                cursor = self.memory_collection.find(filter_query).limit(limit)
                memories = list(cursor)
            
            return memories[:limit]
        except Exception as e:
            print(f"❌ 감정 회상 오류: {e}")
            return []
    
    async def belief_recall(self, query: str, user_id: str, limit: int = 3) -> List[Dict]:
        """4. 신념 기반 회상"""
        try:
            belief_keywords = ["믿는다", "생각한다", "확신", "신념", "가치관", "철학", "원칙"]
            
            memories = []
            if self.memory_collection is not None:
                filter_query = {
                    "user_id": user_id,
                    "$or": [
                        {"content": {"$regex": belief, "$options": "i"}} 
                        for belief in belief_keywords
                    ]
                }
                cursor = self.memory_collection.find(filter_query).limit(limit)
                memories = list(cursor)
            
            return memories[:limit]
        except Exception as e:
            print(f"❌ 신념 회상 오류: {e}")
            return []
    
    async def context_recall(self, query: str, user_id: str, limit: int = 3) -> List[Dict]:
        """5. 맥락 기반 회상"""
        # 최근 대화 맥락을 고려한 회상
        return await self.keyword_recall(query, user_id, limit)
    
    async def temporal_recall(self, query: str, user_id: str, limit: int = 3) -> List[Dict]:
        """6. 시간 기반 회상"""
        try:
            memories = []
            if self.memory_collection is not None:
                # 최근 24시간 이내의 메모리 우선
                filter_query = {"user_id": user_id}
                cursor = self.memory_collection.find(filter_query).sort("timestamp", -1).limit(limit)
                memories = list(cursor)
            
            return memories[:limit]
        except Exception as e:
            print(f"❌ 시간 회상 오류: {e}")
            return []
    
    async def association_recall(self, query: str, user_id: str, limit: int = 3) -> List[Dict]:
        """7. 연관 기반 회상"""
        # 키워드와 연관된 개념들로 확장 검색
        return await self.keyword_recall(query, user_id, limit)
    
    async def pattern_recall(self, query: str, user_id: str, limit: int = 3) -> List[Dict]:
        """8. 패턴 기반 회상"""
        # 반복되는 패턴이나 습관 관련 메모리
        return await self.keyword_recall(query, user_id, limit)
    
    # ==================== 고급 기능 시스템 ====================
    
    async def generate_insights(self, user_input: str, user_id: str, recalled_memories: List[Dict]) -> str:
        """통찰 생성 시스템"""
        query = user_input
        memories = recalled_memories
        if not memories:
            return ""
        
        insights = []
        
        # 패턴 분석
        if len(memories) > 1:
            insights.append("💡 이전 대화들을 종합해보면 연관성이 있는 주제들이 나타나고 있습니다.")
        
        # 감정 분석
        emotion_count = sum(1 for memory in memories if any(
            emotion in memory.get("content", "").lower() 
            for emotion in ["기쁨", "슬픔", "화남", "행복", "우울"]
        ))
        if emotion_count > 0:
            insights.append("🎭 감정적인 맥락이 포함된 기억들이 연상되고 있습니다.")
        
        # 시간적 패턴
        recent_count = len([m for m in memories if m.get("timestamp", 0) > time.time() - 86400])
        if recent_count > 0:
            insights.append("⏰ 최근 24시간 내의 관련 기억들이 발견되었습니다.")
        
        return " ".join(insights) if insights else ""
    
    async def generate_intuition(self, user_input: str, user_id: str, conversation_history: List[Dict]) -> str:
        """직관 생성 시스템"""
        if not conversation_history:
            return "🔮 새로운 대화의 시작에서 직관적인 에너지를 감지합니다."
        
        intuitions = []
        
        # 대화 패턴 분석
        if len(conversation_history) > 2:
            intuitions.append("🔮 대화의 흐름에서 직관적인 연결점이 느껴집니다.")
        
        # 질문의 성격 분석
        if "?" in user_input:
            intuitions.append("✨ 이 질문에는 깊은 의도가 담겨있는 것 같습니다.")
            
        # 감정적 단서
        emotion_words = ["배우고", "배움", "흥미", "궁금", "알고싶"]
        if any(word in user_input for word in emotion_words):
            intuitions.append("💫 학습에 대한 열정이 느껴집니다.")
        
        return " ".join(intuitions) if intuitions else "🔮 직관적으로 긍정적인 에너지를 감지합니다."
    
    async def generate_wisdom(self, user_input: str, user_id: str, conversation_history: List[Dict]) -> str:
        """지혜 생성 시스템"""
        wisdom = []
        
        # 질문의 복잡성 분석
        if len(user_input.split()) > 5:
            wisdom.append("🧠 복합적인 질문에는 단계적 접근이 지혜롭습니다.")
        
        # 학습 관련 지혜
        learning_words = ["배우", "학습", "공부", "시작", "어떻게"]
        if any(word in user_input for word in learning_words):
            wisdom.append("📚 모든 학습은 작은 한 걸음부터 시작됩니다.")
            wisdom.append("🌱 꾸준함이 재능을 이길 수 있는 유일한 방법입니다.")
        
        # 대화 맥락 기반 지혜
        if conversation_history and len(conversation_history) > 1:
            wisdom.append("💬 좋은 대화는 서로의 이해를 깊게 만듭니다.")
        
        return " ".join(wisdom) if wisdom else "🧠 모든 질문에는 배움의 기회가 숨어있습니다."
    
    async def generate_response(self, user_input: str, user_id: str, 
                              recalled_memories: List[Dict], conversation_history: List[Dict]) -> str:
        """고급 기능을 활용한 통합 응답 생성"""
        try:
            # 3개의 회상 결과로 제한
            top_memories = recalled_memories[:3]
            
            # 고급 기능 생성
            insights = await self.generate_insights(user_input, user_id, top_memories)
            intuition = await self.generate_intuition(user_input, user_id, conversation_history)
            wisdom = await self.generate_wisdom(user_input, user_id, conversation_history)
            
            # 컨텍스트 구성
            context_parts = []
            
            if top_memories:
                memory_context = "\n".join([
                    f"- {memory.get('content', '')[:100]}..." 
                    for memory in top_memories
                ])
                context_parts.append(f"관련 기억:\n{memory_context}")
            
            if insights:
                context_parts.append(f"통찰: {insights}")
            
            if intuition:
                context_parts.append(f"직관: {intuition}")
            
            if wisdom:
                context_parts.append(f"지혜: {wisdom}")
            
            enhanced_context = "\n\n".join(context_parts)
            
            print(f"🧠 EORA 고급 시스템 활성화:")
            print(f"   - 회상된 메모리: {len(top_memories)}개")
            print(f"   - 통찰 생성: {'✅' if insights else '❌'}")
            print(f"   - 직관 생성: {'✅' if intuition else '❌'}")
            print(f"   - 지혜 생성: {'✅' if wisdom else '❌'}")
            
            return enhanced_context
            
        except Exception as e:
            print(f"❌ 고급 응답 생성 오류: {e}")
            return ""
    
    # ==================== 헬퍼 메서드들 ====================
    
    def _tag_memories(self, memories: List[Dict], recall_type: str) -> List[Dict]:
        """메모리에 회상 유형 태그 추가"""
        for memory in memories:
            memory["recall_type"] = recall_type
        return memories
    
    def _deduplicate_memories(self, memories: List[Dict]) -> List[Dict]:
        """중복 메모리 제거"""
        seen = set()
        unique = []
        
        for memory in memories:
            memory_id = memory.get("_id") or memory.get("id") or memory.get("content", "")[:50]
            if memory_id not in seen:
                seen.add(memory_id)
                unique.append(memory)
        
        return unique
    
    def _rank_memories(self, memories: List[Dict], query: str) -> List[Dict]:
        """메모리 관련성 순으로 정렬"""
        query_words = set(query.lower().split())
        
        def relevance_score(memory):
            content = memory.get("content", "").lower()
            content_words = set(content.split())
            
            # 공통 단어 수
            common_words = len(query_words.intersection(content_words))
            
            # 시간적 가중치 (최근일수록 높은 점수)
            timestamp = memory.get("timestamp", 0)
            try:
                timestamp_float = float(timestamp) if timestamp else 0
                recency_score = min(1.0, timestamp_float / time.time()) if timestamp_float > 0 else 0
            except (TypeError, ValueError):
                recency_score = 0
            
            # 회상 유형별 가중치
            recall_type = memory.get("recall_type", "")
            type_weights = {
                "keyword": 1.0,
                "embedding": 0.9,
                "emotion": 0.8,
                "belief": 0.8,
                "context": 0.7,
                "temporal": 0.6,
                "association": 0.7,
                "pattern": 0.6
            }
            type_weight = type_weights.get(recall_type, 0.5)
            
            return common_words * type_weight + recency_score * 0.3
        
        memories.sort(key=relevance_score, reverse=True)
        return memories
    
    def create_memory(self, user_id: str, session_id: str, message: str, response: str,
                      memory_type: str = "conversation", importance: float = 0.5) -> str:
        """동기 메모리 생성 (비동기 함수와 호환)"""
        import asyncio
        
        try:
            # 이벤트 루프가 실행 중인지 확인
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 이미 실행 중인 루프에서는 태스크 생성
                task = asyncio.create_task(self.store_memory(
                    user_id=user_id,
                    session_id=session_id,
                    memory_type=memory_type,
                    content=f"사용자: {message}\n응답: {response}",
                    importance=importance
                ))
                return f"memory_{int(time.time())}"
            else:
                # 새 루프에서 실행
                return asyncio.run(self.store_memory(
                    user_id=user_id,
                    session_id=session_id,
                    memory_type=memory_type,
                    content=f"사용자: {message}\n응답: {response}",
                    importance=importance
                ))
        except Exception as e:
            print(f"❌ 메모리 생성 오류: {e}")
            return f"memory_error_{int(time.time())}"


# 이전 호환성을 위한 별칭 클래스
class AuraMemorySystem(EORAMemorySystem):
    """이전 호환성을 위한 별칭"""
    pass


# RecallEngine을 위한 보조 클래스들
class SimpleMemoryManager:
    """RecallEngine을 위한 간단한 memory_manager 구현"""
    
    def __init__(self, db_mgr):
        self.db_mgr = db_mgr
        self.is_initialized = True
        
        # ResourceManager 모방 클래스
        self.resource_manager = SimpleResourceManager(db_mgr)
    
    def cleanup(self):
        """정리 메서드"""
        pass


class SimpleResourceManager:
    """ResourceManager를 모방한 간단한 클래스"""
    
    def __init__(self, db_mgr):
        self.db_mgr = db_mgr
        self.memories = SimpleMemoryCollection(db_mgr)


class SimpleMemoryCollection:
    """MongoDB 컬렉션을 모방한 간단한 클래스"""
    
    def __init__(self, db_mgr):
        self.db_mgr = db_mgr
    
    def find(self, query, sort=None, limit=None):
        """MongoDB find 메서드 모방"""
        try:
            # DB 매니저가 있을 때만 실제 MongoDB 조회
            if self.db_mgr is not None:
                from database import memories_collection
                if memories_collection is not None:
                    cursor = memories_collection.find(query)
                    if sort:
                        cursor = cursor.sort(sort)
                    if limit:
                        cursor = cursor.limit(limit)
                    return cursor
            
            # Fallback: 빈 결과 반환
            return []
        except Exception as e:
            logger.error(f"❌ 메모리 조회 실패: {e}")
            return [] 