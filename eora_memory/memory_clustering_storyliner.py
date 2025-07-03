"""
기억 클러스터링 + 스토리라인 생성기
- 감정/주제 기반으로 비슷한 기억들 묶기
- 하나의 스토리처럼 이어서 요약
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from pymongo import MongoClient
from eora_memory.recall_summarizer import summarize_memory_chain

mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["aura_memory"]
collection = db["memory_atoms"]

def cluster_memories_by_emotion_and_topic(target_emotion: str, target_topic: str, limit=10):
    """
    감정 + 주제 기준으로 기억 묶기
    """
    memories = list(
        collection.find({
            "emotion_label": {"$regex": target_emotion},
            "tags": {"$in": [target_topic]}
        }).sort("timestamp", -1).limit(limit)
    )
    return memories

def create_storyline_from_cluster(memories):
    """
    묶인 기억들을 하나의 이야기처럼 자연스럽게 요약
    """
    if not memories:
        return "📭 연결할 기억이 없습니다."

    return summarize_memory_chain(memories)

if __name__ == "__main__":
    target_emotion = "불안"
    target_topic = "도전"

    clustered = cluster_memories_by_emotion_and_topic(target_emotion, target_topic)
    story = create_storyline_from_cluster(clustered)

    print("🧠 생성된 기억 스토리라인:")
    print(story)