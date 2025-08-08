import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
import json
import os
from datetime import datetime

LOG_DIR = "./chat_logs"

def list_sessions():
    return [f for f in os.listdir(LOG_DIR) if f.endswith("_chat.json")]

def load_session(session_file):
    with open(os.path.join(LOG_DIR, session_file), encoding="utf-8") as f:
        return f.read()

def summarize_session(session_text):
    lines = session_text.strip().split("\n")
    return {
        "length": len(lines),
        "first_line": lines[0] if lines else "",
        "last_updated": datetime.fromtimestamp(os.path.getmtime(os.path.join(LOG_DIR, session_file)))
    }