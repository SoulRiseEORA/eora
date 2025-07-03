"""
AURA Memory Module (MongoDB 연동 버전, utils 경로 수정됨)
"""

from pymongo import MongoClient
from datetime import datetime
from EORA.utils import extract_tags, get_resonance_score, summarize_text

client = MongoClient("mongodb://localhost:27017")
db = client["EORA"]
collection = db["memory_atoms"]

def save_memory(user, gpt, eora="이오라 판단", context="일반", emotion="중립", value="보존", origin="이오라"):
    memory = {
        "summary": summarize_text(user),
        "user": user,
        "gpt": gpt,
        "eora": eora,
        "tags": extract_tags(user),
        "trigger_keywords": extract_tags(user),
        "next_goal": "다음 행동 예측",
        "origin": origin,
        "resonance_score": get_resonance_score(user),
        "importance": 8700,
        "connections": [],
        "context": context,
        "emotion": emotion,
        "value_tendency": value,
        "last_used": datetime.now().isoformat()
    }
    result = collection.insert_one(memory)
    print(f"🧠 저장됨 (MongoDB): ID {result.inserted_id}")

def recall_memory_by_trigger(user_input):
    keywords = extract_tags(user_input)
    result = collection.find({
        "$or": [
            {"tags": {"$in": keywords}},
            {"trigger_keywords": {"$in": keywords}}
        ]
    }).sort("resonance_score", -1).limit(3)

    memories = [doc["summary"] for doc in result]
    return memories