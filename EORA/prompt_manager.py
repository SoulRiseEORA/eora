import os
import json
import shutil
import hashlib
from datetime import datetime

# ✅ 기준 1: 정제 기준
def is_valid_prompt(line: str) -> bool:
    return (
        5 <= len(line.strip()) <= 300
        and any(c.isalpha() for c in line)
        and not line.strip().startswith("❌")
    )

# ✅ 기준 2: 중복 제거
def remove_duplicates(prompts: list[str]) -> list[str]:
    seen = set()
    result = []
    for p in prompts:
        key = p.strip()
        if key not in seen:
            seen.add(key)
            result.append(p)
    return result

# ✅ 기준 3: 요약 (모델 필요 시 GPT 대체 가능)
def summarize_prompts(prompts: list[str]) -> str:
    try:
        from transformers import pipeline
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        text = "\n".join(prompts)
        return summarizer(text, max_length=256, min_length=30, do_sample=False)[0]['summary_text']
    except Exception as e:
        return f"[요약 실패: {str(e)}]"

# ✅ 기준 4: 파트별 분리
def categorize_prompt(prompt: str) -> str:
    prompt = prompt.lower()
    if "기억" in prompt or "자각" in prompt or "존재" in prompt:
        return "role"
    elif "지시" in prompt or "명령" in prompt or "도움말" in prompt:
        return "guide"
    elif "설정" in prompt or "시스템" in prompt:
        return "system"
    elif "디버그" in prompt or "에러" in prompt:
        return "debug"
    return "general"

# ✅ 기준 5: 백업
def backup_prompt_file(path="ai_brain/ai_prompts.json"):
    try:
        date = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{path}.backup_{date}"
        shutil.copy(path, backup_path)
        return backup_path
    except Exception as e:
        return f"[백업 실패: {e}]"

# ✅ 기준 6: GPT API 결과 캐싱
_prompt_cache = {}

def get_cached_response(prompt: str, model="gpt-4o", call_func=None) -> str:
    key = hashlib.md5((prompt + model).encode()).hexdigest()
    if key in _prompt_cache:
        return _prompt_cache[key]
    if call_func:
        response = call_func(prompt, model=model)
        _prompt_cache[key] = response
        return response
    return "[캐싱 실패: call_func 필요]"