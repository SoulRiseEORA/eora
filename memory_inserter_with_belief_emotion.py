from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from aura_system.memory_structurer_advanced import create_memory_atom

# DB 연결
client = MongoClient("mongodb://localhost:27017")
db = client["aura_memory"]
collection = db["memory_atoms"]

def insert_atom(user_input: str, gpt_response: str, origin_type="user") -> str:
    atom = create_memory_atom(user_input, gpt_response, origin_type)
    result = collection.insert_one(atom)
    print("✅ 저장된 memory atom:")
    print(f"🧠 input: {user_input}")
    print(f"🤖 output: {gpt_response[:50]}...")
    print(f"💓 emotion_score: {atom['emotion_score']}  🧠 belief: {atom['belief_vector']}")
    print(f"🌀 importance: {atom['importance']}  resonance: {atom['resonance_score']}")
    return str(result.inserted_id)

# 테스트 실행 예시
if __name__ == "__main__":
    insert_atom("나는 어제 밤에 혼자 길을 걸었어", "그건 고요한 경험이었겠네요. 당신의 내면과 만나는 시간처럼 느껴집니다.")
