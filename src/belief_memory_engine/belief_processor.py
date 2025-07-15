from belief_detector import extract_belief_phrases
from belief_reframer import suggest_reframe
import json
from datetime import datetime
import os

log_path = "belief_log.json"

def detect_and_reframe_belief(user_id, user_text):
    belief = extract_belief_phrases(user_text)
    if not belief:
        return None, None, None

    reframed = suggest_reframe(belief)
    log_entry = {
        "user_id": user_id,
        "belief": belief,
        "reframed": reframed,
        "detected": datetime.utcnow().isoformat()
    }

    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(log_entry)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    return belief, reframed, log_entry
