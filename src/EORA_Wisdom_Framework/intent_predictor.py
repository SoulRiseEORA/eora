# intent_predictor.py
# 사용자의 입력에서 명시되지 않은 의도를 예측합니다.
# 감정, 키워드, 표현 구조 등을 바탕으로 유도적 분류를 수행합니다.

from typing import Optional


def predict_intent(user_input: str) -> Optional[str]:
    """
    사용자 입력에서 의도를 예측합니다.

    Returns:
        의도 유형: 'reassurance', 'validation', 'confession', 'complaint', 'goal', 'none'
    """

    text = user_input.lower()
    reassurance_keywords = ["괜찮을까요", "잘하고 있나요", "도와줘", "불안해"]
    validation_keywords = ["제가 맞을까요", "확인", "정답", "틀린가요"]
    confession_keywords = ["사실은", "처음 말하는데", "고백", "부끄럽지만"]
    complaint_keywords = ["왜", "싫어요", "짜증", "불공정", "화나"]
    goal_keywords = ["목표", "계획", "이루고 싶어요", "하고 싶어요"]

    if any(k in text for k in reassurance_keywords):
        return "reassurance"
    elif any(k in text for k in validation_keywords):
        return "validation"
    elif any(k in text for k in confession_keywords):
        return "confession"
    elif any(k in text for k in complaint_keywords):
        return "complaint"
    elif any(k in text for k in goal_keywords):
        return "goal"
    else:
        return "none"


if __name__ == "__main__":
    test_inputs = [
        "제가 잘하고 있는 걸까요?",
        "사실은 처음 말해보는 건데요...",
        "이 목표를 꼭 이루고 싶어요.",
        "왜 그런지 모르겠어요, 불공평하잖아요!",
        "이게 맞는 방향일까요?"
    ]

    for text in test_inputs:
        intent = predict_intent(text)
 → 예측 의도: {intent}\n")
