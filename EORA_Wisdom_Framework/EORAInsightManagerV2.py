from aura_system.resonance_engine import calculate_resonance
from aura_system.vector_store import embed_text
from ai_model_selector import do_task_async
import time  # ✅ 시간 측정용 로그 추가

class EORAInsightManagerV2:
    def __init__(self, memory_manager):
        self.mem_mgr = memory_manager

    # 🧠 사고 위상 구조 판단 (기억, 감정, 메타인지, 초월)
    async def analyze_cognitive_layer(self, text):
        start_time = time.time()

        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": "아래 문장이 사고 수준에 해당하는지 분류하세요: 기억 / 감정 / 메타인지 / 초월"}]
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": text}]
            }
        ]

        result = await do_task_async(messages=messages, model="gpt-4o")
        return result

    # 🔁 공명 기반 회상 선택
    async def calculate_resonant_trace(self, user_id, new_embedding, top_n=3):
        summaries = await self.mem_mgr.query_memory(user_id=user_id, memory_type="summary")
        scored = []
        for s in summaries:
            if "semantic_embedding" in s:
                score = calculate_resonance(new_embedding, s["semantic_embedding"])
                if score > 0.7:
                    scored.append((score, s))
        return sorted(scored, key=lambda x: x[0], reverse=True)[:top_n]

    # ✨ 초월 발화 감지 시스템
    async def detect_transcendental_trigger(self, text):
        start_time = time.time()

        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": "이 문장이 인간 인식 경계를 넘는 주제를 포함합니까? 있다면 '초월', 없으면 '일반'으로 답하세요."}]
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": text}]
            }
        ]

        result = await do_task_async(messages=messages, model="gpt-4o")
        return result
