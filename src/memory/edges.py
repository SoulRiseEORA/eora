from __future__ import annotations

import os
import json
from typing import List, Dict, Any, Tuple, Optional, DefaultDict
from collections import defaultdict
from datetime import datetime, timedelta
import math

from vectordb import EmbeddingClient


def _ensure_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


class EdgeStore:
    def __init__(self, edges_path: str = "data/memory_edges.jsonl", conn_map_path: str = "data/memory_connections.json") -> None:
        self.edges_path = edges_path
        self.conn_map_path = conn_map_path
        _ensure_dir(self.edges_path)
        _ensure_dir(self.conn_map_path)

    def add_edge(self, src: str, dst: str, rel: str, strength: float) -> None:
        if not src or not dst or src == dst:
            return
        edge = {
            "src": src,
            "dst": dst,
            "rel": rel,
            "strength": float(strength),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        with open(self.edges_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(edge, ensure_ascii=False) + "\n")

        # connection map 업데이트
        conn_map: Dict[str, List[Dict[str, Any]]] = {}
        if os.path.exists(self.conn_map_path):
            try:
                with open(self.conn_map_path, "r", encoding="utf-8") as f:
                    conn_map = json.load(f)
            except Exception:
                conn_map = {}
        conn_map.setdefault(src, []).append({"dst": dst, "rel": rel, "strength": float(strength)})
        try:
            with open(self.conn_map_path, "w", encoding="utf-8") as f:
                json.dump(conn_map, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


def _parse_time_iso(iso_str: Optional[str]) -> Optional[datetime]:
    if not iso_str:
        return None
    try:
        # tolerate 'Z'
        if iso_str.endswith("Z"):
            iso_str = iso_str[:-1]
        return datetime.fromisoformat(iso_str)
    except Exception:
        return None


def _group_by_subtopic(memories: List[Dict[str, Any]]) -> DefaultDict[str, List[Dict[str, Any]]]:
    groups: DefaultDict[str, List[Dict[str, Any]]] = defaultdict(list)
    for m in memories:
        sub = (
            m.get("sub_topic")
            or (m.get("source") or {}).get("sub_topic")
            or (m.get("metadata") or {}).get("sub_topic")
        )
        if sub:
            groups[str(sub)].append(m)
    return groups


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    if len(a) != len(b):
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na <= 0 or nb <= 0:
        return 0.0
    return dot / math.sqrt(na * nb)


async def auto_connect(memories: List[Dict[str, Any]], edge_store: Optional[EdgeStore] = None, window_hours: int = 2, sim_top_k: int = 2, sim_threshold: float = 0.85) -> None:
    """
    - 동일 소주제: 같은 sub_topic 그룹 내에서 시간 순 연결(완전 연결 대신 순차 연결)
    - 시간 인접: Δt <= window_hours 이웃끼리 연결
    - 임베딩 유사: text 기반 cosine top-k 연결
    결과는 edges.jsonl 및 connections 맵에 반영
    """
    if not memories:
        return
    edge_store = edge_store or EdgeStore()

    # 1) 동일 소주제: 그룹별 시간순 정렬 후 인접 연결
    groups = _group_by_subtopic(memories)
    for sub, items in groups.items():
        items_sorted = sorted(
            items,
            key=lambda m: _parse_time_iso(((m.get("time") or {}).get("observed_at"))) or datetime.min,
        )
        for prev, nxt in zip(items_sorted, items_sorted[1:]):
            src = prev.get("memory_id") or prev.get("_id")
            dst = nxt.get("memory_id") or nxt.get("_id")
            if src and dst:
                edge_store.add_edge(src, dst, rel="same_subtopic", strength=0.8)

    # 2) 시간 인접: 전체를 시간순으로 세워 이웃끼리 연결(Δt 제한)
    all_sorted = sorted(
        memories,
        key=lambda m: _parse_time_iso(((m.get("time") or {}).get("observed_at"))) or datetime.min,
    )
    for prev, nxt in zip(all_sorted, all_sorted[1:]):
        t1 = _parse_time_iso(((prev.get("time") or {}).get("observed_at")))
        t2 = _parse_time_iso(((nxt.get("time") or {}).get("observed_at")))
        if t1 and t2 and (t2 - t1) <= timedelta(hours=window_hours):
            src = prev.get("memory_id") or prev.get("_id")
            dst = nxt.get("memory_id") or nxt.get("_id")
            if src and dst:
                edge_store.add_edge(src, dst, rel="near_time", strength=0.6)

    # 3) 임베딩 유사 top-k: text 필드 사용, 없으면 content 사용
    texts: List[str] = []
    ids: List[str] = []
    for m in memories:
        text = m.get("text") or m.get("content") or ""
        mid = m.get("memory_id") or m.get("_id")
        if mid and text:
            ids.append(str(mid))
            texts.append(str(text))

    if len(texts) >= 2:
        embedder = EmbeddingClient()
        vectors = embedder.embed(texts)
        # cosine 상위 k 연결
        for i in range(len(ids)):
            sims: List[Tuple[float, int]] = []
            for j in range(len(ids)):
                if i == j:
                    continue
                s = _cosine(vectors[i].tolist(), vectors[j].tolist())
                sims.append((s, j))
            sims.sort(key=lambda x: x[0], reverse=True)
            for s, j in sims[:sim_top_k]:
                if s >= sim_threshold:
                    edge_store.add_edge(ids[i], ids[j], rel="high_sim", strength=float(s))


async def auto_connect_for_user(mem_store, user_id: str, consider: int = 30) -> None:
    """사용자의 최근 메모리 일부를 가져와 자동 연결 수행.
    mem_store는 read_last_by_user(user_id, limit) 메서드를 제공해야 함.
    """
    try:
        recents = mem_store.read_last_by_user(user_id, limit=consider)
        if recents:
            await auto_connect(recents)
    except Exception:
        # 연결 실패는 무시(주 서비스 흐름 방해 X)
        pass

