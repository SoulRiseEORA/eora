import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from emotion_system.emotion_core import EmotionCore, get_emotion_core
from belief_memory_engine.belief_filter import is_forbidden, is_preferred

from pymongo import MongoClient
import redis

CONFIG_PATH = Path(__file__).parent.parent / "config" / "aura_config.json"
MEMORY_JSON_PATH = Path(__file__).parent.parent / "memory" / "memory_db.json"

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"storage": "json"}

def load_memory_db():
    config = load_config()
    storage = config.get("storage", "json")

    if storage == "mongo":
        client = MongoClient("mongodb://localhost:27017")
        db = client["eora"]
        return list(db["memory_atoms"].find())
    elif storage == "redis":
        r = redis.Redis()
        keys = r.keys("memory:*")
        return [json.loads(r.get(k)) for k in keys]
    else:
        try:
            with open(MEMORY_JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

def multi_stage_selector(user_input_tags, top_k=3):
    db = load_memory_db()
    results = []

    for memory in db:
        score = 0
        if is_forbidden(memory):
            continue

        tags = memory.get("tags", [])
        imp = memory.get("importance", 0)
        res = memory.get("resonance_score", 0)
        emo_score = emotion_match_score(tags)
        pref_bonus = 200 if is_preferred(memory) else 0

        score += imp * 0.3 + res * 0.3 + emo_score * 100 * 0.3 + pref_bonus
        results.append((score, memory))

    results.sort(reverse=True, key=lambda x: x[0])
    return [mem for _, mem in results[:top_k]]

def format_memories(memories):
    lines = ["\n📌 회상된 기억:"]
    for m in memories:
        lines.append(f"🕓 {m.get('timestamp')} — {m.get('summary_prompt')}")
    return "\n".join(lines)

def calculate_emotion_match(emotion1: Dict[str, Any], emotion2: Dict[str, Any]) -> float:
    """두 감정 간의 매칭 점수 계산"""
    try:
        emotion_core = get_emotion_core()
        result = emotion_core.process_emotion({
            'emotion1': emotion1,
            'emotion2': emotion2,
            'type': 'match_score'
        })
        return result.get('match_score', 0.0)
    except Exception as e:
        logger.error(f"감정 매칭 점수 계산 실패: {str(e)}")
        return 0.0

if __name__ == "__main__":
    test_tags = ["기쁨", "행복", "기대감"]
    top = multi_stage_selector(test_tags)
    print(format_memories(top))