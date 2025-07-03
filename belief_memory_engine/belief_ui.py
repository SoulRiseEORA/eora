from belief_detector import extract_belief_phrases
from belief_reframer import suggest_reframe
import json
from datetime import datetime
import os

log_path = "belief_log.json"

def log_change(user_id, belief, reframed):
    entry = {
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
    logs.append(entry)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def main():
    import os
user_id = os.getenv("USER_ID", "default_user")
    print("💬 신념 탐지 CLI 시작 (그만하려면 '종료' 입력)")

    while True:
        user_input = input("👤 당신: ")
        if user_input.strip().lower() == "종료":
            print("👋 종료합니다.")
            break

        belief = extract_belief_phrases(user_input)
        if belief:
            print(f"🤖 감지된 신념: {belief}")
            new_belief = suggest_reframe(belief)
            print(f"💡 새로운 시각: {new_belief}")
            log_change(user_id, belief, new_belief)
        else:
            print("🤖 특별한 신념은 감지되지 않았습니다.")

if __name__ == "__main__":
    main()
