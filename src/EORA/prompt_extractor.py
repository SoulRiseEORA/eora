"""
prompt_extractor_CLEAN.py
- 따옴표 문장 우선 추출
- 지시문 자동 제거 ("프롬프트에 저장", "저장하세요" 등)
- 의미 없는 안내문 제거
"""

import re

TRIGGER_PHRASES = [
    "프롬프트에 저장", "프롬프트로 저장", "프롬프트 만들어", "저장해",
    "저장하세요", "기억해", "기억하도록", "기억해줘", "추가해", "추가하세요"
]

def extract_meaningful_prompt(msg: str) -> str:
    # 1. 따옴표 기반 추출
    quotes = re.findall(r'"(.+?)"', msg)
    if quotes:
        return quotes[0].strip()

    # 2. 지시문 제거
    for phrase in TRIGGER_PHRASES:
        msg = msg.replace(phrase, "")

    # 3. 의미 있는 문장 추출
    candidates = re.split(r"[.?!\n]", msg)
    for c in candidates:
        c = c.strip()
        if len(c) > 10 and not any(x in c for x in ["프롬프트", "감사합니다", "저장"]):
            return c

    # 4. fallback
    return msg.strip()[:100]