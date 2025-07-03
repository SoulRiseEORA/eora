"""
config_loader.py
- 금강GPT가 기억할 config 파일 내용을 DB화하고 system prompt로 연결
"""

import sqlite3
from pathlib import Path
from hashlib import md5
from docx import Document
import json
import pandas as pd

DB_PATH = str(Path(__file__).parent / "configs_memory.db")
CONFIG_DIR = Path(__file__).parent / "configs"

def compute_md5(path):
    return md5(path.read_bytes()).hexdigest()

def summarize_file(path: Path) -> str:
    try:
        if path.suffix == ".txt":
            return path.read_text(encoding="utf-8")[:4000]
        elif path.suffix == ".json":
            obj = json.loads(path.read_text(encoding="utf-8"))
            return json.dumps(obj, indent=2)[:4000]
        elif path.suffix == ".docx":
            doc = Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs)[:4000]
        elif path.suffix == ".xlsx":
            df = pd.read_excel(path)
            return df.head(10).to_string()
    except Exception as e:
        return f"[오류] {path.name} → {e}"
    return ""

def sync_config_memory():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS file_memory (
            filepath TEXT PRIMARY KEY,
            filehash TEXT,
            content TEXT
        )""")
    updated = 0
    for file in CONFIG_DIR.glob("*.*"):
        filehash = compute_md5(file)
        cur.execute("SELECT filehash FROM file_memory WHERE filepath=?", (str(file),))
        row = cur.fetchone()
        if not row or row[0] != filehash:
            content = summarize_file(file)
            cur.execute("REPLACE INTO file_memory VALUES (?, ?, ?)", (str(file), filehash, content))
            updated += 1
    conn.commit()
    conn.close()
    return updated

def load_all_memory_summary():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT content FROM file_memory")
    summaries = cur.fetchall()
    conn.close()
    return "\n".join(s[0] for s in summaries if s)
