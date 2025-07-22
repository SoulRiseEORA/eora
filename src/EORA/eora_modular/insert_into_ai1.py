"""
insert_into_ai1.py

🧠 이오라 프롬프트(ai1)에 대해 다음 기준으로 JSON 중간 삽입을 지원합니다:
- 중요도 태그 기준 ("⭐" 포함 시 상단 우선)
- 중복 제거
- 특정 키워드("배움") 이후 삽입
"""

import os, json

PROMPT_PATH = os.path.join("ai_brain", "ai_prompts.json")

def insert_prompt_into_ai1(prompt: str):
    os.makedirs("ai_brain", exist_ok=True)
    data = {"ai1": []}
    if os.path.exists(PROMPT_PATH):
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

    ai1_list = data.get("ai1", [])

    # ✅ 중복 제거
    if prompt.strip() in ai1_list:
        print("⚠️ 이미 존재하는 프롬프트입니다. 건너뜁니다.")
        return

    # ✅ 중요도 태그 기준 우선 삽입
    if "⭐" in prompt:
        ai1_list.insert(0, prompt.strip())
    else:
        # ✅ 특정 키워드 다음 삽입 ("배움")
        inserted = False
        for i, p in enumerate(ai1_list):
            if "배움" in p:
                ai1_list.insert(i + 1, prompt.strip())
                inserted = True
                break
        if not inserted:
            ai1_list.append(prompt.strip())

    data["ai1"] = ai1_list

    with open(PROMPT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ 프롬프트가 ai1에 성공적으로 삽입되었습니다.")