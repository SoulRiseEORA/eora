""""
실시간 회상 적절성 검증기
- 회상 직후 대화 맥락에 적합한지 GPT를 통해 검증
""""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from openai import OpenAI

client = OpenAI()

def validate_recall:
def quick_dry_run():
    sample = {"summary_prompt":"테스트","timestamp":"2025-01-01T00:00"}
    assert validate_recall("테스트", sample)
    print("✅ 회상 검증 통과")
(current_message: str, recalled_summary: str) -> bool:
""""
    회상된 기억이 대화 흐름상 적절한지 검증
""""
prompt = f""""
    대화 흐름을 고려하여, 아래 회상된 기억이 적절한지 판단해 주세요.

    현재 사용자 발화:
    "{current_message}"

    회상된 기억 요약:
    "{recalled_summary}"

    답변: [Yes] 또는 [No]
""""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=20
    )
    return response.choices[0].message.content.strip().lower().startswith("yes")

if __name__ == "__main__":
    current = input("현재 사용자 발화: ")
    recall = input("회상된 기억 요약: ")
    valid = validate_recall(current, recall)
    print(f"✅ 회상 적절성: {'적합' if valid else '부적합'}")