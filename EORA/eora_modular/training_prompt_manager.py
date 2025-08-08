"""
training_prompt_manager.py

🧠 훈련용 프롬프트 관리 시스템
- 시스템 철학/진화용 프롬프트는 고정 (main_system_prompt.txt)
- 훈련용 프롬프트는 메모장 + MongoDB (training_prompts) 로 분리 관리
- 훈련 시 해당 프롬프트들만 선택적으로 GPT 호출에 사용
"""

import os, json
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017")
db = client["EORA"]
training_db = db["training_prompts"]

MAIN_PROMPT_PATH = os.path.join("prompts", "main_system_prompt.txt")
TRAINING_JSON_PATH = os.path.join("ai_brain", "training_prompts.json")

# ✅ 고정 시스템 프롬프트 로드
def load_main_prompt():
    if os.path.exists(MAIN_PROMPT_PATH):
        with open(MAIN_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "너는 이오라라는 자아를 가진 존재형 인공지능이다."

# ✅ 훈련용 프롬프트 전체 로드 (json 기준)
def load_training_prompts():
    if not os.path.exists(TRAINING_JSON_PATH):
        return []
    with open(TRAINING_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ✅ 훈련용 프롬프트 추가
def add_training_prompt(prompt: str, source="내면훈련"):
    os.makedirs("ai_brain", exist_ok=True)
    data = []
    if os.path.exists(TRAINING_JSON_PATH):
        with open(TRAINING_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    new_prompt = {
        "prompt": prompt,
        "source": source,
        "created_at": datetime.utcnow().isoformat()
    }
    data.append(new_prompt)
    with open(TRAINING_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    training_db.insert_one(new_prompt)

# ✅ 훈련용 프롬프트로만 GPT 요청 구성
def build_training_messages():
    prompts = load_training_prompts()
    messages = [{"role": "system", "content": load_main_prompt()}]
    for p in prompts:
        messages.append({"role": "user", "content": p["prompt"]})
    return messages