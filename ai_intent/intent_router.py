"""
EORA 고도화 판단 시스템
- 과거 회상 vs 지식 질문 vs 일반 요청 판단
- 모호한 경우 GPT가 재판단
- 청크 응답 / 자동 요약 / 직감 시제 분석 / 사용자 스타일 반영
"""

import re
from datetime import datetime
from openai import OpenAI

client = OpenAI()

# ---------------------------
# 🔍 직감 기반 트리거 분석기
# ---------------------------
def should_trigger_intent(user_input: str) -> bool:
    past_clues = ["했었", "그때", "전에", "예전에", "말했던", "기억나", "알려줬", "추억", "그날"]
    if any(clue in user_input.lower() for clue in past_clues):
        return True
    if re.search(r"(\d+일|몇일|며칠) 전", user_input):
        return True
    return False

# ---------------------------
# 🧠 1차 GPT 기반 분류
# ---------------------------
def classify_user_intent(user_input: str) -> tuple[str, bool]:
    prompt = f"""
    다음 문장이 어떤 목적에 해당하는지 GPT가 판단해주세요:
    1. 과거 대화 회상 → 'conversation_recall'
    2. 학습된 지식 기반 질문 → 'knowledge_question'
    3. 새로운 요청 → 'new_input'

    또한 확신이 있는지도 판단해주세요.

    문장: "{user_input}"
    형식:
    category: ...
    certainty: ...
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=128
    )
    lines = response.choices[0].message.content.strip().split("\n")
    category = lines[0].split(":")[1].strip()
    uncertain = lines[1].split(":")[1].strip().lower() == "no"
    return category, uncertain

# ---------------------------
# ❓ 모호할 경우 GPT에 재질문
# ---------------------------
def resolve_ambiguous_intent_with_gpt(user_input: str) -> str:
    prompt = f"""문장이 모호합니다. 다음 중 어느 목적에 해당하는지 다시 판단해주세요:
- conversation_recall
- knowledge_question
- new_input

문장: "{user_input}"
답변:
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=64
    )
    return response.choices[0].message.content.strip()

# ---------------------------
# ✅ 최종 분기 라우터
# ---------------------------
def route_input(user_input: str) -> str:
    if not should_trigger_intent(user_input):
        return "🗣 일반 대화 흐름 유지"

    category, uncertain = classify_user_intent(user_input)
    if uncertain:
        category = resolve_ambiguous_intent_with_gpt(user_input)

    if category == "conversation_recall":
        return "🧠 회상 실행 (memory_db → GPT 요약)"
    elif category == "knowledge_question":
        return "📚 학습된 정보 기반 검색"
    else:
        return "💬 일반 요청 응답"
