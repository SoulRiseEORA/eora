"""
EORA Two-Track Subtopic 선택 시스템
- 직감 기반 빠른 선택
- 문맥 기반 정석 분석
- 둘을 비교 후 최종 소주제 선택
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
import random
from openai import OpenAI

client = OpenAI()

# ---------------------------
# 직감 기반 소주제 선택 (Fast Intuition Track)
# ---------------------------
def intuition_select_subtopic(user_input):
    """
    빠른 직감 기반 소주제 후보 생성 및 선택
    """
    quick_keywords = [
        "디자인", "색상", "스타일", "브랜딩", "감정표현", "아이디어",
        "계획", "구성", "패턴", "톤", "로고", "상징성", "시각적 흐름",
        "창의성", "안정성", "속도감", "고급스러움", "신뢰성", "유연성", "집중"
    ]
    candidates = random.sample(quick_keywords, 5)
    selected = random.choice(candidates)
    return selected

# ---------------------------
# 정석 기반 문맥 분석 소주제 선택 (Logical Context Track)
# ---------------------------
def logic_select_subtopic(user_input):
    """
    GPT로 사용자의 발화를 분석하여 소주제 후보 생성
    """
    prompt = f"""
    다음 사용자의 발화 내용을 분석하여 가장 중심이 되는 소주제 하나를 뽑아주세요.

    문장: "{user_input}"

    결과(단어 하나만):
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=20
    )
    return response.choices[0].message.content.strip()

# ---------------------------
# 최종 소주제 결정 로직
# ---------------------------
def decide_subtopic(user_input):
    """
    직감 트랙과 정석 트랙을 모두 실행 후 결과를 비교
    """
    intuition_result = intuition_select_subtopic(user_input)
    logic_result = logic_select_subtopic(user_input)

    print(f"🧠 직감 트랙 제안: {intuition_result}")
    print(f"🧠 정석 트랙 제안: {logic_result}")

    # 결과가 같으면 확정, 다르면 논리적 판단 우선
    if intuition_result.lower() == logic_result.lower():
        final_subtopic = logic_result
    else:
        # 신뢰성 우선: 논리 기반 결과 우선
        final_subtopic = logic_result

    print(f"✅ 최종 선택된 소주제: {final_subtopic}")
    return final_subtopic