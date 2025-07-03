
import os
import json
from pymongo import MongoClient

class CobotFeatureDB:
    def __init__(self,
                 host="localhost",
                 port=27017,
                 db="eora_ai",
                 collection="cobot_features",
                 use_fallback_json=True,
                 fallback_json_path="configs/cobot_features.json"):
        self.use_json = use_fallback_json
        self.fallback_json_path = fallback_json_path
        try:
            self.client = MongoClient(host, port, serverSelectionTimeoutMS=200)
            self.db = self.client[db]
            self.col = self.db[collection]
            # 연결 테스트
            self.client.server_info()
        except Exception:
            self.client = None
            print("❗ MongoDB 연결 실패 → JSON 캐시 모드로 전환")

    def _load_json(self):
        if os.path.exists(self.fallback_json_path):
            with open(self.fallback_json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def get_all(self):
        if self.client:
            return list(self.col.find({}))
        return self._load_json()

    def get_top(self, limit=100):
        if self.client:
            return list(self.col.find().sort("중요도", -1).limit(limit))
        return self._load_json()[:limit]

    def find_by_keyword(self, keyword, limit=20):
        if self.client:
            return list(self.col.find({
                "$or": [
                    {"기능명": {"$regex": keyword, "$options": "i"}},
                    {"설명": {"$regex": keyword, "$options": "i"}}
                ]
            }).limit(limit))
        return [x for x in self._load_json() if keyword.lower() in x.get("기능명", "").lower() or keyword.lower() in x.get("설명", "").lower()][:limit]

    def get_by_ai_role(self, role_keyword="AI2_CODING", limit=20):
        if self.client:
            return list(self.col.find({
                "권장_AI": {"$regex": role_keyword, "$options": "i"}
            }).sort("중요도", -1).limit(limit))
        return [x for x in self._load_json() if role_keyword.lower() in x.get("권장_AI", "").lower()][:limit]
