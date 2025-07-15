"""
memory_db.py
- GPT 학습 청크를 JSON 파일 또는 MongoDB에 저장
"""

import os
import json
from datetime import datetime

DB_FILE = "memory_db.json"

def save_chunk(category: str, chunk: str):
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                db = json.load(f)
        else:
            db = {}

        date_key = f"{category}_{datetime.now().strftime('%Y%m%d')}"
        db.setdefault(date_key, []).append(chunk)

        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)

        print(f"✅ 저장됨: {date_key} – {chunk[:30]}...")
    except Exception as e:
        print(f"❌ 메모리 저장 실패: {str(e)}")