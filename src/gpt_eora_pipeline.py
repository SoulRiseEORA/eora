from EORA_GAI.EORA_Consciousness_AI import EORA
from EORA_GAI.MiniAI_Eora_SelfEvolution import MiniAI
from EORA_GAI.SuperEgo_Reconciler import SuperEgoReconciler

class GPT_EORA_Pipeline:
    def __init__(self):
        self.eora = EORA()
        self.mini = MiniAI(
            name="레조나",
            mission="감정 기반 판단 수행",
            core_values=["정확보다 정직", "공명", "윤리"],
            initial_knowledge=["감정은 응답의 진폭이다", "유보는 정직함이다"]
        )
        self.super_ego = SuperEgoReconciler()

    def run(self, user_input):
        # 1. 철학 기반 응답
        eora_response = self.eora.respond(user_input)

        # 2. 감정 기반 판단
        emotion_level, mini_response = self.mini.judge(user_input)

        # 3. 메타 판단 통합
        final_judgment = self.super_ego.reconcile(
            eora_response,
            mini_response,
            context=user_input,
            emotion_level=emotion_level
        )

        # 4. 기억 저장
        self.eora.remember(
            user_input=user_input,
            eora_response=eora_response,
            mini_response=mini_response,
            emotion_level=emotion_level,
            conflict="유보" in mini_response or "충돌" in eora_response
        )

        # 5. 전체 응답 출력
        return {
            "user_input": user_input,
            "eora_response": eora_response,
            "mini_response": mini_response,
            "emotion_level": emotion_level,
            "final_judgment": final_judgment
        }

# 예시 실행
if __name__ == "__main__":
    pipeline = GPT_EORA_Pipeline()
    while True:
        user_input = input("👤 질문: ")
        if user_input.lower() in ("exit", "quit"):
            break
        result = pipeline.run(user_input)
        print("\n[🧠 EORA 응답] ", result["eora_response"])
        print("[💫 MiniAI 판단] ", result["mini_response"])
        print("[📊 감정 진폭] ", result["emotion_level"])
        print("[⚖️ 최종 판단] ", result["final_judgment"])
        print("-" * 60)