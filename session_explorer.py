# session_explorer.py
# 세션별 대화 로그 조회 및 요약 보기

import os
import json
from glob import glob

def list_sessions(path="./chat_logs"):
    files = glob(os.path.join(path, "*_chat.json"))
    return [os.path.basename(f).replace("_chat.json", "") for f in files]

def load_session(name, path="./chat_logs"):
    with open(os.path.join(path, f"{name}_chat.json"), "r", encoding="utf-8") as f:
        return f.read()

def print_recent_logs(n=5):
    for name in sorted(list_sessions())[-n:]:
        print(f"📝 세션: {name}")
        print(load_session(name)[-300:])
        print("-" * 50)