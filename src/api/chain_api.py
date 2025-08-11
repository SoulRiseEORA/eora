from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from aura_system.memory_chain import get_memory_chain
from aura_system.chain_vector_index import index_chain_summary, search_similar_chains


router = APIRouter(prefix="/api/chain", tags=["chain"]) 


class ChainCommitRequest(BaseModel):
    memories: List[Dict[str, Any]]  # [{"memory_id": ..., "content": ..., "score": ...}]
    metadata: Optional[Dict[str, Any]] = None
    prev_chain_id: Optional[str] = None


@router.post("/commit")
async def commit_chain(req: ChainCommitRequest):
    if not req.memories:
        raise HTTPException(status_code=400, detail="memories 필수")
    chain_mgr = await get_memory_chain()
    chain_id = await chain_mgr.create_chain(req.memories, req.metadata, req.prev_chain_id)
    if not chain_id:
        raise HTTPException(status_code=500, detail="체인 생성 실패")

    # 요약 인덱싱(비차단식)
    try:
        chain = await chain_mgr.get_chain(chain_id)
        summary = chain.get("summary", "") if chain else ""
        if summary:
            await index_chain_summary(chain_id, summary, (req.metadata or {}))
    except Exception:
        pass

    return {"chain_id": chain_id}


class ChainFindOrCreateRequest(BaseModel):
    text: str


@router.post("/find_or_create")
async def find_or_create(req: ChainFindOrCreateRequest):
    if not req.text:
        raise HTTPException(status_code=400, detail="text 필수")
    # 유사 체인 우선 검색
    try:
        sims = await search_similar_chains(req.text, top_k=1)
        if sims and sims[0].get("score", 0) >= 0.82:
            return {"chain_id": sims[0]["chain_id"], "matched": True, "score": sims[0]["score"]}
    except Exception:
        pass

    # 기존 함수로 폴백
    from aura_system.memory_chain import find_or_create_chain_id
    chain_id = await find_or_create_chain_id(req.text)
    return {"chain_id": chain_id, "matched": False}

