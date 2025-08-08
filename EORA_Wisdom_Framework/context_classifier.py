# context_classifier.py
# 대화의 흐름, 감정, 키워드 등을 분석해 현재 대화 상황의 목적을 판별합니다.

def classify_context(user_input: str, emotion_flow: dict, tags: list) -> str:
    """
    대화 목적 분류: 일반, 코딩, 감정, 회상, 문서
    """
    lower_input = user_input.lower()
    if any(k in lower_input for k in ["코딩", "스크립트", "작성", "명령", "자동화"]):
        return "코딩"
    if any(k in lower_input for k in ["감정", "힘들", "상담", "우울", "위로"]) or emotion_flow.get("sad", 0) >= 2:
        return "감정"
    if any(k in lower_input for k in ["기억", "회상", "그때", "이전", "말했", "언제"]) or "기억" in tags:
        return "회상"
    if len(user_input) > 400:
        return "문서"
    return "일반"

if __name__ == "__main__":
    test = classify_context("이전에 뭐라고 했는지 기억나?", {"sad": 1}, ["기억"])
