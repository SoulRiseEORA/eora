import json
from recall_trigger_detector import detect_recall_intent
from datetime import datetime

MEMORY_DB_PATH = "./memory_db.json"  # 수정된 경로

def load_memory_db(path=MEMORY_DB_PATH):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Could not load memory DB: {e}")
        return []

def recall_memory(user_input, memory_db):
    intent, target_date = detect_recall_intent(user_input)
    if not intent:
        return "회상 트리거가 감지되지 않았습니다."

    recalled = []

    for memory in memory_db:
        if target_date:
            if memory.get("timestamp", "").startswith(str(target_date)):
                recalled.append(memory)
        else:
            if any(k in memory.get("summary_prompt", "") for k in ["기억", "대화", "이야기", "추억", "일"]) or \
               any(k in memory.get("tags", []) for k in ["기억", "대화", "감정", "사건"]):
                recalled.append(memory)

    if not recalled:
        return "해당 조건에 맞는 기억을 찾지 못했습니다."

    recalled.sort(key=lambda x: (x.get("resonance_score", 0), x.get("importance", 0)), reverse=True)
    return format_recall(recalled[:3])

def format_recall(memories):
    formatted = ["\n📌 회상된 기억:"]
    for m in memories:
        formatted.append(f"🕓 {m.get('timestamp')} — {m.get('summary_prompt')}")
    return "\n".join(formatted)

if __name__ == "__main__":
    test_input = input("💬 사용자 입력: ")
    memory_db = load_memory_db()
    result = recall_memory(test_input, memory_db)
    print(result)
