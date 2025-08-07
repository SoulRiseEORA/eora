"""
소주제 기반 메모리 저장기
- 최종 선택된 소주제를 포함하여 메모리를 MongoDB에 저장
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from pymongo import MongoClient
from datetime import datetime

mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["eora_memory"]
collection = db["memories"]

def save_memory_with_subtopic(user_msg, gpt_msg, emotion, belief_tags, event_score, final_subtopic, session_id):
    memory = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "topic": "대화",
        "sub_topic": final_subtopic,
        "user": user_msg,
        "gpt": gpt_msg,
        "emotion": emotion,
        "belief_tags": belief_tags,
        "event_score": round(event_score, 4),
        "resonance_score": estimate_resonance(event_score),
        "summary_prompt": gpt_msg[:120],
        "connections": [],
        "context_window_id": f"{session_id}-{datetime.now().strftime('%H%M')}",
        "last_used": None,
        "forgetting_score": 1.0,
        "search_path": [],
        "chain_id": f"{session_id}-{final_subtopic.replace(' ', '_')}"
    }
    collection.insert_one(memory)
    return memory

def estimate_resonance(score):
    return min(1.0, max(0.2, score * 1.15))