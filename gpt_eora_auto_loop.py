import openai
from eora_interface import EORAInterface
from emotion_logic_module import estimate_emotion
import os

openai.api_key = os.getenv("OPENAI_API_KEY", "your-api-key")

class GPT_EORA_Agent:
    def __init__(self):
        self.eora = EORAInterface()

    def generate_response(self, user_input: str) -> str:
        # 감정 분석
        emotion, code, score = estimate_emotion(user_input)
        
        # 감정 기반 system 메시지 조정
        system_msg = self.style_by_emotion(emotion)

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_input}
        ]

        try:
            res = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7
            )
            gpt_output = res.choices[0].message['content']
        except Exception as e:
            gpt_output = f"[GPT 호출 실패] {e}"

        # 기억 저장
        self.eora.save_with_emotion(user_input, gpt_output)
        return gpt_output

    def style_by_emotion(self, emotion: str) -> str:
        # 감정에 따른 응답 스타일 변형
        if emotion in ["슬픔", "우울", "절망", "외로움"]:
            return "당신의 감정을 공감하고 위로해주는 대화 스타일을 유지하세요."
        elif emotion in ["기쁨", "행복", "감사", "설렘"]:
            return "밝고 따뜻한 톤으로 공감하며 함께 기뻐하는 대화를 하세요."
        elif emotion in ["불안", "두려움", "긴장"]:
            return "진정시켜주고 신뢰를 주는 어조로 응답하세요."
        elif emotion in ["화", "짜증", "분노"]:
            return "차분하고 중립적인 어조로 공감을 전달하세요."
        else:
            return "일반적인 따뜻하고 친근한 어조로 응답하세요."

# 사용 예시
if __name__ == "__main__":
    agent = GPT_EORA_Agent()
    while True:
        user_input = input("👤 사용자: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        gpt_reply = agent.generate_response(user_input)
        print("🧠 EORA:", gpt_reply)
