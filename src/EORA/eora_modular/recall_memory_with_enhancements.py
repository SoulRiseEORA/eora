# 개선된 recall_memory_with_enhancements.py (전략 1~5 적용)

from aura_system.vector_store import embed_text_async
from aura_system.meta_store import get_all_atoms
from aura_system.memory_store import MemoryStore, get_memory_store
from EORA_Wisdom_Framework.EORAInsightManagerV2 import EORAInsightManagerV2
from datetime import datetime, timedelta
import numpy as np
import uuid
import logging
import asyncio

logger = logging.getLogger(__name__)

def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(vec1, vec2) / (norm1 * norm2))

class MemoryStore:
    def __init__(self):
        """초기화"""
        self.mongo_client = None
        self.mongo_collection = None
        self._init_mongodb()
        self.EMOTION_SIMILARITY_THRESHOLD = 0.7
        self.memory_store = {}
        self.initialized = False
        
    def _init_mongodb(self):
        """MongoDB 초기화"""
        try:
            from pymongo import MongoClient
            self.mongo_client = MongoClient('mongodb://localhost:27017/')
            self.mongo_collection = self.mongo_client['eora']['memories']
            logger.info("✅ MongoDB 연결 완료")
        except Exception as e:
            logger.error(f"❌ MongoDB 연결 실패: {str(e)}")
            print("❗ MongoDB 연결에 실패하여 회상 기능의 일부가 비활성화될 수 있습니다.") # 사용자에게 명확한 경고 출력
            self.mongo_client = None
            self.mongo_collection = None
        
    async def initialize(self):
        """메모리 매니저 초기화"""
        try:
            # 초기화 로직
            self.initialized = True
            return True
        except Exception as e:
            print(f"메모리 매니저 초기화 실패: {str(e)}")
            return False
            
    async def embed_text(self, text):
        """텍스트 임베딩 생성"""
        try:
            # 실제 임베딩 함수 호출로 변경
            return await embed_text_async(text)
        except Exception as e:
            print(f"임베딩 생성 실패: {str(e)}")
            return None
            
    async def recall_memory_with_enhancements(self, query: str, query_embedding=None, context: dict = None, max_results: int = 5) -> list:
        """
        향상된 2단계 회상 로직 (핵심 회상 + 직감 회상)
        1. 핵심 회상: 높은 임계값(0.75)으로 정확한 기억을 찾습니다.
        2. 직감 회상: 실패 시, 낮은 임계값(0.1)으로 가장 유사한 기억을 반드시 찾습니다.
        """
        if not query:
            return []

        if not self.initialized:
            print("메모리 매니저가 초기화되지 않았습니다.")
            return []

        try:
            if query_embedding is None:
                query_embedding = await self.embed_text(query)
            if not query_embedding:
                logger.warning("쿼리 임베딩 생성에 실패하여 회상을 중단합니다.")
                return []
            
            all_memories = list(self.mongo_collection.find({}))
            
            # --- 1단계: 핵심 회상 (높은 임계값) ---
            high_confidence_results = []
            for mem in all_memories:
                embedding = mem.get("metadata", {}).get("embedding")
                if embedding and isinstance(embedding, list):
                    similarity = cosine_similarity(query_embedding, embedding)
                    if similarity >= 0.75: # 높은 임계값
                        high_confidence_results.append({**mem, 'similarity': similarity})

            if high_confidence_results:
                logger.info(f"✅ [핵심 회상] {len(high_confidence_results)}개의 관련성 높은 기억을 찾았습니다.")
                high_confidence_results.sort(key=lambda x: x['similarity'], reverse=True)
                return high_confidence_results[:max_results]
            
            # --- 2단계: 직감 회상 (판단과 선택) ---
            logger.info("🤔 [직감 회상] 핵심 회상 실패. 가장 유사한 기억을 탐색하여 판단을 시작합니다...")
            all_scored_memories = []
            for mem in all_memories:
                embedding = mem.get("metadata", {}).get("embedding")
                if embedding and isinstance(embedding, list):
                    similarity = cosine_similarity(query_embedding, embedding)
                    if similarity >= 0.1: # 후보를 찾기 위한 최소 임계값
                        all_scored_memories.append({**mem, 'similarity': similarity})
            
            if all_scored_memories:
                all_scored_memories.sort(key=lambda x: x['similarity'], reverse=True)
                best_intuition_score = all_scored_memories[0]['similarity']

                # '직감'의 품질을 판단하는 임계값(0.25)
                INTUITION_QUALITY_THRESHOLD = 0.25
                if best_intuition_score >= INTUITION_QUALITY_THRESHOLD:
                    logger.info(f"✨ [직감 회상] 유사도 {best_intuition_score:.2f}의 기억을 포함하여 {len(all_scored_memories)}개를 회상합니다.")
                    return all_scored_memories[:max_results]
                else:
                    # 가장 유사한 기억조차도 품질이 낮으면 '기억 없음'을 선택
                    logger.info(f"🤔 [직감 선택] 가장 유사한 기억의 유사도({best_intuition_score:.2f})가 낮아 '기억 없음'으로 판단합니다.")
                    return []
            else:
                # 후보조차 없는 경우
                logger.info("🤷 회상 실패: 데이터베이스에 임베딩된 기억이 없거나 유사한 기억을 찾을 수 없습니다.")
                return []

        except Exception as e:
            logger.error(f"❌ 회상 중 심각한 오류 발생: {e}", exc_info=True)
            return []
            
    async def store_memory(self, content, metadata=None):
        """메모리 저장"""
        try:
            if not self.initialized:
                print("메모리 매니저가 초기화되지 않았습니다.")
                return False
                
            # 메모리 ID 생성
            memory_id = str(uuid.uuid4())
            
            # 임베딩 생성
            embedding = await self.embed_text(content)
            if not embedding:
                return False
                
            # 메모리 저장
            self.memory_store[memory_id] = {
                'content': content,
                'embedding': embedding,
                'metadata': metadata or {},
                'timestamp': datetime.now().isoformat()
            }
            
            return True
            
        except Exception as e:
            print(f"메모리 저장 중 오류: {str(e)}")
            return False
            
    async def clear_memory(self):
        """메모리 초기화"""
        try:
            self.memory_store.clear()
            return True
        except Exception as e:
            print(f"메모리 초기화 중 오류: {str(e)}")
            return False

