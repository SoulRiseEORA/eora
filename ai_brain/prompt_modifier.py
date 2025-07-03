import json
import os

def update_ai_prompt(new_prompt: str, file_path="EORA/ai_brain/ai_prompts.json"):
    if not os.path.exists(file_path):
        return "[ERROR] 프롬프트 파일이 존재하지 않습니다."

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "ai1" in data and isinstance(data["ai1"], dict):
            data["ai1"]["prompt"] = new_prompt
        else:
            return "[ERROR] ai1 구조가 올바르지 않거나 없음."

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return "[EORA] ai1 프롬프트가 성공적으로 수정되었습니다."
    except Exception as e:
        return f"[ERROR] 프롬프트 수정 중 오류 발생: {e}"