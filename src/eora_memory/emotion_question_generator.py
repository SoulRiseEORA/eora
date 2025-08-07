"""
감정 질문 자연어 생성기
- 100개 이상의 감정 질문 샘플
- 샘플 중 무작위 선택
- 선택된 질문을 GPT를 통해 자연스럽게 다듬기
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
import random
from openai import OpenAI

client = OpenAI()

# 감정 질문 샘플 100개 (일부 예시)
base_questions = [
    "지금 기분이 어떠신가요?",
    "이번 작업을 마치고 어떤 느낌이 드시나요?",
    "오늘 하루 중 가장 인상 깊었던 순간은?",
    "방금 마친 결과에 대해 어떤 생각이 드세요?",
    "진행 중에 힘들었던 점은 있었나요?",
    "새로운 아이디어가 떠오른 부분이 있었나요?",
    "과정을 거치면서 느낀 감정은 무엇이었나요?",
    "지금 떠오르는 단어는 무엇인가요?",
    "이번 경험을 한 단어로 표현한다면?",
    "완료 후 느껴지는 에너지는 어떤가요?",
    "이 작업이 앞으로 어떻게 연결될 것 같나요?",
    "오늘 당신을 가장 행복하게 한 것은 무엇인가요?",
    "이번 주제에서 얻은 통찰이 있다면?",
    "이전과 달라진 점을 느끼셨나요?",
    "처음 시작할 때와 비교해 어떤 변화가 있었나요?",
    "이 경험을 다른 사람에게 어떻게 설명하고 싶나요?",
    "마음속에 남는 장면이 있다면 어떤 건가요?",
    "지금 마음에 가장 강하게 떠오르는 감정은?",
    "앞으로 이어갈 방향에 대해 어떤 느낌을 가지고 있나요?",
    "이번 세션을 통해 발견한 나만의 패턴이 있나요?"
    # ... 계속 추가 가능 (지금은 20개, 필요시 100개 완성 가능)
]

def generate_emotion_question():
    """
    감정 질문을 자연스럽게 생성
    """
    base = random.choice(base_questions)
    prompt = f"""
    아래 문장을 더 부드럽고 자연스러운 감정 질문 문장으로 리포맷 해주세요.
    너무 기계적이지 않고, 친근하고 대화체로.

    기본 문장: "{base}"

    새로운 문장:
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=80
    )
    return response.choices[0].message.content.strip()