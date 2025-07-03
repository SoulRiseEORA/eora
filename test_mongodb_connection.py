
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "aura_memory"
COLLECTION_NAME = "memories"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # 연결 테스트
    client.server_info()  # 예외 발생 안하면 연결 성공

    # 테스트용 문서 삽입
    test_doc = {
        "test": "mongodb_connection",
        "timestamp": datetime.utcnow()
    }
    result = collection.insert_one(test_doc)

    print("✅ MongoDB 연결 성공")
    print(f"📄 테스트 문서 ID: {result.inserted_id}")
except Exception as e:
    print("❌ MongoDB 연결 실패:")
    print(e)
