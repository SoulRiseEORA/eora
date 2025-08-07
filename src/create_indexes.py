"""
create_indexes.py

MongoDB에 필요한 인덱스를 자동으로 생성해 주는 스크립트입니다.
사용법 (CMD):
  > python create_indexes.py

환경변수 MONGO_URI, MONGO_DB 사용 가능 (없으면 기본값 사용).
"""

import os
from pymongo import MongoClient

def main():
    # 1) 환경변수 또는 기본값으로 MongoDB URI와 DB 이름 설정
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGO_DB", "aura_memory_db")
    collection_name = os.getenv("MONGO_COLLECTION", "memory")

    print(f"🔗 MongoDB 연결: {mongo_uri}{db_name}.{collection_name}")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    col = db[collection_name]

    # 2) 인덱스 생성 (없으면 만들고, 있으면 스킵)
    index_name = "trigger_ts_idx"
    print("⏳ 인덱스 생성 또는 확인 중...")
    col.create_index(
        [("trigger_keywords", 1), ("timestamp", -1)],
        name=index_name
    )
    print(f"✅ 인덱스 '{index_name}' 가(이) 설정되었습니다.")

if __name__ == "__main__":
    main()
