class WisdomEngine:
    def judge(self, insight, context, user_emotion):
        if user_emotion in ["anger", "sadness"]:
            return "지금은 감정이 격해 보이니, 잠시 생각을 정리해보시는 건 어떨까요?"
        elif insight and insight["intent_score"] > 0.8:
            return f"당신은 '{insight['central_theme']}'에 대해 깊이 고민 중입니다. 이번엔 더 나은 방향으로 가볼 수 있을 것 같아요."
        else:
            return "이 문제는 간단하지 않지만, 당신의 선택을 존중합니다. 함께 정리해볼까요?" 