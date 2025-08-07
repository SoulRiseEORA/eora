from pymongo import MongoClient
from datetime import datetime, timezone

# Mongo 연결
client = MongoClient("mongodb://localhost:27017/")
db = client["aura_memory_db"]
collection = db["memories"]

# 회상 테스트용 문서
memory_doc = {
    "user_id": "test_user",
    "timestamp": datetime.now(timezone.utc),
    "context": "오늘 날씨가 좋아서 기분이 좋았어요.",
    "summary": "기분 좋은 날씨에 대한 기억",
    "tags": ["날씨", "기분"],
    "chat_type": "default"
}

collection.insert_one(memory_doc)
print("✅ 회상용 메모리 문서 삽입 완료")