def store_memory(content, metadata=None):
    """메모리 저장"""
    memory_store = get_memory_store()
    return memory_store.store_memory(content, metadata)

def recall_memory(query, context=None):
    """메모리 회상"""
    memory_store = get_memory_store()
    return memory_store.recall_memory_with_enhancements(query, context)

def clear_memory():
    """메모리 초기화"""
    memory_store = get_memory_store()
    return memory_store.clear_memory()

# ==============================================================================
# 독립 함수 - 실제 회상 로직의 진입점
# ==============================================================================
async def recall_memory_with_enhancements(query: str, query_embedding=None, context: dict = None, max_results: int = 5) -> list:
    """
    향상된 2단계 회상 로직 (핵심 회상 + 직감 회상)
    1. 핵심 회상: 높은 임계값(0.75)으로 정확한 기억을 찾습니다.
    2. 직감 회상: 실패 시, 낮은 임계값(0.1)으로 가장 유사한 기억을 반드시 찾습니다.
    """
    if not query:
        return []

    memory_store = get_memory_store()
    if not memory_store or not memory_store.mongo_collection:
        logger.warning("MongoDB가 연결되지 않아 회상을 건너뜁니다.")
        return []

    try:
        if query_embedding is None:
            query_embedding = await embed_text_async(query)
        if not query_embedding:
            logger.warning("쿼리 임베딩 생성에 실패하여 회상을 중단합니다.")
            return []
        
        all_memories = list(memory_store.mongo_collection.find({}))
        
        # --- 1단계: 핵심 회상 (높은 임계값) ---
        high_confidence_results = []
        for mem in all_memories:
            embedding = mem.get("metadata", {}).get("embedding")
            if embedding and isinstance(embedding, list):
                similarity = cosine_similarity(query_embedding, embedding)
                if similarity >= 0.75:
                    high_confidence_results.append({**mem, 'similarity': similarity})

        if high_confidence_results:
            high_confidence_results.sort(key=lambda x: x['similarity'], reverse=True)
            logger.info(f"✅ [핵심 회상] {len(high_confidence_results)}개의 관련성 높은 기억을 찾았습니다.")
            return high_confidence_results[:max_results]
            
        # --- 2단계: 직감 회상 (판단과 선택) ---
        logger.info("🤔 [직감 회상] 핵심 회상 실패. 가장 유사한 기억을 탐색하여 판단을 시작합니다...")
        all_scored_memories = []
        for mem in all_memories:
            embedding = mem.get("metadata", {}).get("embedding")
            if embedding and isinstance(embedding, list):
                similarity = cosine_similarity(query_embedding, embedding)
                if similarity >= 0.1: # 후보를 찾기 위한 최소 임계값
                    all_scored_memories.append({**mem, 'similarity': similarity})
        
        if all_scored_memories:
            all_scored_memories.sort(key=lambda x: x['similarity'], reverse=True)
            best_intuition_score = all_scored_memories[0]['similarity']

            # '직감'의 품질을 판단하는 임계값(0.25)
            INTUITION_QUALITY_THRESHOLD = 0.25
            if best_intuition_score >= INTUITION_QUALITY_THRESHOLD:
                logger.info(f"✨ [직감 회상] 유사도 {best_intuition_score:.2f}의 기억을 포함하여 {len(all_scored_memories)}개를 회상합니다.")
                return all_scored_memories[:max_results]
            else:
                # 가장 유사한 기억조차도 품질이 낮으면 '기억 없음'을 선택
                logger.info(f"🤔 [직감 선택] 가장 유사한 기억의 유사도({best_intuition_score:.2f})가 낮아 '기억 없음'으로 판단합니다.")
                return []
        else:
            # 후보조차 없는 경우
            logger.info("🤷 회상 실패: 데이터베이스에 임베딩된 기억이 없거나 유사한 기억을 찾을 수 없습니다.")
            return []

    except Exception as e:
        logger.error(f"❌ 회상 중 심각한 오류 발생: {e}", exc_info=True)
        return []