"""
AURA 확장형 메모리 구조 및 연결 기반 회상 흐름 시스템
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId             # ←★ 추가: ObjectId 사용 위해

client = MongoClient("mongodb://localhost:27017")
db = client["eora_memory"]
collection = db["memories"]

# ---------------------------
# 저장 확장: 메모리 간 연결, 토픽 피라미드 포함
# ---------------------------
def save_extended_memory(user_msg, gpt_msg, emotion, belief_tags, event_score,
                         session_id, topic, sub_topic, related_ids=[]):
    memory = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "topic": topic,
        "sub_topic": sub_topic,
        "user": user_msg,
        "gpt": gpt_msg,
        "emotion": emotion,
        "belief_tags": belief_tags,
        "event_score": round(event_score, 4),
        "resonance_score": estimate_resonance(event_score),
        "summary_prompt": gpt_msg[:120],
        "connections": related_ids,
        "context_window_id": f"{session_id}-{datetime.now().strftime('%H%M')}",
        "last_used": None,
        "forgetting_score": 1.0,
        "search_path": [],
        "chain_id": f"{session_id}-{topic.replace(' ', '_')}"
    }
    collection.insert_one(memory)
    return memory

# ---------------------------
# 회상 흐름: 관련 기억 연쇄 검색
# ---------------------------
def recall_chain(start_topic, depth=3):
    current_set = list(collection.find({"topic": start_topic})
                                  .sort("timestamp", -1).limit(1))
    result_chain = []
    visited = set()

    while current_set and len(result_chain) < depth:
        current = current_set[0]
        if str(current["_id"]) in visited:
            break
        result_chain.append(current)
        visited.add(str(current["_id"]))
        conn_ids = current.get("connections", [])
        current_set = (list(collection.find(
                        {"_id": {"$in": [ObjectId(cid) for cid in conn_ids]}}))
                       if conn_ids else [])

    return result_chain

# ---------------------------
# 유틸: 공명 점수 추정
# ---------------------------
def estimate_resonance(score):
    return min(1.0, max(0.2, score * 1.15))
