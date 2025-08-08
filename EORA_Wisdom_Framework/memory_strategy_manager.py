# memory_strategy_manager.py
# 컨텍스트(상황) 자동 분석 + 기억 유지 전략 제공

def get_turn_limit_for_context(context: str) -> int:
    strategy = {
        "일반": 7,
        "코딩": 15,
        "감정": 20,
        "회상": 0,
        "문서": 3
    }
    return strategy.get(context, 7)

def get_context_from_text(text: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ["감정", "느낌", "슬픔", "기쁨", "감성"]):
        return "감정"
    if any(word in lowered for word in ["코드", "python", "에러", "함수", "클래스"]):
        return "코딩"
    if any(word in lowered for word in ["파일", "문서", "학습", "첨부"]):
        return "문서"
    if any(word in lowered for word in ["기억", "회상", "전에", "그때", "이전"]):
        return "회상"
    return "일반"

# 테스트용
if __name__ == "__main__":
    test_inputs = [
        "오늘은 코드 에러가 발생했어",
        "감정적으로 힘든 날이야",
        "이 문서를 학습시켜줘",
        "그때 했던 말 기억나?",
        "날씨가 좋아"
    ]
    for t in test_inputs:
        ctx = get_context_from_text(t)
        turns = get_turn_limit_for_context(ctx)
