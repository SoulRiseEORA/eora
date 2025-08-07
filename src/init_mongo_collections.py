from pymongo import MongoClient
from datetime import datetime

# Mongo 연결
client = MongoClient("mongodb://localhost:27017/")
db = client["aura_memory_db"]

collections_to_create = {
    "memories": {
        "user_id": "example_user",
        "timestamp": datetime.utcnow(),
        "context": "예시 대화 내용",
        "summary": "요약된 기억",
    },
    "errors": {
        "timestamp": datetime.utcnow(),
        "error_message": "에러 메시지 예시",
        "traceback": "Traceback 예시",
        "module": "ai_chat",
    },
    "categories": {
        "category_id": "cat001",
        "title": "기획 관리",
        "keywords": ["자동화", "GPT", "시각화"],
        "description": "AI 프로젝트 카테고리 예시",
        "created_at": datetime.utcnow()
    },
    "generations": {
        "prompt": "사용자 입력 예시",
        "code": "print('Hello World')",
        "user": "example_user",
        "tags": ["test", "example"],
        "date": datetime.utcnow()
    }
}

# 각 컬렉션에 예시 문서 삽입
for name, doc in collections_to_create.items():
    col = db[name]
    if col.count_documents({}) == 0:
        col.insert_one(doc)

print("🎉 MongoDB 초기화 완료")
