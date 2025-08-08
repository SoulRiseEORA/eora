"""
감정 기반 기억 회상 모듈
- 특정 감정(label)로 저장된 기억만 불러오기
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from pymongo import MongoClient

mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["aura_memory"]
collection = db["memory_atoms"]

def recall_memories_by_emotion(target_emotion: str, limit=5):
    """
    특정 감정에 해당하는 기억을 최신 순으로 회상
    """
    memories = list(
        collection.find({"emotion_label": {"$regex": target_emotion}})
        .sort("timestamp", -1)
        .limit(limit)
    )
    return memories

if __name__ == "__main__":
    memories = recall_memories_by_emotion("불안")
    for memory in memories:
        print(f"🧠 [{memory['emotion_label']}] {memory['summary_prompt']}")