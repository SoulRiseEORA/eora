"""
기억 연결 강도화 모듈
- 기억 간 연결의 '강도' 수치화 및 저장
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from pymongo import MongoClient
from bson.objectid import ObjectId
import random

mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["aura_memory"]
collection = db["memory_atoms"]

def strengthen_memory_link(source_id, target_id, strength_score):
    """
    source 기억에서 target 기억으로 연결 + 강도 점수 기록
    """
    link_entry = {
        "target_id": target_id,
        "strength": round(strength_score, 3)
    }

    collection.update_one(
        {"_id": ObjectId(source_id)},
        {"$push": {"strengthened_connections": link_entry}}
    )
    print(f"✅ 연결 강도 추가 완료: {source_id} → {target_id} (강도: {strength_score})")

if __name__ == "__main__":
    src = input("Source 기억 ID: ")
    tgt = input("Target 기억 ID: ")
    strength = float(input("강도 점수 (0.0 ~ 1.0): "))
    strengthen_memory_link(src, tgt, strength)