import os
import json
import asyncio
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple

import numpy as np
import faiss
from openai import OpenAI


def _ensure_dir(path: str) -> None:
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def _normalize_rows(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-12
    return matrix / norms


class EmbeddingClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small") -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "").strip()
        self.model = model
        self._client = OpenAI(api_key=self.api_key) if self.api_key else None
        self._cache: Dict[str, np.ndarray] = {}
        self._cache_order: List[str] = []
        self._cache_cap = 256

    def embed(self, texts: List[str]) -> np.ndarray:
        if not self._client:
            raise RuntimeError("OpenAI API 키가 필요합니다.")
        # 간단 LRU 캐시: 완전 일치 텍스트에 한함
        cached: List[np.ndarray] = []
        to_query: List[str] = []
        for t in texts:
            if t in self._cache:
                cached.append(self._cache[t])
            else:
                cached.append(None)  # placeholder
                to_query.append(t)
        if to_query:
            resp = self._client.embeddings.create(model=self.model, input=to_query)
            idx = 0
            for i, t in enumerate(texts):
                if cached[i] is None:
                    vec = np.array(resp.data[idx].embedding, dtype=np.float32)
                    self._cache[t] = vec
                    self._cache_order.append(t)
                    if len(self._cache_order) > self._cache_cap:
                        old = self._cache_order.pop(0)
                        self._cache.pop(old, None)
                    cached[i] = vec
                    idx += 1
        # 모두 numpy로 스택
        return np.vstack(cached)


@dataclass
class VectorRecord:
    vector_id: int
    metadata: Dict[str, Any]


class FaissVectorStore:
    """
    디스크 영속형 FAISS 코사인 유사도 인덱스. L2-normalized 후 Inner Product 사용.
    """

    def __init__(self, base_path: str, dimension: int = 1536) -> None:
        self.base_path = base_path
        self.index_path = f"{base_path}.index"
        self.meta_path = f"{base_path}.metadata.jsonl"
        self.dimension = dimension
        self._index = None  # type: Optional[faiss.Index]
        self._next_id = 0
        self._lock = asyncio.Lock()
        self._meta_map: Dict[int, Dict[str, Any]] = {}
        self._load_or_init()

    def _load_or_init(self) -> None:
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self._index = faiss.read_index(self.index_path)
            # 메타 맵 적재 (메모리 상주)
            self._meta_map.clear()
            try:
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            row = json.loads(line)
                            vid = int(row.get("id"))
                            self._meta_map[vid] = row.get("meta", {})
                        except Exception:
                            continue
            except FileNotFoundError:
                pass
            self._next_id = len(self._meta_map)
        else:
            # Inner Product with normalized vectors approximates cosine similarity
            self._index = faiss.IndexFlatIP(self.dimension)
            _ensure_dir(self.index_path)
            _ensure_dir(self.meta_path)

    def _count_metadata_lines(self) -> int:
        try:
            with open(self.meta_path, "r", encoding="utf-8") as f:
                return sum(1 for _ in f)
        except FileNotFoundError:
            return 0

    def _append_metadata(self, metadatas: List[Dict[str, Any]]) -> List[int]:
        assigned_ids: List[int] = []
        with open(self.meta_path, "a", encoding="utf-8") as f:
            for meta in metadatas:
                vector_id = self._next_id
                f.write(json.dumps({"id": vector_id, "meta": meta}, ensure_ascii=False) + "\n")
                assigned_ids.append(vector_id)
                self._next_id += 1
                # 메모리 맵 즉시 갱신
                self._meta_map[vector_id] = meta
        return assigned_ids

    async def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]], embedder: EmbeddingClient) -> List[int]:
        if not texts:
            return []
        if metadatas and len(metadatas) != len(texts):
            raise ValueError("metadatas 길이는 texts와 동일해야 합니다.")

        async with self._lock:
            vectors = await asyncio.to_thread(embedder.embed, texts)
            norm_vectors = _normalize_rows(vectors)
            self._index.add(norm_vectors)

            metas = metadatas or [{} for _ in texts]
            assigned_ids = await asyncio.to_thread(self._append_metadata, metas)
            await asyncio.to_thread(faiss.write_index, self._index, self.index_path)
            return assigned_ids

    async def search(self, query_text: str, top_k: int, embedder: EmbeddingClient) -> List[Tuple[int, float, Dict[str, Any]]]:
        if top_k <= 0:
            return []
        async with self._lock:
            if self._index is None or self._index.ntotal == 0:
                return []

            query_vec = await asyncio.to_thread(embedder.embed, [query_text])
            query_vec = _normalize_rows(query_vec)
            distances, indices = await asyncio.to_thread(self._index.search, query_vec, top_k)

            results: List[Tuple[int, float, Dict[str, Any]]] = []
            for rank, idx in enumerate(indices[0]):
                if idx == -1:
                    continue
                score = float(distances[0][rank])
                meta = self._meta_map.get(int(idx), {})
                # 메타정보가 없으면 최소한 id라도 포함
                if not meta:
                    meta = {"id": int(idx)}
                results.append((int(idx), score, meta))
            return results

