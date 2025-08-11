from __future__ import annotations

import asyncio
from typing import Dict, List, Any, Optional

from vectordb import FaissVectorStore, EmbeddingClient


_store: Optional[FaissVectorStore] = None
_embedder: Optional[EmbeddingClient] = None


def _get_store() -> FaissVectorStore:
    global _store
    if _store is None:
        _store = FaissVectorStore(base_path="data/faiss/chain_summaries", dimension=1536)
    return _store


def _get_embedder() -> EmbeddingClient:
    global _embedder
    if _embedder is None:
        _embedder = EmbeddingClient()
    return _embedder


async def index_chain_summary(chain_id: str, summary: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """체인 요약을 임베딩 인덱스에 추가/축적 저장합니다."""
    store = _get_store()
    embedder = _get_embedder()
    meta = {"chain_id": chain_id}
    if metadata:
        meta.update(metadata)
    await store.add_texts([summary], [meta], embedder)


async def search_similar_chains(text: str, top_k: int = 1) -> List[Dict[str, Any]]:
    """요약 텍스트로 유사한 체인을 검색합니다."""
    store = _get_store()
    embedder = _get_embedder()
    results = await store.search(text, top_k, embedder)
    # 결과 표준화
    return [
        {"chain_id": meta.get("chain_id"), "score": float(score), "metadata": meta}
        for vid, score, meta in results
        if meta.get("chain_id")
    ]

