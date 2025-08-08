# mongodb_initializer.py (업데이트 버전)
from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)

db_name = "aura_memory"
collection_name = "memories"

db = client[db_name]
collection = db[collection_name]

if collection_name not in db.list_collection_names():
    db.create_collection(collection_name)
    print(f"✅ '{collection_name}' 컬렉션을 생성했습니다.")

# 🚨 실제로 컬렉션이 보이게 하려면 문서 하나라도 넣어야 함
sample_doc = {
    "user_input": "날씨가 좋아서 기분이 좋아요",
    "response": "정말 맑은 날은 좋은 기분을 줍니다.",
    "emotion": "positive",
    "timestamp": "2025-05-07T00:00:00"
}
collection.insert_one(sample_doc)
print(f"✅ 테스트 문서가 삽입되어 컬렉션이 MongoDB에 생성되었습니다.")
