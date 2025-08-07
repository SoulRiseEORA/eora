import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from aura_system.vector_store import FaissIndex
from aura_system.meta_store import get_atoms_by_ids
import logging

logger = logging.getLogger(__name__)

async def retrieve(query_emb, query_tags=None, top_k=3):
    """벡터 검색 및 메모리 회상
    
    Args:
        query_emb (list): 쿼리 임베딩
        query_tags (list, optional): 검색할 태그 목록
        top_k (int): 반환할 결과 수
        
    Returns:
        list: 회상된 메모리 목록
    """
    try:
        faiss_index = FaissIndex()
        results = await faiss_index.search(query_emb, top_k)
        if not results:
            return []

        # results는 (거리, 메타데이터 ID) 튜플의 리스트
        ids = [item[1] for item in results]  # 메타데이터 ID만 추출
        atoms = await get_atoms_by_ids(ids)

        if query_tags:
            atoms = [a for a in atoms if any(tag in a.get("tags", []) for tag in query_tags)]

        atoms.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return atoms[:top_k]
    except Exception as e:
        logger.error(f"⚠️ 메모리 회상 실패: {str(e)}")
        return []

async def multi_stage_selector(query_emb, tags=None, top_k=3):
    """다단계 선택기
    
    Args:
        query_emb (list): 쿼리 임베딩
        tags (list, optional): 검색할 태그 목록
        top_k (int): 반환할 결과 수
        
    Returns:
        list: 회상된 메모리 목록
    """
    return await retrieve(query_emb, tags, top_k)