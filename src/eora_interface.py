from memory_structurer_advanced_emotion_code import create_memory_atom
from pymongo import MongoClient
from datetime import datetime
from typing import List

class EORAInterface:
    def __init__(self, mongo_uri="mongodb://localhost:27017", db_name="aura_memory", collection_name="memory_atoms"):
        self.client = MongoClient(mongo_uri)
        self.collection = self.client[db_name][collection_name]

    def save_with_emotion(self, user_input: str, gpt_response: str, origin_type="user") -> str:
        atom = create_memory_atom(user_input, gpt_response, origin_type)
        result = self.collection.insert_one(atom)
        print(f"✅ 저장 완료: 감정={atom['emotion_label']} | 직감={atom['belief_vector']} | 중요도={atom['importance']}")
        return str(result.inserted_id)

    def recall_with_context(self, keywords: List[str], limit=5) -> List[dict]:
        query = {
            "tags": {"$in": keywords}
        }
        sort_order = [("resonance_score", -1), ("importance", -1), ("timestamp", -1)]
        results = list(self.collection.find(query).sort(sort_order).limit(limit))
        return results

# 예시 실행
if __name__ == "__main__":
    eora = EORAInterface()
    uid = eora.save_with_emotion("오늘 기분이 너무 좋아요. 하늘이 맑아서 행복했어요.", "맑은 하늘은 정말 기분을 좋게 하죠. 행복한 하루 되세요!")
    memories = eora.recall_with_context(["기분", "좋아", "맑아"])
    for m in memories:
        print(f"📅 {m['timestamp']} | 감정: {m['emotion_label']} | 내용: {m['user_input'][:30]}")
