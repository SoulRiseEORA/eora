"""
memory_structurer_advanced_emotion_code.py
- 안전한 절대경로 기반 JSON 로더
"""

import os, json, datetime, random
from aura_system.embedding_engine import embed_text

BASE_DIR = os.path.dirname(__file__)
json_path = os.path.join(BASE_DIR, "emotion_code_map.json")

with open(json_path, "r", encoding="utf-8") as f:
    EMOTION_CODE_MAP = json.load(f)

def estimate_emotion(text: str) -> (str, float):
    max_score, best = 0, "기타"
    for label in EMOTION_CODE_MAP:
        if label in text:
            score = len(label)
            if score > max_score:
                max_score, best = score, label
    weight = round(0.5 + 0.1 * min(max_score, 5), 3)
    return best, weight

def extract_belief_vector(text: str) -> list:
    random.seed(hash(text) & 0xFFFF)
    return [round(random.uniform(0, 1), 3) for _ in range(3)]

def create_memory_atom(user_input: str, gpt_response: str, origin_type='user') -> dict:
    now = datetime.datetime.utcnow()
    embedding = embed_text(user_input)
    emo_label, emo_weight = estimate_emotion(user_input)
    emo_code = EMOTION_CODE_MAP.get(emo_label, {}).get('code', 'EXXX')
    return {
        'type': 'conversation',
        'user_input': user_input,
        'gpt_response': gpt_response,
        'timestamp': now,
        'tags': list(set(user_input.lower().split())),
        'semantic_embedding': embedding,
        'emotion_label': emo_label,
        'emotion_code': emo_code,
        'emotion_score': emo_weight,
        'belief_vector': extract_belief_vector(user_input),
        'resonance_score': 70 + round(random.random() * 30, 2),
        'importance': 8000 + round(random.random() * 2000, 2),
        'origin_type': origin_type,
        'used_count': 0,
        'last_used': now,
        'linked_ids': []
    }
