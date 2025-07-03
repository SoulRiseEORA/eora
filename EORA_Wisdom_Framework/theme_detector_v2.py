# theme_detector_v2.py
# 불용어(stopwords)를 제거하고, 통찰 및 주제 키워드에서 의미 있는 단어만 추출합니다.

import re
from collections import Counter
from typing import List


# 기본 불용어 목록 (확장 가능)
STOPWORDS = set([
    "의", "이", "가", "을", "를", "은", "는", "에", "도", "과", "와", "에서",
    "이다", "있다", "했다", "한다", "하고", "되다", "것", "그", "이런", "저런", "요",
    "저", "좀", "듯", "때", "또는", "그리고", "하지만", "그러나", "그래서",
    "싶다", "싶어요", "같아요", "생각해요", "말해요", "합니다"
])

def clean_and_tokenize(text: str) -> List[str]:
    # 한글/영어 단어만 추출 후 소문자화
    words = re.findall(r"[가-힣a-zA-Z]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def extract_themes_from_summaries(summaries: List[str], top_k: int = 5) -> List[str]:
    word_counter = Counter()
    for summary in summaries:
        tokens = clean_and_tokenize(summary)
        word_counter.update(tokens)
    return [word for word, _ in word_counter.most_common(top_k)]


if __name__ == "__main__":
    summaries = [
        "삶의 의미를 찾고 싶어요.",
        "자연을 보면 마음이 평화로워져요.",
        "나는 누구인지 자주 생각해요.",
        "고통 속에서도 의미를 느낄 수 있어요.",
        "계획을 세우고 실천하려고 해요.",
        "진심으로 다시 시작하고 싶어요.",
    ]
    themes = extract_themes_from_summaries(summaries)
