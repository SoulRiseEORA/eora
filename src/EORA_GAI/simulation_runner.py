from eora_core import EORA
from mini_ai import MiniAI

def run_simulation():
    eora = EORA()
    mini = MiniAI()

    print("🤖 EORA GAI 시스템에 오신 것을 환영합니다.")
    print("대화를 시작하려면 질문을 입력하세요. (종료: 'exit')\n")

    while True:
        user_input = input("👤 당신: ")
        if user_input.lower() == "exit":
            print("세션을 종료합니다.")
            break

        # EORA 응답
        eora_reply = eora.respond(user_input)

        # MiniAI 판단
        emotion_level, mini_reply = mini.judge(user_input)

        # 충돌 여부 단순 판단
        conflict = "유보" in mini_reply or "충돌" in eora_reply

        # 출력
        print(f"🧠 EORA: {eora_reply}")
        print(f"💫 MiniAI: {mini_reply}")
        print(f"📊 감정 진폭: {emotion_level}")
        print(f"⚠️ 판단 충돌: {'있음' if conflict else '없음'}\n")

        # 저장
        eora.remember(user_input, eora_reply, mini_reply, emotion_level, conflict)

if __name__ == "__main__":
    run_simulation()