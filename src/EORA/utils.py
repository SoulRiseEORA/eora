"""
AURA 유틸리티 모듈 (EORA.utils용)
- 키워드 추출
- 간단한 요약 생성
- 공명 점수(직감도) 계산
"""

import random

def extract_tags(text):
    # 간단한 키워드 기반 태그 추출 (NLP로 교체 가능)
    keywords = ["전략", "계획", "목표", "기억", "문서", "요약", "의도", "개선", "기능", "대화"]
    return [word for word in keywords if word in text]

def summarize_text(text):
    # 길이 기반 간단 요약 생성
    return text.strip()[:50] + "..." if len(text) > 50 else text.strip()

def get_resonance_score(text):
    # 텍스트 길이 + 랜덤 요소로 점수 생성 (실제 감정 모델로 대체 가능)
    base = len(text)
    score = min(100, base // 5 + random.randint(5, 30))
    return score