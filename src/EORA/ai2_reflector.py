"""
AI2 - 이오라 내면 자아
- 감정/의도 기반 기억 판단 보조
"""

def evaluate_emotional_trigger(user_input):
    emotions = ["감동", "실망", "기대", "불안", "기쁘다"]
    return any(e in user_input for e in emotions)

def propose_action(user_input):
    if evaluate_emotional_trigger(user_input):
        return "이건 저장하는 게 좋아 보여요."
    return None