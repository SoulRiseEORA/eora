#!/usr/bin/env python3
"""
향상된 학습 데이터 회상 시스템
- 강화된 학습 시스템과 호환
- 다양한 검색 전략 지원
- 사용자별 개인화된 결과
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
from bson import ObjectId
import re

logger = logging.getLogger(__name__)

class EnhancedRecallSystem:
    """향상된 학습 데이터 회상 시스템"""
    
    def __init__(self, mongo_client=None):
        self.mongo_client = mongo_client
        self.db = None
        if mongo_client:
            try:
                if hasattr(mongo_client, 'get_default_database'):
                    self.db = mongo_client.get_default_database()
                else:
                    self.db = mongo_client["eora_ai"]
            except Exception as e:
                logger.warning(f"기본 데이터베이스 설정 실패, eora_ai 사용: {e}")
                self.db = mongo_client["eora_ai"]
    
    def is_connected(self) -> bool:
        """연결 상태 확인"""
        if self.mongo_client is None or self.db is None:
            return False
        try:
            self.mongo_client.admin.command('ping')
            return True
        except:
            return False
    
    async def recall_learning_data(self, 
                                 query: str, 
                                 user_id: str = None,
                                 memory_type: str = None,
                                 category: str = None,
                                 filename: str = None,
                                 limit: int = 5) -> List[Dict]:
        """
        학습된 데이터 회상 (통합 검색)
        
        Args:
            query (str): 검색어
            user_id (str): 사용자 ID (개인화용)
            memory_type (str): 메모리 타입 ('enhanced_learning', 'document_chunk' 등)
            category (str): 카테고리 필터
            filename (str): 파일명 필터
            limit (int): 결과 제한
            
        Returns:
            List[Dict]: 회상된 학습 데이터 목록
        """
        if not self.is_connected():
            logger.warning("MongoDB 연결이 없어 학습 데이터 회상을 건너뜁니다")
            return []
        
        try:
            logger.info(f"🔍 학습 데이터 회상 시작 - 쿼리: '{query}', 사용자: {user_id}")
            
            all_results = []
            
            # 1. 강화된 학습 시스템 데이터 검색
            enhanced_results = await self._search_enhanced_learning(query, category, filename, limit)
            all_results.extend(enhanced_results)
            
            # 2. 문서 청크 데이터 검색
            chunk_results = await self._search_document_chunks(query, category, filename, limit)
            all_results.extend(chunk_results)
            
            # 3. 기타 학습 관련 데이터 검색
            other_results = await self._search_other_learning_data(query, memory_type, limit)
            all_results.extend(other_results)
            
            # 4. 중복 제거 및 관련성 점수 계산
            unique_results = self._remove_duplicates(all_results)
            scored_results = self._calculate_relevance_scores(unique_results, query)
            
            # 5. 결과 정렬 및 제한
            final_results = sorted(scored_results, key=lambda x: x.get('relevance_score', 0), reverse=True)[:limit]
            
            # 6. 결과 포맷팅
            formatted_results = self._format_results(final_results)
            
            logger.info(f"✅ 학습 데이터 회상 완료 - 결과: {len(formatted_results)}개")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ 학습 데이터 회상 오류: {e}")
            import traceback
            logger.error(f"상세 오류: {traceback.format_exc()}")
            return []
    
    async def _search_enhanced_learning(self, query: str, category: str, filename: str, limit: int) -> List[Dict]:
        """강화된 학습 시스템 데이터 검색"""
        try:
            search_query = {"memory_type": "enhanced_learning"}
            
            # 카테고리 필터
            if category:
                search_query["category"] = {"$regex": category, "$options": "i"}
            
            # 파일명 필터
            if filename:
                search_query["source_file"] = {"$regex": filename, "$options": "i"}
            
            # 텍스트 검색
            if query:
                text_conditions = [
                    {"response": {"$regex": query, "$options": "i"}},
                    {"message": {"$regex": query, "$options": "i"}},
                    {"tags": {"$in": [query]}},
                    {"category": {"$regex": query, "$options": "i"}},
                    {"source_file": {"$regex": query, "$options": "i"}}
                ]
                search_query = {"$and": [search_query, {"$or": text_conditions}]}
            
            cursor = self.db.memories.find(search_query).sort("timestamp", -1).limit(limit * 2)
            results = list(cursor)
            
            logger.info(f"📚 enhanced_learning 검색 결과: {len(results)}개")
            return results
            
        except Exception as e:
            logger.error(f"❌ enhanced_learning 검색 오류: {e}")
            return []
    
    async def _search_document_chunks(self, query: str, category: str, filename: str, limit: int) -> List[Dict]:
        """문서 청크 데이터 검색"""
        try:
            search_query = {"memory_type": "document_chunk"}
            
            # 관리자 공유 데이터 우선 검색
            admin_query = search_query.copy()
            admin_query["metadata.admin_shared"] = True
            admin_query["source"] = "file_learning"
            
            # 카테고리 필터
            if category:
                admin_query["metadata.category"] = {"$regex": category, "$options": "i"}
            
            # 파일명 필터
            if filename:
                admin_query["filename"] = {"$regex": filename, "$options": "i"}
            
            # 텍스트 검색
            if query:
                text_conditions = [
                    {"content": {"$regex": query, "$options": "i"}},
                    {"keywords": {"$in": [query]}},
                    {"topic": {"$regex": query, "$options": "i"}},
                    {"filename": {"$regex": query, "$options": "i"}},
                    {"metadata.filename": {"$regex": query, "$options": "i"}}
                ]
                admin_query = {"$and": [admin_query, {"$or": text_conditions}]}
            
            # 관리자 공유 데이터 검색
            cursor = self.db.memories.find(admin_query).sort("timestamp", -1).limit(limit)
            admin_results = list(cursor)
            
            results = admin_results
            
            # 결과가 부족하면 일반 document_chunk도 검색
            if len(results) < limit:
                remaining_limit = limit - len(results)
                fallback_query = {"memory_type": "document_chunk", "source": "file_learning"}
                
                if query:
                    fallback_query = {"$and": [fallback_query, {"$or": text_conditions}]}
                
                # 이미 찾은 결과 제외
                existing_ids = [result["_id"] for result in results]
                if existing_ids:
                    fallback_query["_id"] = {"$nin": existing_ids}
                
                cursor = self.db.memories.find(fallback_query).sort("timestamp", -1).limit(remaining_limit)
                fallback_results = list(cursor)
                results.extend(fallback_results)
            
            logger.info(f"📄 document_chunk 검색 결과: {len(results)}개")
            return results
            
        except Exception as e:
            logger.error(f"❌ document_chunk 검색 오류: {e}")
            return []
    
    async def _search_other_learning_data(self, query: str, memory_type: str, limit: int) -> List[Dict]:
        """기타 학습 관련 데이터 검색"""
        try:
            search_query = {}
            
            # 특정 메모리 타입이 지정된 경우
            if memory_type:
                search_query["memory_type"] = memory_type
            else:
                # 학습 관련 메모리 타입들
                learning_types = ["file_learning", "document_learning", "knowledge_base", "training_data"]
                search_query["memory_type"] = {"$in": learning_types}
            
            # 텍스트 검색
            if query:
                text_conditions = [
                    {"content": {"$regex": query, "$options": "i"}},
                    {"response": {"$regex": query, "$options": "i"}},
                    {"message": {"$regex": query, "$options": "i"}},
                    {"keywords": {"$in": [query]}},
                    {"topic": {"$regex": query, "$options": "i"}}
                ]
                search_query = {"$and": [search_query, {"$or": text_conditions}]}
            
            cursor = self.db.memories.find(search_query).sort("timestamp", -1).limit(limit)
            results = list(cursor)
            
            logger.info(f"📋 기타 학습 데이터 검색 결과: {len(results)}개")
            return results
            
        except Exception as e:
            logger.error(f"❌ 기타 학습 데이터 검색 오류: {e}")
            return []
    
    def _remove_duplicates(self, results: List[Dict]) -> List[Dict]:
        """중복 결과 제거"""
        seen_ids = set()
        unique_results = []
        
        for result in results:
            result_id = str(result.get("_id"))
            if result_id not in seen_ids:
                seen_ids.add(result_id)
                unique_results.append(result)
        
        return unique_results
    
    def _calculate_relevance_scores(self, results: List[Dict], query: str) -> List[Dict]:
        """관련성 점수 계산"""
        if not query:
            for result in results:
                result["relevance_score"] = 1.0
            return results
        
        query_lower = query.lower()
        query_words = query_lower.split()
        
        for result in results:
            score = 0
            
            # 내용에서 검색
            content = result.get("content", result.get("response", "")).lower()
            
            # 정확한 매치
            if query_lower in content:
                score += 5
            
            # 키워드 매치
            keywords = result.get("keywords", [])
            if any(query_lower in str(kw).lower() for kw in keywords):
                score += 3
            
            # 주제/카테고리 매치
            topic = result.get("topic", result.get("category", "")).lower()
            if query_lower in topic:
                score += 3
            
            # 파일명 매치
            filename = result.get("filename", result.get("source_file", "")).lower()
            if query_lower in filename:
                score += 2
            
            # 단어별 부분 매치
            for word in query_words:
                if len(word) > 2:  # 2글자 이상만
                    if word in content:
                        score += 1
                    if word in topic:
                        score += 0.5
                    if word in filename:
                        score += 0.5
            
            # 메모리 타입에 따른 가중치
            memory_type = result.get("memory_type", "")
            if memory_type == "enhanced_learning":
                score += 1
            elif memory_type == "document_chunk":
                score += 0.8
            
            # admin_shared 데이터에 가중치
            if result.get("metadata", {}).get("admin_shared"):
                score += 1
            
            result["relevance_score"] = score
        
        return results
    
    def _format_results(self, results: List[Dict]) -> List[Dict]:
        """결과 포맷팅"""
        formatted_results = []
        
        for result in results:
            formatted_result = {
                "_id": str(result.get("_id")),
                "content": result.get("content", result.get("response", "")),
                "memory_type": result.get("memory_type", ""),
                "relevance_score": result.get("relevance_score", 0),
                "timestamp": result.get("timestamp")
            }
            
            # 파일명
            if "filename" in result:
                formatted_result["filename"] = result["filename"]
            elif "source_file" in result:
                formatted_result["filename"] = result["source_file"]
            
            # 카테고리
            if "category" in result:
                formatted_result["category"] = result["category"]
            elif result.get("metadata", {}).get("category"):
                formatted_result["category"] = result["metadata"]["category"]
            
            # 키워드/태그
            if "keywords" in result:
                formatted_result["keywords"] = result["keywords"]
            elif "tags" in result:
                formatted_result["keywords"] = result["tags"]
            
            # 추가 메타데이터
            if "metadata" in result:
                formatted_result["metadata"] = result["metadata"]
            
            # 타임스탬프 포맷팅
            if formatted_result["timestamp"] and hasattr(formatted_result["timestamp"], "isoformat"):
                formatted_result["timestamp"] = formatted_result["timestamp"].isoformat()
            
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    async def get_learning_statistics(self) -> Dict[str, Any]:
        """학습 데이터 통계"""
        if not self.is_connected():
            return {"error": "MongoDB 연결 없음"}
        
        try:
            stats = {}
            
            # 전체 메모리 수
            stats["total_memories"] = self.db.memories.count_documents({})
            
            # 강화된 학습 메모리
            stats["enhanced_learning"] = self.db.memories.count_documents({"memory_type": "enhanced_learning"})
            
            # 문서 청크
            stats["document_chunks"] = self.db.memories.count_documents({"memory_type": "document_chunk"})
            
            # 카테고리별 통계
            pipeline = [
                {"$match": {"memory_type": {"$in": ["enhanced_learning", "document_chunk"]}}},
                {"$group": {
                    "_id": "$category",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}}
            ]
            category_stats = list(self.db.memories.aggregate(pipeline))
            stats["categories"] = category_stats
            
            # 파일별 통계
            pipeline = [
                {"$match": {"memory_type": {"$in": ["enhanced_learning", "document_chunk"]}}},
                {"$group": {
                    "_id": {"$ifNull": ["$filename", "$source_file"]},
                    "count": {"$sum": 1},
                    "latest": {"$max": "$timestamp"}
                }},
                {"$sort": {"latest": -1}}
            ]
            file_stats = list(self.db.memories.aggregate(pipeline))
            stats["files"] = file_stats[:10]  # 최근 10개만
            
            stats["timestamp"] = datetime.now().isoformat()
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ 학습 통계 조회 실패: {e}")
            return {"error": str(e)}

# 전역 인스턴스
enhanced_recall_system = None

def get_enhanced_recall_system(mongo_client=None):
    """향상된 회상 시스템 인스턴스 반환"""
    global enhanced_recall_system
    if enhanced_recall_system is None:
        enhanced_recall_system = EnhancedRecallSystem(mongo_client)
    return enhanced_recall_system