"""
소주제 기반 연쇄 기억 회상기
- 선택된 소주제를 중심으로 연속 기억 회상
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from pymongo import MongoClient
from bson.objectid import ObjectId

mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["eora_memory"]
collection = db["memories"]

def recall_chain_by_subtopic(sub_topic, depth=5):
    """
    소주제(sub_topic)를 중심으로 기억을 연쇄 회상
    """
    current_set = list(collection.find({"sub_topic": sub_topic}).sort("timestamp", -1).limit(1))
    result_chain = []
    visited = set()

    while current_set and len(result_chain) < depth:
        current = current_set[0]
        if str(current["_id"]) in visited:
            break
        result_chain.append(current)
        visited.add(str(current["_id"]))
        conn_ids = current.get("connections", [])
        if conn_ids:
            current_set = list(collection.find({"_id": {"$in": [ObjectId(cid) for cid in conn_ids]}}))
        else:
            break

    return result_chain