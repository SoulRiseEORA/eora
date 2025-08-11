from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import time

from search.hybrid_search import hybrid_candidates, simple_rerank
from search.context_builder import summarize_with_sources


router = APIRouter(prefix="/api/retrieve", tags=["retrieve"])

# 간단 TTL 캐시 (짧은 수명)
_cache: Dict[str, Dict[str, Any]] = {}
_CACHE_TTL_SEC = 45

def _cache_get(key: str):
    item = _cache.get(key)
    if not item:
        return None
    if time.time() - item["ts"] > _CACHE_TTL_SEC:
        _cache.pop(key, None)
        return None
    return item["value"]

def _cache_set(key: str, value: Any):
    _cache[key] = {"ts": time.time(), "value": value}


class RetrieveRequest(BaseModel):
    query: str
    entities: List[str] = []
    top_k: int = 12


@router.post("/hybrid")
async def retrieve(req: RetrieveRequest):
    if not req.query:
        raise HTTPException(status_code=400, detail="query 필수")
    ck = f"hyb|{req.query}|{','.join(req.entities or [])}|{req.top_k}"
    cached = _cache_get(ck)
    if cached:
        return cached
    cands = await hybrid_candidates(req.query, req.entities)
    top = await simple_rerank(req.query, cands, top_n=req.top_k)
    context = summarize_with_sources(top)
    result = {"top": top, "context": context}
    _cache_set(ck, result)
    return result


# ===== 실험적: 하이브리드 회상 통합(점진 추가) =====
class HybridRequest(BaseModel):
    query: str
    user_id: str = "anonymous"
    top_k: int = 12


@router.post("/hybrid2")
async def retrieve_hybrid2(req: HybridRequest):
    if not req.query:
        raise HTTPException(status_code=400, detail="query 필수")
    try:
        ck = f"hyb2|{req.query}|{req.user_id}|{req.top_k}"
        cached = _cache_get(ck)
        if cached:
            return cached
        # 체인 요약 유사 체인 후보 + 벡터 후보를 병합(간이)
        from aura_system.chain_vector_index import search_similar_chains
        chains = await search_similar_chains(req.query, top_k=5)
        chain_docs = [
            {"id": c.get("chain_id"), "score": c.get("score", 0.0), "metadata": {"source_id": c.get("chain_id"), "source": "chain"}}
            for c in chains
        ]
        # 기존 벡터 병합
        vec_as_docs = [
            {"id": did, "score": float(sc), "metadata": meta}
            for (did, sc, meta) in await __vector_only(req.query, req.top_k)
        ]
        merged_docs = chain_docs + vec_as_docs
        # 간이 정렬
        merged_docs.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        result = {"top": merged_docs[: req.top_k]}
        _cache_set(ck, result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def __vector_only(query: str, top_k: int):
    from vectordb import FaissVectorStore, EmbeddingClient
    store = FaissVectorStore(base_path="data/faiss/eora_main", dimension=1536)
    embedder = EmbeddingClient()
    return await store.search(query, top_k, embedder)

