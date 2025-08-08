
import json
import os

def trim_prompt_log(path="EORA/logs/prompt_history_log.json", limit=500):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if len(data) > limit:
            trimmed = data[-limit:]
            with open(path, "w", encoding="utf-8") as f:
                json.dump(trimmed, f, indent=2, ensure_ascii=False)
