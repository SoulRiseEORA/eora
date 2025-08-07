"""
복합 감정 인코더
- 하나의 발화에 다중 감정 레이블 저장 지원
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from pymongo import MongoClient
import json

# Railway 최적화된 MongoDB 연결
try:
    from mongodb_config import get_optimized_mongodb_connection
except ImportError:
    def get_optimized_mongodb_connection():
        return MongoClient("mongodb://localhost:27017")

# ===== 추가된 3줄 =====
SRC_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
kw_json  = os.path.join(SRC_DIR, "emotion_system", "emotion_keywords_map.json")
# ======================

# 로컬 emotion_keywords_map.json 로드
with open(kw_json, "r", encoding="utf-8") as f:
    EMOTION_KEYWORDS = json.load(f)

mongo_client = get_optimized_mongodb_connection()
db = mongo_client["aura_memory"]
collection = db["memory_atoms"]

def extract_multiple_emotions(text: str):
    """
    텍스트에서 여러 감정을 감지하여 리스트 반환
    """
    detected = []
    for emotion, keywords in EMOTION_KEYWORDS.items():
        if any(k in text.lower() for k in keywords):
            detected.append(emotion)
    return list(set(detected))

def save_memory_with_multiple_emotions(memory_id):
    """
    기존 메모리에 복합 감정 추가
    """
    memory = collection.find_one({"_id": memory_id})
    if not memory:
        print("❌ 메모리 ID를 찾을 수 없습니다.")
        return

    text = memory.get("user_input", "") + " " + memory.get("gpt_response", "")
    emotions = extract_multiple_emotions(text)
    if not emotions:
        emotions = ["기타"]

    collection.update_one(
        {"_id": memory_id},
        {"$set": {"complex_emotions": emotions}}
    )
    print(f"✅ 복합 감정 저장 완료: {emotions}")

if __name__ == "__main__":
    from bson import ObjectId
    mem_id = input("메모리 ID 입력: ")
    save_memory_with_multiple_emotions(ObjectId(mem_id))
