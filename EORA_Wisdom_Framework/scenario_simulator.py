# scenario_simulator.py
# 시나리오 시뮬레이터는 다양한 응답 후보군에 대해 "예측 결과"를 추정합니다.
# 이를 통해 AI가 말한 후 일어날 수 있는 단기적/장기적 반응을 예상하고,
# 회피하거나 신뢰를 쌓는 판단을 할 수 있도록 도와줍니다.

from typing import Tuple

def simulate_outcome(response: str) -> str:
    """
    사용자의 응답 문장을 받아, 예상되는 반응을 분류합니다.
    기본 분류: 긍정적(positive), 중립적(neutral), 부정적(negative)
    향후 확장: 감정 점수, 신뢰도, 위험도 평가
    """

    # 키워드 기반 초기 간단 시뮬레이션 (V1)
    positive_keywords = ["응원", "괜찮아요", "함께", "할 수 있어요", "도와드릴게요", "기억해요"]
    negative_keywords = ["모르겠어요", "힘들어요", "그건 아니에요", "무의미해요", "포기", "실망"]
    conflict_triggers = ["왜 그러셨어요", "그건 잘못", "비판", "책임"]

    response_lower = response.lower()

    # 부정 반응 유도 가능성
    if any(k in response_lower for k in negative_keywords + conflict_triggers):
        return "negative"

    # 긍정 반응 유도 가능성
    elif any(k in response_lower for k in positive_keywords):
        return "positive"

    # 중립 또는 명확하지 않음
    else:
        return "neutral"

# 고급 예시: 확률/가중치 기반 스코어 평가 추가 예정
# def score_outcome(response: str) -> Dict:
#     return {
#         "emotion_change": 0.75,
#         "trust_boost": 0.8,
#         "conflict_risk": 0.2
#     }

if __name__ == "__main__":
    test_cases = [
        "괜찮아요, 함께 해볼 수 있어요.",
        "그건 좀 실망이에요.",
        "왜 그렇게 행동하셨나요?",
        "무의미한 일 같아요.",
        "할 수 있다고 믿어요.",
        "정확한 의미를 모르겠어요."
    ]

    for sentence in test_cases:
        pass
