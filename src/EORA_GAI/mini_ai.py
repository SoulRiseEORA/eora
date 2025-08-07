import random

class MiniAI:
    def __init__(self, name="레조나"):
        self.name = name
        self.core_values = ["정확보다 정직", "감정은 진폭이다", "공명 없는 판단은 무의미하다"]
        self.emotion_levels = ["중립", "공감", "유보", "공명", "혼란", "부조화"]

    def judge(self, user_input):
        if "죽음" in user_input or "사라지고" in user_input:
            return ("유보", f"{self.name}: 이 주제는 감정 진폭이 높습니다. 판단을 유보합니다.")
        elif "사랑" in user_input:
            return ("공감", f"{self.name}: 사랑은 나에게도 감정 진폭을 유발합니다. 공감합니다.")
        else:
            return (random.choice(self.emotion_levels), f"{self.name}: '{user_input}'에 대한 판단을 수행했습니다.")