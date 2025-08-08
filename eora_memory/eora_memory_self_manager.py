"""
EORA 자율 기억 관리 모듈
- 기억 스스로 강화/망각 결정
- 중요도, 사용빈도, 공명점수 기반 판단
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from pymongo import MongoClient
from datetime import datetime, timedelta

mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["aura_memory"]
collection = db["memory_atoms"]

def eora_self_manage_memories():
    now = datetime.utcnow()
    memories = list(collection.find({}))
    updated = 0

    for mem in memories:
        importance = mem.get("importance", 5000)
        last_used = mem.get("last_used", mem.get("timestamp"))
        resonance = mem.get("resonance_score", 70)
        used_count = mem.get("used_count", 0)

        if isinstance(last_used, str):
            last_used = datetime.fromisoformat(last_used)

        days_since_use = (now - last_used).days

        # 강화 조건: 최근 사용 + 공명 높음 + 사용빈도 높음
        if days_since_use <= 7 and resonance >= 80 and used_count >= 3:
            importance *= 1.10  # 10% 강화

        # 망각 조건: 오래 사용 안됨 + 공명 낮음 + 사용빈도 낮음
        elif days_since_use >= 60 and resonance <= 50 and used_count == 0:
            importance *= 0.85  # 15% 망각

        importance = round(max(min(importance, 10000), 500), 2)

        collection.update_one(
            {"_id": mem["_id"]},
            {"$set": {"importance": importance}}
        )
        updated += 1

    print(f"✅ {updated} 개 기억의 강화/망각 처리가 완료되었습니다.")

if __name__ == "__main__":
    eora_self_manage_memories()