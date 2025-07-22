"""
EORA event_score 자동 생성기
대화의 감정 강도, 신념 태그, 질문 여부 등을 종합하여 0~1 점수 계산
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
import re
import random

# 감정 점수 가중치 테이블 (예시)
emotion_weights = {
    "positive": 0.7,
    "neutral": 0.4,
    "conflict": 0.6,
    "negative": 0.5,
    "excited": 0.8,
    "confused": 0.6,
    "sad": 0.4,
    "angry": 0.5,
    "curious": 0.65,
    "motivated": 0.75
}

def is_question(text):
    return "?" in text or text.strip().endswith("나요") or text.strip().endswith("지요")

def count_emphasizers(text):
    return sum(text.count(k) for k in ["정말", "아주", "굉장히", "너무", "진짜", "확실히"])

def compute_event_score(user_msg: str, gpt_msg: str, emotion: str, belief_tags: list) -> float:
    """
    종합적으로 event_score를 산출
    """
    score = 0.0

    # 감정 가중치
    score += emotion_weights.get(emotion, 0.3)

    # 신념태그 개수
    score += 0.05 * len(belief_tags)

    # 질문 포함 여부
    if is_question(user_msg):
        score += 0.1

    # 강조 표현
    score += 0.05 * count_emphasizers(user_msg + gpt_msg)

    # 클리핑
    return min(round(score, 4), 1.0)