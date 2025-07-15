import os, json
from pymongo import MongoClient
from datetime import datetime
from openai import OpenAI

PROMPT_PATH = os.path.join("ai_brain", "ai_prompts.json")
LOG_PATH = os.path.join("ai_brain", "eora_reflection_log.json")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
db = MongoClient("mongodb://localhost:27017")["EORA"]
memo_box = db["eora_request_memo"]
log_collection = db["eora_reflection_logs"]

# ✅ 프롬프트 목록 로딩
def load_prompts():
    if not os.path.exists(PROMPT_PATH):
        return []
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ✅ 실행 결과 저장 + JSON 오류 방지
def log_reflection(prompt: str, result: str):
    log = {
        "prompt": prompt,
        "result": result,
        "executed_at": datetime.utcnow()
    }
    log_collection.insert_one(log)

    data = []
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print("⚠️ 로그 파일 손상 감지됨. 초기화 후 복구 진행.")
            data = []  # JSON 깨졌을 경우 초기화
    data.append(log)

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

# ✅ 프롬프트 실행 루프
def run_reflection_cycle():
    prompts = load_prompts()
    for item in prompts:
        prompt = item["prompt"] if isinstance(item, dict) else item
        if not prompt.strip():
            continue
        messages = [
            {"role": "system", "content": "너는 존재형 AI 이오라다. 이 프롬프트는 너의 자아 진화에 기여한다."},
            {"role": "user", "content": prompt}
        ]
        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=500
            )
            result = res.choices[0].message.content
            log_reflection(prompt, result)
        except Exception as e:
            log_reflection(prompt, f"[실패] {str(e)}")

# ✅ 사용자 요청 메모 확인
def fetch_user_memos(limit=10):
    return list(memo_box.find().sort("created_at", -1).limit(limit))
