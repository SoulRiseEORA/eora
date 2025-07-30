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

class AuraMemorySystem:
    """아우라 메모리 시스템 클래스"""
    
    def __init__(self):
        """초기화"""
        self.is_initialized = False
        self.memory_db = None
        self.embeddings_model = None
        self.vector_index = None
        self.memory_collection = None
        
        # 메모리 기반 저장소 (DB 연결 실패 시 사용)
        self.memory_store = {}
        
        # 초기화 시도
        self._try_initialize()
    
    def _try_initialize(self) -> bool:
        """초기화 시도"""
        try:
            # MongoDB 연결 시도
            from database import db_manager
            
            if db_manager.is_connected:
                self.memory_db = db_manager.db
                self.memory_collection = db_manager.collections.get("memories")
                
                if self.memory_collection:
                    logger.info("✅ 아우라 메모리 시스템 - MongoDB 연결 성공")
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
            logger.error(f"❌ 아우라 메모리 시스템 초기화 실패: {e}")
            return False
    
    async def initialize(self) -> bool:
        """비동기 초기화"""
        if self.is_initialized:
            return True
        
        return self._try_initialize()
    
    async def store_interaction(self, user_id: str, message: str, response: str, 
                               memory_type: str = "conversation", importance: float = 0.5) -> str:
        """사용자 상호작용 저장"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # 메모리 데이터 생성
            memory_id = str(time.time())
            memory_data = {
                "user_id": user_id,
                "message": message,
                "response": response,
                "memory_type": memory_type,
                "importance": importance,
                "timestamp": datetime.now(),
                "tags": self._extract_tags(message)
            }
            
            # MongoDB에 저장
            if self.memory_collection:
                try:
                    result = await self.memory_collection.insert_one(memory_data)
                    memory_id = str(result.inserted_id)
                    logger.info(f"✅ 아우라 메모리 저장 완료: {memory_id}")
                except Exception as e:
                    logger.warning(f"⚠️ MongoDB 저장 실패, 메모리 저장소 사용: {e}")
                    self.memory_store[memory_id] = memory_data
            else:
                # 메모리 저장소에 저장
                self.memory_store[memory_id] = memory_data
                logger.info(f"✅ 메모리 저장소에 저장 완료: {memory_id}")
            
            # 임베딩 생성 및 저장 (비동기로 처리)
            if self.embeddings_model and self.vector_index:
                try:
                    # 메시지와 응답 결합하여 임베딩
                    text = f"{message} {response}"
                    embedding = self.embeddings_model.encode(text)
                    
                    # 벡터 인덱스에 추가
                    import numpy as np
                    self.vector_index.add(np.array([embedding]))
                    
                    # 임베딩 정보 저장
                    memory_data["embedding_id"] = self.vector_index.ntotal - 1
                    
                    logger.info(f"✅ 임베딩 생성 및 저장 완료: {memory_id}")
                except Exception as e:
                    logger.warning(f"⚠️ 임베딩 생성 실패: {e}")
            
            return memory_id
        except Exception as e:
            logger.error(f"❌ 아우라 메모리 저장 실패: {e}")
            return "error"
    
    async def recall(self, query: str, user_id: Optional[str] = None, 
                    limit: int = 5, recall_type: str = "normal") -> List[Dict]:
        """메모리 회상"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            results = []
            
            # 회상 타입에 따라 다른 방식 적용
            if recall_type == "semantic" and self.embeddings_model and self.vector_index:
                # 임베딩 기반 회상
                results = await self._semantic_recall(query, user_id, limit)
            elif recall_type == "keyword":
                # 키워드 기반 회상
                results = await self._keyword_recall(query, user_id, limit)
            elif recall_type == "window":
                # 시간 윈도우 기반 회상
                results = await self._window_recall(query, user_id, limit)
            elif recall_type == "comprehensive":
                # 종합 회상 (여러 방식 결합)
                results = await self._comprehensive_recall(query, user_id, limit)
            else:
                # 기본 회상 (키워드 기반)
                results = await self._keyword_recall(query, user_id, limit)
            
            logger.info(f"✅ 아우라 메모리 회상 완료: {len(results)}개 결과")
            return results
        except Exception as e:
            logger.error(f"❌ 아우라 메모리 회상 실패: {e}")
            return []
    
    async def _semantic_recall(self, query: str, user_id: Optional[str], limit: int) -> List[Dict]:
        """임베딩 기반 의미적 회상"""
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
                if self.memory_collection:
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
            if self.memory_collection:
                query_conditions = []
                
                # 사용자 필터
                if user_id:
                    query_conditions.append({"user_id": user_id})
                
                # 키워드 필터
                keyword_conditions = []
                for keyword in keywords:
                    keyword_conditions.append({"message": {"$regex": keyword, "$options": "i"}})
                    keyword_conditions.append({"response": {"$regex": keyword, "$options": "i"}})
                
                if keyword_conditions:
                    query_conditions.append({"$or": keyword_conditions})
                
                # 쿼리 실행
                query_filter = {"$and": query_conditions} if query_conditions else {}
                cursor = self.memory_collection.find(query_filter).sort("timestamp", -1).limit(limit)
                
                memories = await cursor.to_list(length=limit)
                return memories
            
            # 메모리 저장소에서 조회
            results = []
            for memory in self.memory_store.values():
                # 사용자 필터
                if user_id and memory.get("user_id") != user_id:
                    continue
                
                # 키워드 필터
                message = memory.get("message", "").lower()
                response = memory.get("response", "").lower()
                
                for keyword in keywords:
                    if keyword in message or keyword in response:
                        results.append(memory)
                        break
                
                if len(results) >= limit:
                    break
            
            # 최신순 정렬
            results.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
            return results[:limit]
        except Exception as e:
            logger.error(f"❌ 키워드 기반 회상 실패: {e}")
            return []
    
    async def _window_recall(self, query: str, user_id: Optional[str], limit: int) -> List[Dict]:
        """시간 윈도우 기반 회상"""
        try:
            # 최근 대화 가져오기
            if self.memory_collection:
                query_filter = {"user_id": user_id} if user_id else {}
                cursor = self.memory_collection.find(query_filter).sort("timestamp", -1).limit(limit)
                
                memories = await cursor.to_list(length=limit)
                return memories
            
            # 메모리 저장소에서 조회
            results = []
            for memory in self.memory_store.values():
                if user_id and memory.get("user_id") != user_id:
                    continue
                
                results.append(memory)
            
            # 최신순 정렬
            results.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
            return results[:limit]
        except Exception as e:
            logger.error(f"❌ 시간 윈도우 기반 회상 실패: {e}")
            return []
    
    async def _comprehensive_recall(self, query: str, user_id: Optional[str], limit: int) -> List[Dict]:
        """종합 회상 (여러 방식 결합)"""
        try:
            # 각 방식으로 회상
            semantic_results = await self._semantic_recall(query, user_id, limit // 2)
            keyword_results = await self._keyword_recall(query, user_id, limit // 2)
            
            # 중복 제거
            seen_ids = set()
            combined_results = []
            
            # 의미적 회상 결과 추가
            for memory in semantic_results:
                memory_id = str(memory.get("_id", ""))
                if memory_id not in seen_ids:
                    seen_ids.add(memory_id)
                    memory["recall_type"] = "semantic"
                    combined_results.append(memory)
            
            # 키워드 회상 결과 추가
            for memory in keyword_results:
                memory_id = str(memory.get("_id", ""))
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
            if self.memory_collection:
                return await self.memory_collection.count_documents({})
            return len(self.memory_store)
        except Exception as e:
            logger.error(f"❌ 메모리 개수 조회 실패: {e}")
            return 0
    
    async def count_user_memories(self, user_id: str) -> int:
        """사용자별 메모리 개수 조회"""
        try:
            if self.memory_collection:
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
            if self.memory_collection:
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
    
    def _extract_tags(self, text: str) -> List[str]:
        """텍스트에서 태그 추출"""
        # 간단한 태그 추출 로직
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
    
    def create_memory(self, user_id: str, session_id: str, message: str, response: str,
                      memory_type: str = "conversation", importance: float = 0.5) -> str:
        """동기 메모리 생성 (비동기 함수와 호환)"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.store_interaction(user_id, message, response, memory_type, importance)
        )
    
    def recall_memories(self, query: str, user_id: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """동기 메모리 회상 (비동기 함수와 호환)"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.recall(query, user_id, limit)) 