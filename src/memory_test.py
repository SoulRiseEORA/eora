from pymongo import MongoClient
from datetime import datetime
import random
import string

client = MongoClient("mongodb://localhost:27017")
db = client["aura_memory"]
collection = db["memory_atoms"]

test_key = "TEST_" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

test_atom = {
    "type": "conversation",
    "user_input": f"{test_key} 오늘 뭐했는지 기억해?",
    "gpt_response": f"{test_key} 너는 산책을 했다고 했었어.",
    "tags": [test_key.lower(), "테스트"],
    "importance": 9999,
    "resonance_score": 95,
    "timestamp": datetime.utcnow(),
    "used_count": 0,
    "last_used": datetime.utcnow()
}

result = collection.insert_one(test_atom)
print("✅ 저장됨:", result.inserted_id)

confirm = input("삭제할까요? (y/n): ")
if confirm.lower() == "y":
    collection.delete_one({"_id": result.inserted_id})
    print("🧹 삭제 완료")
else:
    print("✅ 보존됨")
