"""
기억 주제 간 연결 생성기
- 기억끼리 주제 유사도 기반으로 연결
- GPT를 통해 주제 관련성을 판단하여 connections[] 자동 추가
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from pymongo import MongoClient
from bson.objectid import ObjectId
from openai import OpenAI

client = OpenAI()
mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["eora_memory"]
collection = db["memories"]

def fetch_recent_memories(limit=50):
    return list(collection.find().sort("timestamp", -1).limit(limit))

def link_topics_in_memory():
    memories = fetch_recent_memories()
    updates = 0

    for memory in memories:
        candidates = [m for m in memories if m["_id"] != memory["_id"]]
        linked_ids = []

        for candidate in candidates:
            if are_topics_related(memory.get("topic", ""), candidate.get("topic", "")):
                linked_ids.append(candidate["_id"])

        if linked_ids:
            collection.update_one(
                {"_id": memory["_id"]},
                {"$set": {"connections": linked_ids}}
            )
            updates += 1

    print(f"✅ {updates} 개의 기억에 연결이 추가되었습니다.")

def are_topics_related(topic1: str, topic2: str) -> bool:
    """
    GPT를 통해 두 주제가 관련되어 있는지 판단
    """
    prompt = f"""
    주제1: "{topic1}"
    주제2: "{topic2}"

    이 두 주제가 서로 의미적으로 연관되어 있습니까?
    대답은 'Yes' 또는 'No'로 해주세요.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=32
    )
    return response.choices[0].message.content.strip().lower().startswith("yes")