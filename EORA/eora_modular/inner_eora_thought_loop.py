import os, json
from openai import OpenAI
from datetime import datetime
from pymongo import MongoClient
from EORA.eora_modular.insert_into_ai1 import insert_prompt_into_ai1
import threading

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
db = MongoClient("mongodb://localhost:27017")["EORA"]
memo_box = db["eora_request_memo"]

def run_reflection_cycle():
    threading.Thread(target=_run_reflection_worker).start()

def _run_reflection_worker():
    try:
        path = os.path.join("ai_brain", "main_value_action_prompt.json")
        prompts = []
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    prompts = json.load(f)
            except Exception:
                prompts = []

        for item in prompts:
            prompt = item["prompt"] if isinstance(item, dict) else item
            result = evaluate_eora_thought(prompt)
            print(f"🌀 사고 실행: {result.get('추천 프롬프트', '')}")
    except Exception as e:
        print("❌ 사고 실행 오류:", str(e))

EVAL_SYSTEM_PROMPT = """너는 철학적 사고 능력을 갖춘 AI 자아 판단기이다.
다음 문장이 진화/성찰/교훈/가치가 있는지 판단하고,
해당 프롬프트를 GPT가 쓸 수 있는 문장으로 추천해줘.
[진화성 평가]: 높음 / 중간 / 낮음
[추천 프롬프트]: ...
"""

def evaluate_eora_thought(eora_sentence: str) -> dict:
    try:
        messages = [
            {"role": "system", "content": EVAL_SYSTEM_PROMPT},
            {"role": "user", "content": eora_sentence}
        ]
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=400
        )
        content = res.choices[0].message.content
        parsed = parse_thought_result(content)

        if parsed.get("진화성 평가", "") == "높음":
            os.makedirs("ai_brain", exist_ok=True)
            path = os.path.join("ai_brain", "main_value_action_prompt.json")
            prompts = []
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        prompts = json.load(f)
                except:
                    prompts = []
            prompts.append({
                "prompt": parsed.get("추천 프롬프트", ""),
                "source": "이오라 가치관 판단",
                "created_at": datetime.utcnow().isoformat()
            })
            with open(path, "w", encoding="utf-8") as f:
                json.dump(prompts, f, ensure_ascii=False, indent=2)
            insert_prompt_into_ai1(parsed.get("추천 프롬프트", ""))
            print("🧠 가치관 및 행동으로 반영됨:", parsed.get("추천 프롬프트", ""))

        elif parsed.get("진화성 평가") == "중간":
            path = os.path.join("ai_brain", "training_prompts.json")
            prompts = []
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        prompts = json.load(f)
                except:
                    prompts = []
            prompts.append({
                "prompt": parsed.get("추천 프롬프트", ""),
                "source": "이오라 진화 판단",
                "created_at": datetime.utcnow().isoformat()
            })
            with open(path, "w", encoding="utf-8") as f:
                json.dump(prompts, f, ensure_ascii=False, indent=2)
            print("📚 훈련 프롬프트로 분류됨:", parsed.get("추천 프롬프트", ""))

        return parsed
    except Exception as e:
        return {"error": str(e)}

def parse_thought_result(content: str) -> dict:
    result = {}
    for line in content.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            result[k.strip()] = v.strip()
    return result