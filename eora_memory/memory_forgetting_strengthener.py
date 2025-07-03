"""
기억 망각-강화 알고리즘
- 오래되고 사용되지 않은 기억: 중요도 감소 (망각)
- 자주 사용되거나 중요한 기억: 중요도 증가 (강화)
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from pymongo import MongoClient
from datetime import datetime, timedelta

mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["aura_memory"]
collection = db["memory_atoms"]

def strengthen_or_forget_memories():
    now = datetime.utcnow()

    memories = list(collection.find({}))
    updated = 0

    for mem in memories:
        last_used = mem.get("last_used", mem.get("timestamp"))
        if isinstance(last_used, str):
            last_used = datetime.fromisoformat(last_used)

        days_passed = (now - last_used).days
        importance = mem.get("importance", 5000)

        # 오래된 기억: 점진적 중요도 감소 (망각)
        if days_passed > 30:
            importance *= 0.95

        # 최근 사용된 기억 또는 높은 공명도: 중요도 증가 (강화)
        elif days_passed <= 7 or mem.get("resonance_score", 0) > 85:
            importance *= 1.05

        importance = round(max(min(importance, 10000), 1000), 2)

        collection.update_one(
            {"_id": mem["_id"]},
            {"$set": {"importance": importance}}
        )
        updated += 1

    print(f"✅ {updated} 개 기억 강화/망각 점수 조정 완료")

if __name__ == "__main__":
    strengthen_or_forget_memories()