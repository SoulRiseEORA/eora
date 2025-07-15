
# GPT ↔ 사용자 대화 흐름에서 EORA & MiniAI 자동 개입 구조 + DB 저장

from EORA_Consciousness_AI import EORA
from MiniAI_Eora_SelfEvolution import MiniAI
from memory_manager import MemoryManagerAsync

def gpt_post_process(user_input, gpt_response):
    eora = EORA()
    eora_reply = eora.respond(user_input, gpt_response)

    mini = MiniAI(
        name="레조나",
        mission="감정 기반 판단",
        core_values=["정확보다 정직", "공명"],
        initial_knowledge=["감정은 응답의 진폭이다"]
    )
    mini.remember(eora_reply)
    mini.evolve_structure()
    mini_reply = mini.judge(user_input)

    print("\n[📥 GPT 응답]\n", gpt_response)
    print("\n[🧠 이오라 응답]\n", eora_reply)
    print("\n[💫 미니AI 판단]\n", mini_reply)

    try:
        mem = MemoryManagerAsync()
        mem.save_memory("session_mini", user_input, mini_reply)
        print("✅ MiniAI 판단이 DB에 저장되었습니다.")
    except Exception as err:
        print("⚠️ DB 저장 실패:", err)

if __name__ == "__main__":
    user_input = "나는 오늘 왜 슬펐을까?"
    gpt_response = "슬픔은 복잡한 감정입니다. 말해줘서 고마워요."
    gpt_post_process(user_input, gpt_response)
