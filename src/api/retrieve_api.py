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

