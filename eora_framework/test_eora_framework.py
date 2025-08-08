from eora_framework import EORAFramework

def test():
    eora = EORAFramework()
    # 샘플 대화
    user_inputs = [
        ("오늘은 기분이 좀 우울해.", "괜찮으신가요? 감정을 나눠주셔서 고마워요.", "sadness", ["감정", "상담"]),
        ("내일은 중요한 발표가 있어.", "준비 잘 하셨으니 잘 될 거예요.", "anticipation", ["목표", "성장"]),
        ("최근에 자주 실수하는 것 같아.", "실수는 성장의 일부입니다.", "reflection", ["성찰", "성장"])
    ]
    for user, gpt, emotion, tags in user_inputs:
        result = eora.process(user, gpt, emotion, tags)
        print(result)

if __name__ == "__main__":
    test() 