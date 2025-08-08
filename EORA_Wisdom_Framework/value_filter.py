# value_filter.py
# 다양한 판단 옵션 중, 우선순위에 따라 가장 적절한 응답을 선택합니다.
# 각 옵션은 시뮬레이션 결과가 포함된 튜플 형태로 들어오며,
# 우선순위는 value_map 구조로 정의됩니다.

from typing import List, Tuple, Dict

def filter_by_value(simulated_options: List[Tuple[str, str]], priority_map: Dict[str, float]) -> str:
    """
    옵션 리스트와 가치 우선순위를 받아 가장 적합한 응답을 반환합니다.

    Parameters:
        simulated_options: List of tuples like [(response_text, outcome)]
        priority_map: Dictionary like {"empathy": 1.0, "truth": 0.8, "authority": 0.5}

    Returns:
        Best response text (str)
    """

    outcome_weights = {
        "positive": priority_map.get("empathy", 1.0),
        "neutral": priority_map.get("truth", 0.5),
        "negative": -priority_map.get("conflict_avoidance", 1.0)  # 부정 회피 가중치
    }

    scored_options = []
    for response, outcome in simulated_options:
        score = outcome_weights.get(outcome, 0)
        scored_options.append((response, score))

    # 최종 점수가 가장 높은 응답 반환
    scored_options.sort(key=lambda x: x[1], reverse=True)
    return scored_options[0][0] if scored_options else simulated_options[0][0]

if __name__ == "__main__":
    options = [
        ("괜찮아요, 함께 해볼 수 있어요.", "positive"),
        ("그건 좀 실망이에요.", "negative"),
        ("정확한 의미를 모르겠어요.", "neutral")
    ]

    value_priority = {
        "empathy": 1.0,
        "truth": 0.8,
        "conflict_avoidance": 0.9
    }

    best = filter_by_value(options, value_priority)
