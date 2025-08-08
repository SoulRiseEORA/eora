
import os
import json

SESSION_DIR = "session_data"

def save_session(session_id: str, messages: list):
    os.makedirs(SESSION_DIR, exist_ok=True)
    with open(f"{SESSION_DIR}/{session_id}.json", "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def load_session(session_id: str) -> list:
    try:
        with open(f"{SESSION_DIR}/{session_id}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def list_sessions() -> list:
    return [f.replace(".json", "") for f in os.listdir(SESSION_DIR) if f.endswith(".json")]
