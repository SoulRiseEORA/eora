import os
import json
from typing import List, Dict, Any, Optional
from .schema import MemoryRecord


class JsonMemoryStore:
    """JSON 파일 기반 간단한 메모리 저장소 (MongoDB 대체 폴백)"""

    def __init__(self, path: str = "data/memories.jsonl") -> None:
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def write(self, record: MemoryRecord) -> None:
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")

    def read_all(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.path):
            return []
        out: List[Dict[str, Any]] = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except Exception:
                    continue
        return out

    def read_latest_versions(self) -> List[Dict[str, Any]]:
        all_docs = self.read_all()
        latest: Dict[str, Dict[str, Any]] = {}
        for doc in all_docs:
            key = doc.get("memory_id")
            if key not in latest or (doc.get("version", 0) or 0) > (latest[key].get("version", 0) or 0):
                latest[key] = doc
        return list(latest.values())

    # 편의를 위한 간단 조회 (edges 자동 생성 훅에서 사용)
    def read_last_by_user(self, user_id: str, limit: int = 30) -> List[Dict[str, Any]]:
        docs = [d for d in self.read_all() if d.get("user_id") == user_id]
        docs.sort(key=lambda d: (d.get("time") or {}).get("observed_at") or "", reverse=True)
        return docs[:limit]

