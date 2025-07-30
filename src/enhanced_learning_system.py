#!/usr/bin/env python3
"""
강화된 학습 시스템
- 카테고리별 학습 (영업시간, 상담내용, 심리상담, 명상 등)
- 500~1000자 청크 분할
- DB 반영 확인
- 상세 로그 및 디버그 정보
"""

import logging
import re
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from bson import ObjectId

logger = logging.getLogger(__name__)

class EnhancedLearningSystem:
    """강화된 학습 시스템"""
    
    def __init__(self, mongo_client=None):
        self.mongo_client = mongo_client
        self.db = None
        if mongo_client:
            self.db = mongo_client.get_database()
        
        # 카테고리별 키워드 정의
        self.category_keywords = {
            "영업시간": ["영업시간", "운영시간", "오픈시간", "마감시간", "휴무일", "평일", "주말", "공휴일"],
            "상담내용": ["상담", "문의", "고객서비스", "고객지원", "상담시간", "상담가능"],
            "심리상담": ["심리", "상담", "치료", "스트레스", "불안", "우울", "트라우마", "정신건강"],
            "명상": ["명상", "마음챙김", "호흡", "요가", "명상법", "명상방법", "마음수련"],
            "일반": ["일반", "기타", "기본"]
        }
    
    async def learn_document(self, content: str, filename: str, category: str = None) -> Dict[str, Any]:
        """문서 학습 처리"""
        logger.info("="*60)
        logger.info(f"📚 강화된 학습 시작: {filename}")
        logger.info(f"📋 카테고리: {category or '자동감지'}")
        logger.info("="*60)
        
        try:
            # 1단계: 카테고리 자동 감지
            if not category:
                category = self._detect_category(content)
                logger.info(f"🔍 자동 감지된 카테고리: {category}")
            
            # 2단계: 텍스트 청크 분할 (500~1000자)
            chunks = self._split_into_chunks(content)
            logger.info(f"✂️ 청크 분할 완료: {len(chunks)}개")
            
            # 3단계: DB 저장
            saved_memories = await self._save_to_database(chunks, filename, category)
            logger.info(f"💾 DB 저장 완료: {len(saved_memories)}개")
            
            # 4단계: DB 반영 확인
            verification_results = await self._verify_database_save(saved_memories, chunks)
            
            # 5단계: 결과 반환
            result = {
                "success": True,
                "filename": filename,
                "category": category,
                "total_chunks": len(chunks),
                "saved_memories": len(saved_memories),
                "db_verification": verification_results,
                "details": {
                    "original_length": len(content),
                    "avg_chunk_size": sum(len(c) for c in chunks) // len(chunks) if chunks else 0,
                    "min_chunk_size": min(len(c) for c in chunks) if chunks else 0,
                    "max_chunk_size": max(len(c) for c in chunks) if chunks else 0,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            logger.info("="*60)
            logger.info("🎉 강화된 학습 완료!")
            logger.info(f"📁 파일: {filename}")
            logger.info(f"🏷️ 카테고리: {category}")
            logger.info(f"✂️ 청크: {len(chunks)}개")
            logger.info(f"💾 저장: {len(saved_memories)}개")
            logger.info("="*60)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 강화된 학습 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }
    
    def _detect_category(self, content: str) -> str:
        """내용 기반 카테고리 자동 감지"""
        content_lower = content.lower()
        
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    logger.info(f"🔍 카테고리 감지: '{keyword}' -> {category}")
                    return category
        
        return "일반"
    
    def _split_into_chunks(self, content: str, min_size: int = 500, max_size: int = 1000) -> List[str]:
        """텍스트를 500~1000자 청크로 분할"""
        logger.info(f"✂️ 청크 분할 시작: {min_size}~{max_size}자")
        
        # 문장 단위로 분할
        sentences = re.split(r'[.!?。！？]', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence_with_period = sentence + "."
            
            # 최소 크기보다 작으면 계속 추가
            if len(current_chunk + sentence_with_period) < min_size:
                current_chunk += sentence_with_period
            # 최대 크기를 초과하면 현재 청크 저장하고 새 청크 시작
            elif len(current_chunk + sentence_with_period) > max_size:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                    logger.info(f"✅ 청크 {len(chunks)} 생성: {len(current_chunk)}자")
                current_chunk = sentence_with_period
            # 적절한 크기면 현재 청크에 추가
            else:
                current_chunk += sentence_with_period
        
        # 마지막 청크 처리
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
            logger.info(f"✅ 마지막 청크 {len(chunks)} 생성: {len(current_chunk)}자")
        
        return chunks
    
    async def _save_to_database(self, chunks: List[str], filename: str, category: str) -> List[str]:
        """청크를 DB에 저장"""
        logger.info(f"💾 DB 저장 시작: {len(chunks)}개 청크")
        
        saved_ids = []
        session_id = f"enhanced_learning_{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if not self.db:
            logger.error("❌ DB 연결 없음")
            return saved_ids
        
        try:
            memories_collection = self.db.memories
            
            for i, chunk in enumerate(chunks):
                memory_doc = {
                    "user_id": "admin",
                    "session_id": session_id,
                    "message": f"[{category} 학습자료 {i+1}/{len(chunks)}] {filename}",
                    "response": chunk,
                    "timestamp": datetime.now(),
                    "memory_type": "enhanced_learning",
                    "category": category,
                    "importance": 0.9,
                    "tags": [category, "학습자료", "강화학습", filename.split('.')[0]],
                    "source_file": filename,
                    "chunk_index": i,
                    "chunk_size": len(chunk)
                }
                
                result = memories_collection.insert_one(memory_doc)
                saved_ids.append(str(result.inserted_id))
                
                if (i+1) % 5 == 0:
                    logger.info(f"💾 저장 진행: {i+1}/{len(chunks)} 완료")
            
            logger.info(f"✅ DB 저장 완료: {len(saved_ids)}개")
            return saved_ids
            
        except Exception as e:
            logger.error(f"❌ DB 저장 실패: {e}")
            return saved_ids
    
    async def _verify_database_save(self, saved_ids: List[str], chunks: List[str]) -> List[str]:
        """DB 저장 확인"""
        logger.info("🔍 DB 저장 확인 시작...")
        verification_results = []
        
        if not self.db:
            verification_results.append("⚠️ DB 연결 없음")
            return verification_results
        
        try:
            memories_collection = self.db.memories
            
            # 저장된 메모리 조회
            stored_memories = list(memories_collection.find(
                {"_id": {"$in": [ObjectId(id) for id in saved_ids]}},
                {"_id": 1, "message": 1, "response": 1, "category": 1, "chunk_index": 1}
            ))
            
            logger.info(f"🔍 DB에서 조회된 메모리: {len(stored_memories)}개")
            
            if len(stored_memories) == len(chunks):
                verification_results.append("✅ 모든 청크 DB 저장 확인")
                logger.info("✅ DB 반영 성공: 모든 청크가 정상적으로 저장됨")
            else:
                verification_results.append(f"⚠️ 부분 저장: {len(stored_memories)}/{len(chunks)}개")
                logger.warning(f"⚠️ DB 반영 부분 실패: 예상 {len(chunks)}개, 실제 {len(stored_memories)}개")
            
            # 샘플 메모리 확인
            if stored_memories:
                sample = stored_memories[0]
                verification_results.append(f"✅ 샘플 메모리 확인: ID={sample['_id']}, 카테고리={sample.get('category', 'N/A')}")
                logger.info(f"📝 샘플 메모리: ID={sample['_id']}, 카테고리={sample.get('category', 'N/A')}")
            
            return verification_results
            
        except Exception as e:
            logger.error(f"❌ DB 확인 실패: {e}")
            verification_results.append(f"❌ DB 확인 실패: {e}")
            return verification_results
    
    async def get_learning_stats(self) -> Dict[str, Any]:
        """학습 통계 조회"""
        if not self.db:
            return {"error": "DB 연결 없음"}
        
        try:
            memories_collection = self.db.memories
            
            # 카테고리별 통계
            pipeline = [
                {"$match": {"memory_type": "enhanced_learning"}},
                {"$group": {
                    "_id": "$category",
                    "count": {"$sum": 1},
                    "total_size": {"$sum": {"$strLenCP": "$response"}}
                }}
            ]
            
            category_stats = list(memories_collection.aggregate(pipeline))
            
            # 전체 통계
            total_count = memories_collection.count_documents({"memory_type": "enhanced_learning"})
            
            return {
                "total_learning_memories": total_count,
                "category_stats": category_stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 학습 통계 조회 실패: {e}")
            return {"error": str(e)}

# 전역 인스턴스
enhanced_learning_system = None

def get_enhanced_learning_system(mongo_client=None):
    """강화된 학습 시스템 인스턴스 반환"""
    global enhanced_learning_system
    if enhanced_learning_system is None:
        enhanced_learning_system = EnhancedLearningSystem(mongo_client)
    return enhanced_learning_system 