"""
AURA Core Module
- 기억 회상 / 연결 / 요약 프롬프트 생성 등 핵심 기능 포함
"""

def recall_memory(user_input):
    # TODO: 트리거 키워드 기반 회상 알고리즘
    print(f"🔁 회상 시도: {user_input}")
    return ["TODO: 연관 기억 1", "TODO: 연관 기억 2"]

def generate_summary_prompt(memory):
    return f"요약된 프롬프트: {memory.get('summary', '')}"

def multi_stage_selector(user_input):
    return recall_memory(user_input)