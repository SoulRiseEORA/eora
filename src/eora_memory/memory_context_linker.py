"""
기억 연결 이유 기록기
- 기억 간 연결시 '왜 연결되었는가'를 기록
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from pymongo import MongoClient
from bson import ObjectId

mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["aura_memory"]
collection = db["memory_atoms"]

def link_memory_with_reason(source_id, target_id, reason_text):
    """
    source_id 기억에서 target_id 기억으로 연결하고, 이유 기록
    """
    connection_entry = {
        "target_id": target_id,
        "reason": reason_text
    }

    collection.update_one(
        {"_id": ObjectId(source_id)},
        {"$push": {"connections_reasoned": connection_entry}}
    )
    print(f"✅ 연결 추가 완료: {source_id} → {target_id} (이유: {reason_text})")

if __name__ == "__main__":
    src = input("Source 기억 ID: ")
    tgt = input("Target 기억 ID: ")
    reason = input("연결 이유 입력: ")
    link_memory_with_reason(src, tgt, reason)