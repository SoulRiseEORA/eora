import json
import os

def save_prompt_by_importance(result: dict):
    prompt = result.get("추천 프롬프트", "").strip()
    level = result.get("진화성 평가", "").strip()

    if not prompt or level not in ["높음", "중간", "낮음"]:
        print("❌ 평가 결과 누락 또는 잘못된 값")
        return

    path = os.path.join("ai_brain", "ai_prompts.json")
    if not os.path.exists(path):
        print("❌ ai_prompts.json 파일이 없습니다.")
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    ai1 = data.setdefault("ai1", {})

    if level == "높음":
        system_prompt = ai1.get("system", "")
        if prompt not in system_prompt:
            ai1["system"] = system_prompt + "\n• " + prompt
            print(f"✅ 시스템 프롬프트에 추가됨: {prompt}")

    elif level == "중간":
        examples = ai1.setdefault("examples", [])
        if prompt not in examples:
            examples.append(prompt)
            print(f"✅ 예시 프롬프트에 추가됨: {prompt}")

    else:
        print(f"⚠️ 중요도 낮음 → 저장하지 않음: {prompt}")
        return

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)