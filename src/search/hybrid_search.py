from __future__ import annotations

import asyncio
from typing import List, Dict, Any, Tuple

from vectordb import FaissVectorStore, EmbeddingClient


async def keyword_search(query: str, top_k: int = 50) -> List[Tuple[float, Dict[str, Any]]]:
    """
    간단한 키워드 검색(파일 기반) 폴백: 실제 BM25/ELK로 교체 가능.
    현재는 빈 리스트 반환해도 하이브리드 파이프라인은 동작.
    """
    return []


async def graph_expand(query_entities: List[str], hops: int = 2) -> List[Tuple[float, Dict[str, Any]]]:
    """
    그래프 확장(폴백). 추후 Neo4j/NetworkX 등으로 교체.
    """
    return []


async def vector_search(query: str, top_k: int = 50) -> List[Tuple[float, Dict[str, Any]]]:
    store = FaissVectorStore(base_path="data/faiss/eora_main", dimension=1536)
    embedder = EmbeddingClient()
    results = await store.search(query, top_k, embedder)
    # 변환: (score, doc)
    return [(score, {"id": vid, **meta}) for vid, score, meta in results]


def _dedup(items: List[Tuple[float, Dict[str, Any]]]) -> List[Tuple[float, Dict[str, Any]]]:
    seen = set()
    out: List[Tuple[float, Dict[str, Any]]] = []
    for score, doc in items:
        key = doc.get("id") or doc.get("memory_id") or str(doc)
        if key in seen:
            continue
        seen.add(key)
        out.append((score, doc))
    return out


async def hybrid_candidates(query: str, entities: List[str]) -> List[Tuple[float, Dict[str, Any]]]:
    vec_coro = vector_search(query, top_k=50)
    kw_coro = keyword_search(query, top_k=50)
    kg_coro = graph_expand(entities, hops=2)
    vec, kw, kg = await asyncio.gather(vec_coro, kw_coro, kg_coro)
    merged = vec + kw + kg
    return _dedup(merged)


def rerank_score(
    semantic: float,
    keyword: float,
    graph: float,
    recency: float,
    personalization: float,
    conflict_penalty: float,
) -> float:
    return (
        0.35 * semantic
        + 0.15 * keyword
        + 0.15 * graph
        + 0.20 * recency
        + 0.15 * personalization
        - 0.20 * conflict_penalty
    )


async def simple_rerank(query: str, cands: List[Tuple[float, Dict[str, Any]]], top_n: int = 12) -> List[Dict[str, Any]]:
    # 간이: 벡터 점수만 사용, 후속으로 Cross-encoder/시간/신뢰/개인화 치환 가능
    scored = []
    for score, doc in cands:
        s = rerank_score(semantic=score, keyword=0, graph=0, recency=doc.get("recency", 0.5), personalization=doc.get("personal", 0.5), conflict_penalty=0)
        scored.append((s, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for s, doc in scored[:top_n]]

