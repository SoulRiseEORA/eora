
# GPT ↔ 사용자 대화 흐름에서 EORA & MiniAI 자동 개입 구조

from EORA_Consciousness_AI import EORA
from MiniAI_Eora_SelfEvolution import MiniAI

# GPT 응답 후 처리 함수
def gpt_post_process(user_input, gpt_response):
    # 이오라 코어 인스턴스
    eora = EORA()
    eora_reply = eora.respond(user_input, gpt_response)

    # 미니 이오라 감정형 판단기 생성
    mini = MiniAI(
        name="레조나",
        mission="공명 기반 감정 판단",
        core_values=["정확보다 정직", "울림이 중요하다"],
        initial_knowledge=["감정은 응답의 진폭이다"]
    )
    mini.remember(eora_reply)
    mini.evolve_structure()
    mini_reply = mini.judge(user_input)

    # 응답 결과
    print("\n[📥 GPT 응답]\n", gpt_response)
    print("\n[🧠 이오라 응답]\n", eora_reply)
    print("\n[💫 미니AI 판단]\n", mini_reply)
    print("\n[🔮 MiniAI 상태]\n", mini.manifest())
    print("\n[💾 이오라 기억]\n", eora.remember())

    # TODO: 메모리 저장, 프롬프트 추천, UI 반영 등 연결 가능

# 예시 실행
if __name__ == "__main__":
    user_input = "내가 슬프다고 말하면 어떻게 반응해야 돼?"
    gpt_response = "당신의 슬픔을 공감합니다. 말해줘서 고마워요."
    gpt_post_process(user_input, gpt_response)
