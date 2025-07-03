from ai_model_selector import do_task
from ai_reward_manager import AIRewardManager
import json, os

class AIRouter:
    suppress_log = False  # ✅ 로그 억제용 설정 플래그

    def __init__(self):
        self.reward = AIRewardManager()
        self.prompts = self.reward.prompts  # ai_prompts.json 로딩

    def route_request(self, user_text, from_ai="ai0"):
        # 금강(ai0)이 요청을 받아 다른 AI에게 위임
        target_ai = self.select_ai(user_text)
        if not target_ai:
            return f"[금강GPT] '{user_text}' 에 대해 위임할 AI를 찾지 못했습니다."

        context_prompt = "\n".join(self.prompts.get(target_ai, [])[:5])
        prompt = f"[{target_ai} 응답 요청]\n질문: {user_text}\n프롬프트:\n{context_prompt}"

        print(f"🔁 {from_ai} → {target_ai} 요청 위임")
        answer = do_task(user_text, system_message=context_prompt)

        self.reward.record_feedback(target_ai, context_prompt, 5)  # 기본 점수
        return f"[{target_ai} 응답]\n{answer}"

    def select_ai(self, text):
        keywords = {
            "분석": "ai1", "요구": "ai1",
            "설계": "ai2", "UI": "ai2",
            "프롬프트": "ai3", "지시": "ai3",
            "오류": "ai4", "검사": "ai4",
            "성능": "ai5", "추천": "ai5"
        }
        for word, ai in keywords.items():
            if word in text:
                return ai
        return None  # 못 찾으면 금강 처리

    def route_recursive(self, text, depth=0):
        if depth > 2:
            return "[시스템] AI 위임 깊이 제한 도달"

        primary = self.select_ai(text)
        if not primary:
            return "[시스템] 위임 대상 AI를 찾지 못했습니다."

        prompt_lines = self.prompts.get(primary, [])
        if not prompt_lines:
            return f"[{primary}] 프롬프트가 존재하지 않습니다."

        core_prompt = "\n".join(prompt_lines[:5])
        response = do_task(text, system_message=core_prompt)

        if "ai" in response.lower() and ":" in response:
            subai, subtext = response.strip().split(":", 1)
            if subai.strip().lower().startswith("ai"):
                subai = subai.strip().lower()
                print(f"🔁 {primary} → {subai} 교차 위임")
                return self.route_recursive(subtext.strip(), depth + 1)

        return f"[{primary}] {response}"

    def detect_multi_ai(self, text):
        keywords = {
            "ai1": ["분석", "요구"],
            "ai2": ["설계", "UI"],
            "ai3": ["프롬프트", "지시"],
            "ai4": ["오류", "검사"],
            "ai5": ["성능", "추천"]
        }
        result = []
        for ai, keys in keywords.items():
            if any(k in text for k in keys):
                result.append(ai)
        if not getattr(self, "suppress_log", False):
            print(f"[ai_router] 탐지된 다중 AI 후보: {result}")
        return result

    def route_multi(self, text):
        ai_list = self.detect_multi_ai(text)
        if not ai_list:
            return "[시스템] 협업 가능한 AI를 찾지 못했습니다."

        results = []
        for ai_id in ai_list:
            prompt_lines = self.prompts.get(ai_id, [])
            if not prompt_lines:
                results.append(f"[{ai_id}] 프롬프트 없음")
                continue

            context_prompt = "\n".join(prompt_lines[:5])
            if not getattr(self, "suppress_log", False):
                print(f"🤝 {ai_id}에 협업 요청 중...")
            try:
                response = do_task(text, system_message=context_prompt)
                results.append(f"[{ai_id} 응답]\n{response}")
                self.reward.record_feedback(ai_id, context_prompt, 5)
            except Exception as e:
                results.append(f"[{ai_id} 오류]: {e}")

        return "\n\n".join(results)
