import os
import json
from typing import List, Dict, Any, Optional
from .schema import MemoryRecord


class JsonMemoryStore:
    """JSON 파일 기반 간단한 메모리 저장소 (MongoDB 대체 폴백)
    - 사용자별 디렉터리에 분산 저장: data/memories/{user_id}/memories.jsonl
    """

    def __init__(self, base_dir: str = "data/memories") -> None:
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _user_file(self, user_id: str) -> str:
        safe_user = (user_id or "anonymous").replace("/", "_").replace("\\", "_")
        user_dir = os.path.join(self.base_dir, safe_user)
        os.makedirs(user_dir, exist_ok=True)
        return os.path.join(user_dir, "memories.jsonl")

    def write(self, record: MemoryRecord) -> None:
        path = self._user_file(record.user_id)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")

    def read_all(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.base_dir):
            return []
        out: List[Dict[str, Any]] = []
        for user_id in os.listdir(self.base_dir):
            user_dir = os.path.join(self.base_dir, user_id)
            path = os.path.join(user_dir, "memories.jsonl")
            if not os.path.isfile(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            out.append(json.loads(line))
                        except Exception:
                            continue
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
        path = self._user_file(user_id)
        docs: List[Dict[str, Any]] = []
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            doc = json.loads(line)
                            if doc.get("user_id") == user_id:
                                docs.append(doc)
                        except Exception:
                            continue
            except Exception:
                pass
        docs.sort(key=lambda d: (d.get("time") or {}).get("observed_at") or "", reverse=True)
        return docs[:limit]

