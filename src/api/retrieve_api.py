from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from search.hybrid_search import hybrid_candidates, simple_rerank
from search.context_builder import summarize_with_sources


router = APIRouter(prefix="/api/retrieve", tags=["retrieve"])


class RetrieveRequest(BaseModel):
    query: str
    entities: List[str] = []
    top_k: int = 12


@router.post("/hybrid")
async def retrieve(req: RetrieveRequest):
    if not req.query:
        raise HTTPException(status_code=400, detail="query 필수")
    cands = await hybrid_candidates(req.query, req.entities)
    top = await simple_rerank(req.query, cands, top_n=req.top_k)
    context = summarize_with_sources(top)
    return {"top": top, "context": context}


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
        # 체인 요약 유사 체인 후보 + 벡터 후보를 병합(간이)
        from aura_system.chain_vector_index import search_similar_chains
        chains = await search_similar_chains(req.query, top_k=5)
        chain_docs = [
            {"id": c.get("chain_id"), "score": c.get("score", 0.0), "metadata": {"source_id": c.get("chain_id"), "source": "chain"}}
            for c in chains
        ]
        base = await hybrid_candidates(req.query, [])
        merged = chain_docs + [(s, d) for s, d in []]  # placeholder for type consistency
        # 기존 벡터 병합
        vec_as_docs = [
            {"id": did, "score": float(sc), "metadata": meta}
            for (did, sc, meta) in await __vector_only(req.query, req.top_k)
        ]
        merged_docs = chain_docs + vec_as_docs
        # 간이 정렬
        merged_docs.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        return {"top": merged_docs[: req.top_k]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def __vector_only(query: str, top_k: int):
    from vectordb import FaissVectorStore, EmbeddingClient
    store = FaissVectorStore(base_path="data/faiss/eora_main", dimension=1536)
    embedder = EmbeddingClient()
    return await store.search(query, top_k, embedder)

