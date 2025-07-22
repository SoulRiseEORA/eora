class InsightEngine:
    def infer(self, memories):
        if not memories:
            return {"central_theme": None, "emotion_trend": None, "intent_score": 0.0}
        # 가장 많이 등장한 belief_tag를 중심 주제로
        tags = [tag for m in memories for tag in m["belief_tags"]]
        central_theme = max(set(tags), key=tags.count) if tags else None
        # 감정 흐름(가장 많이 등장한 감정)
        emotions = [m["emotion"] for m in memories]
        emotion_trend = max(set(emotions), key=emotions.count) if emotions else None
        # intent_score는 임의로
        intent_score = 0.9 if central_theme else 0.5
        return {"central_theme": central_theme, "emotion_trend": emotion_trend, "intent_score": intent_score} 