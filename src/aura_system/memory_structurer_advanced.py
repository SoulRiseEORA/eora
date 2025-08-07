import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
import datetime
import random
from aura_system.embedding_engine import embed_text

# 감정 추정 함수 (예시)
def estimate_emotion(text: str) -> float:
    keywords = ["기쁘", "좋", "행복", "감동", "슬프", "외롭", "불안", "화나"]
    score = sum(word in text for word in keywords) / len(keywords)
    return round(0.5 + score * 0.5, 3)

# 신념 구조 추출 함수 (임의 백터)
def extract_belief_vector(text: str) -> list:
    random.seed(hash(text) % 10000)
    return [round(random.uniform(0.0, 1.0), 3) for _ in range(3)]

# 고도화된 memory atom 생성
def create_memory_atom(user_input: str, gpt_response: str, origin_type="user") -> dict:
    now = datetime.datetime.utcnow()
    embedding = embed_text(user_input)

    memory = {
        "type": "conversation",
        "user_input": user_input,
        "gpt_response": gpt_response,
        "timestamp": now,
        "tags": list(set(user_input.lower().split())),
        "semantic_embedding": embedding,
        "emotion_score": estimate_emotion(user_input),
        "belief_vector": extract_belief_vector(user_input),
        "resonance_score": 70 + round(random.random() * 30, 2),
        "importance": 8000 + round(random.random() * 2000, 2),
        "origin_type": origin_type,
        "used_count": 0,
        "last_used": now,
        "linked_ids": []
    }

    return memory