
import json
import os
from datetime import datetime

PROMPT_DB = "ai_prompts.json"
REWARD_LOG = "ai_reward_log.json"

class AIRewardManager:
    def __init__(self):
        self.prompts = self.load_prompts()
        self.reward_data = self.load_rewards()

    def load_prompts(self):
        if os.path.exists(PROMPT_DB):
            with open(PROMPT_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def load_rewards(self):
        if os.path.exists(REWARD_LOG):
            with open(REWARD_LOG, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def record_feedback(self, ai_name, prompt, score):
        now = datetime.now().isoformat()
        self.reward_data.setdefault(ai_name, []).append({
            "prompt": prompt, "score": score, "time": now
        })
        self.save_rewards()

    def save_rewards(self):
        with open(REWARD_LOG, "w", encoding="utf-8") as f:
            json.dump(self.reward_data, f, indent=2, ensure_ascii=False)

    def evaluate_prompts(self, ai_name):
        scored = self.reward_data.get(ai_name, [])
        if not scored:
            return []
        scores = {}
        for item in scored:
            p = item["prompt"]
            scores[p] = scores.get(p, 0) + item["score"]
        ranked = sorted(scores.items(), key=lambda x: -x[1])
        return [p for p, _ in ranked[:5]]

    def recommend_prompt(self, ai_name):
        best = self.evaluate_prompts(ai_name)
        if best:
            print(f"🔁 [추천 프롬프트: {ai_name}]")
            for p in best:
                print("-", p)
        else:
            print(f"⚠️ {ai_name}에 대한 평가 기록이 없습니다.")
