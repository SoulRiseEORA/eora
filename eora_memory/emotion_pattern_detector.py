"""
감정 반복 패턴 탐지기
- 일정 기간 내 특정 감정 반복 감지
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from pymongo import MongoClient
from datetime import datetime, timedelta
import pandas as pd

mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["aura_memory"]
collection = db["memory_atoms"]

def detect_repeated_emotions(days=30, threshold=3):
    """
    최근 days일 내 같은 감정이 threshold번 이상 반복되면 감지
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(days=days)

    memories = list(collection.find({"timestamp": {"$gte": cutoff.isoformat()}}, {"timestamp":1, "emotion_label":1}))
    if not memories:
        print("⚠️ 분석할 감정 데이터 없음")
        return

    df = pd.DataFrame(memories)
    counts = df["emotion_label"].value_counts()

    for emotion, count in counts.items():
        if count >= threshold:
            print(f"🚨 감정 반복 감지: {emotion} ({count}회)")

if __name__ == "__main__":
    detect_repeated_emotions()