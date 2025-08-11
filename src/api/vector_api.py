from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from vectordb import FaissVectorStore, EmbeddingClient


router = APIRouter(prefix="/api/vector", tags=["vector"])  # 기본 JSON 응답 사용


class UpsertRequest(BaseModel):
    texts: List[str]
    metadatas: Optional[List[Dict[str, Any]]] = None


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


# 단일 인스턴스 (프로세스 내)
_store: Optional[FaissVectorStore] = None
_embedder: Optional[EmbeddingClient] = None


def _get_store() -> FaissVectorStore:
    global _store
    if _store is None:
        _store = FaissVectorStore(base_path="data/faiss/eora_main", dimension=1536)
    return _store


def _get_embedder() -> EmbeddingClient:
    global _embedder
    if _embedder is None:
        _embedder = EmbeddingClient()
    return _embedder


@router.post("/upsert", response_class=JSONResponse)
async def upsert(req: UpsertRequest):
    if not req.texts:
        raise HTTPException(status_code=400, detail="texts 필수")
    store = _get_store()
    embedder = _get_embedder()
    ids = await store.add_texts(req.texts, req.metadatas, embedder)
    return {"inserted": len(ids), "ids": ids}


@router.post("/search", response_class=JSONResponse)
async def search(req: SearchRequest):
    if not req.query:
        raise HTTPException(status_code=400, detail="query 필수")
    store = _get_store()
    embedder = _get_embedder()
    results = await store.search(req.query, req.top_k, embedder)
    return {
        "results": [
            {"id": vid, "score": float(score), "metadata": meta} for vid, score, meta in results
        ]
    }

