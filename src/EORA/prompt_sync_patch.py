"""
prompt_sync_patch_DEBUG.py
- 추출된 프롬프트를 저장하며, 디버깅 로그를 출력하여 문제 발생 지점 확인
"""

import os
import json
from EORA.prompt_controller import save_prompt, apply_prompt_to_session
from EORA.prompt_extractor import extract_prompt_from_text

PROMPT_AUTO_LOG = "configs/prompt_autosave_log.json"
ACTIVE_SESSION = None  # 세션이 외부에서 주입될 수 있음

def gpt_self_judged_save(full_text: str, reason: str = "자동 저장"):
    print("🧪 [DEBUG] 원본 발화:", full_text)
    prompt = extract_prompt_from_text(full_text)
    print("🧪 [DEBUG] 추출된 프롬프트:", repr(prompt))

    if not prompt or len(prompt) < 10:
        print("❌ [ERROR] 추출된 문장이 너무 짧거나 비어 있음. 저장 중단.")
        return "❌ 저장되지 않았습니다."

    ok, msg = save_prompt(prompt)
    print("🧠 [DEBUG] 저장 결과:", msg)

    log = {
        "original_text": full_text.strip(),
        "extracted_prompt": prompt,
        "reason": reason,
        "result": msg
    }

    if ACTIVE_SESSION:
        session_msg = apply_prompt_to_session(ACTIVE_SESSION, prompt)
        log["session_update"] = session_msg
        print("🔗 [DEBUG] 시스템 프롬프트 적용:", session_msg)

    _append_autosave_log(log)
    return msg

def _append_autosave_log(log_entry: dict):
    os.makedirs(os.path.dirname(PROMPT_AUTO_LOG), exist_ok=True)
    logs = []
    if os.path.exists(PROMPT_AUTO_LOG):
        with open(PROMPT_AUTO_LOG, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except:
                logs = []
    logs.append(log_entry)
    with open(PROMPT_AUTO_LOG, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)