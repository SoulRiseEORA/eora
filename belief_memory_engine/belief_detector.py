
# belief_detector.py
# 경로: src/belief_memory_engine/belief_detector.py 또는 src/aura_system/belief_detector.py

import re

# ✅ 유사 표현 탐지 기반 신념 문구 추출기 (확장형)
def extract_belief_phrases(user_text):
    """
    사용자의 문장에서 부정적 신념 또는 자기 인식이 반영된 문장을 추출
    - 유사어, 형태소 변형, 감정 표현 포함
    - NLP 기반 확장 가능
    """

    user_text = user_text.lower()

    patterns = {
        "나는 무가치하다": [
            "난 안 돼", "난 못해", "나는 소용없어", "나는 가치 없어", "나는 의미 없어"
        ],
        "나는 실패자다": [
            "나는 실패자야", "항상 실패해", "계속 망쳐", "실패만 해", "나는 안되는 사람"
        ],
        "사람들은 날 존중하지 않는다": [
            "사람들은 날 무시해", "존중 안 해", "인정 안 받아", "사람들이 날 무시해"
        ],
        "나는 혼자다": [
            "외로워", "아무도 없어", "도움이 없어", "항상 혼자야", "기댈 곳이 없다"
        ],
        "나는 통제할 수 없다": [
            "너무 벅차", "통제 못 해", "감정 조절 안돼", "무너져", "컨트롤 안돼"
        ]
    }

    for belief, phrases in patterns.items():
        for phrase in phrases:
            if phrase in user_text:
                return belief

    return None

# ✅ 신념 벡터 생성기: 감정 표현, 부정어, 자기정체감 토큰 포함
def extract_belief_vector(user_text):
    """
    신념 추출: 신념 문구 유무 + 감정성 + 자기 표현 포함 여부로 벡터 구성
    향후 LLM 기반 심층 신념 추출로 확장 가능
    """
    text = user_text.lower()
    features = [
        float(bool(re.search(r"(안 돼|못 해|실패|무시|혼자|불안|소용없어)", text))),
        float("나는" in text or "난" in text),
        float("사람들" in text or "다른 사람" in text),
        float(bool(re.search(r"(두려움|통제|벅차|무너져)", text))),
        float(extract_belief_phrases(text) is not None)
    ]
    return features
