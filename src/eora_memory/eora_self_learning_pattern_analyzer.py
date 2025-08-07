"""
EORA 사용자 감정/신념 패턴 분석기
- MongoDB memory_atoms 기반
- 사용자별 감정 반복, 회복 속도, 신념 변화 분석
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from pymongo import MongoClient
from datetime import datetime, timedelta
import pandas as pd
from collections import defaultdict

mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["aura_memory"]
collection = db["memory_atoms"]

def analyze_user_patterns(user_id="default_user", days=30):
    cutoff = datetime.utcnow() - timedelta(days=days)
    memories = list(collection.find({"timestamp": {"$gte": cutoff.isoformat()}}))

    emotion_counts = defaultdict(int)
    belief_changes = 0
    recovery_delays = []

    for mem in memories:
        if mem.get("emotion_label"):
            emotion_counts[mem["emotion_label"]] += 1

        if mem.get("belief_detected") and mem.get("belief_reframed"):
            belief_changes += 1

        if mem.get("emotion_score", 0) <= 0.6 and mem.get("importance", 0) >= 8000:
            delay_days = (datetime.utcnow() - datetime.fromisoformat(mem["timestamp"])).days
            recovery_delays.append(delay_days)

    avg_delay = round(sum(recovery_delays) / len(recovery_delays), 2) if recovery_delays else 0

    print(f"📊 사용자 {user_id} 분석 결과:")
    print(f"  - 감정 출현: {dict(emotion_counts)}")
    print(f"  - 신념 리프레임 발생: {belief_changes}회")
    print(f"  - 평균 회복 지연일수: {avg_delay}일")

    return {
        "user_id": user_id,
        "emotion_pattern": dict(emotion_counts),
        "belief_change_count": belief_changes,
        "avg_recovery_delay": avg_delay
    }

if __name__ == "__main__":
    analyze_user_patterns()