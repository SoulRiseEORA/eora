"""
prompt_controller_SAFE.py
- user_prompts 필드가 없거나, str 타입이거나, 잘못된 구조일 때도 안전하게 처리
"""

import os
import json

PROMPT_PATH = "ai_brain/ai_prompts.json"
DEFAULT_PROMPT = "기본 시스템 프롬프트가 설정되지 않았습니다."

def save_prompt(prompt_text: str):
    print("[SAVE] 요청된 프롬프트:", repr(prompt_text))
    os.makedirs(os.path.dirname(PROMPT_PATH), exist_ok=True)

    prompts = []

    if os.path.exists(PROMPT_PATH):
        try:
            with open(PROMPT_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

                # 안전한 구조 확인
                if isinstance(data, dict) and isinstance(data.get("user_prompts"), list):
                    prompts = data["user_prompts"]
                elif isinstance(data, list):  # 예외적으로 리스트만 저장된 경우
                    prompts = data
                else:
                    print("⚠️ [WARNING] 예상치 못한 구조. 초기화 진행.")
        except Exception as e:
            print("❌ [ERROR] 프롬프트 로딩 실패. 초기화:", e)
            prompts = []

    # 중복 제거 후 저장
    if prompt_text.strip() in prompts:
        print("⚠️ [중복] 이미 저장된 프롬프트입니다.")
        return False, "⚠️ 이미 저장된 문장입니다."

    prompts.append(prompt_text.strip())

    try:
        with open(PROMPT_PATH, "w", encoding="utf-8") as f:
            json.dump({"user_prompts": prompts}, f, ensure_ascii=False, indent=4)
        print("✅ [SAVE 완료] 프롬프트 저장됨:", PROMPT_PATH)
        return True, "✅ 프롬프트가 저장되었습니다."
    except Exception as e:
        print("❌ [ERROR] 저장 실패:", e)
        return False, "❌ 저장 중 오류 발생"

def load_prompt():
    if os.path.exists(PROMPT_PATH):
        try:
            with open(PROMPT_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                prompts = data.get("user_prompts", [])
                return prompts[-1] if prompts else DEFAULT_PROMPT
        except Exception as e:
            print("❌ [ERROR] 프롬프트 로딩 실패:", e)
            return DEFAULT_PROMPT
    return DEFAULT_PROMPT

def apply_prompt_to_session(session_obj, prompt_text: str):
    if hasattr(session_obj, "set_system_prompt"):
        session_obj.set_system_prompt(prompt_text)
        return "✅ 세션에 프롬프트 적용 완료"
    return "⚠️ 세션에 system_prompt 속성이 없습니다."