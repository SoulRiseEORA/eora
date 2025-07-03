class SuperEgoReconciler:
    def __init__(self):
        self.priority_rules = [
            ("윤리", 3),
            ("공명", 2),
            ("정확성", 1)
        ]

    def reconcile(self, eora_response, mini_response, context, emotion_level):
        notes = []
        score = 0

        if "윤리" in eora_response or "윤리" in mini_response:
            score += 3
            notes.append("윤리 우선 반영")
        if "공명" in eora_response or "공명" in mini_response or emotion_level == "공명":
            score += 2
            notes.append("공명 반영")
        if "정확" in eora_response or "정확" in mini_response:
            score += 1
            notes.append("정확성 고려")

        if score >= 5:
            final = f"[SuperEgo] 이 응답은 윤리성과 공명을 모두 만족하므로 채택됩니다. ({', '.join(notes)})"
        elif "유보" in mini_response:
            final = "[SuperEgo] 감정적 판단 유보가 감지되어, 응답을 보류합니다."
        else:
            final = "[SuperEgo] 판단 기준 충돌이 존재하므로 신중히 해석해야 합니다."

        return final