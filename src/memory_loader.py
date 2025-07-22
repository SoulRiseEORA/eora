
"""
memory_loader.py
- 학습 내용 제한 반환 버전
"""

import os
import json
import hashlib

MEMORY_DB_FILE = "memory_db.json"

def load_memory_chunks(category="금강", limit=60):
    try:
        if not os.path.exists(MEMORY_DB_FILE):
            return []
        with open(MEMORY_DB_FILE, "r", encoding="utf-8") as f:
            memory = json.load(f)
        items = memory.get(category, [])
        return items[:limit] if limit else items
    except Exception as e:
        print("❌ 메모리 로딩 실패:", e)
        return []
