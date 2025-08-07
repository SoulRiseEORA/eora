"""
개인화 망각/강화 통합 모듈
- 사용자 감정/신념 패턴에 따른 기억 관리 정책 적용
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from pymongo import MongoClient
from datetime import datetime
from eora_memory.eora_personal_memory_policy import get_user_memory_policy

mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["aura_memory"]
collection = db["memory_atoms"]

def personalized_memory_update(user_id="default_user"):
    now = datetime.utcnow()
    policy = get_user_memory_policy(user_id)
    forget_days = policy["forget_threshold"]
    strengthen_factor = policy["strengthen_threshold"]
    min_imp, max_imp = policy["importance_range"]

    memories = list(collection.find({}))
    updated = 0

    for mem in memories:
        last_used = mem.get("last_used", mem.get("timestamp"))
        if isinstance(last_used, str):
            last_used = datetime.fromisoformat(last_used)

        importance = mem.get("importance", 5000)
        resonance = mem.get("resonance_score", 70)
        used_count = mem.get("used_count", 0)

        days_passed = (now - last_used).days

        # 강화 조건
        if days_passed <= 7 and resonance >= 85 and used_count >= 3:
            importance *= (1 + strengthen_factor)

        # 망각 조건
        elif days_passed >= forget_days and resonance < 50 and used_count == 0:
            importance *= 0.85  # 고정 망각 비율

        # 범위 클리핑
        importance = round(max(min(importance, max_imp), min_imp), 2)

        collection.update_one(
            {"_id": mem["_id"]},
            {"$set": {"importance": importance}}
        )
        updated += 1

    print(f"✅ {updated}개 기억이 사용자 맞춤 정책에 따라 강화/망각되었습니다.")

if __name__ == "__main__":
    personalized_memory_update()