"""
MongoDB 기반 AURA 메모리 저장소 연동 모듈
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017")
db = client["eora_memory"]
collection = db["memories"]

def save_memory(user_msg, gpt_msg, emotion, belief_tags, event_score):
    """
    MongoDB에 메모리 저장
    """
    memory = {
        "timestamp": datetime.now().isoformat(),
        "user": user_msg,
        "gpt": gpt_msg,
        "emotion": emotion,
        "belief_tags": belief_tags,
        "event_score": round(event_score, 4),
        "summary_prompt": gpt_msg[:100],
        "topic": extract_topic(user_msg),
        "resonance_score": estimate_resonance(event_score),
    }
    collection.insert_one(memory)
    return memory

def extract_topic(text):
    """
    주제 추출 간이 로직 (향후 GPT 기반 강화 가능)
    """
    if "디자인" in text:
        return "디자인"
    elif "감정" in text:
        return "감정"
    return "일반"

def estimate_resonance(score):
    """
    공명 점수 추정 (event_score에 기반한 간이 계산)
    """
    return min(1.0, max(0.2, score * 1.15))

def load_recent_memories(limit=30):
    return list(collection.find().sort("timestamp", -1).limit(limit))