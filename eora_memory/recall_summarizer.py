"""
회상 결과 요약기
- recall_chain 결과를 GPT를 통해 자연스럽게 요약하여 대화 연결
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from openai import OpenAI

client = OpenAI()

def summarize_memory_chain(memories):
    """
    회상된 memories 리스트를 자연스럽게 요약
    """
    if not memories:
        return "회상할 기억이 없습니다."

    memory_texts = []
    for mem in memories:
        summary = mem.get("summary_prompt", "")
        if summary:
            memory_texts.append(summary)

    joined = "\n".join(memory_texts)
    prompt = f"""
    다음 기억 요약들을 자연스럽게 하나의 짧은 이야기처럼 정리해 주세요.
    너무 딱딱하거나 기계적이지 않고, 대화하듯 이어지게 해주세요.

    기억들:
    {joined}

    요약 결과:
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()