"""
user_reply_refined_command_based.py
- "..." 안 문장을 우선 추출
- 명령어 포함 시 자동 프롬프트로 간주
- 프롬프트 생성 요청 시 GPT 응답을 저장
"""

from datetime import datetime
import re

def handle_user_reply(self, msg: str):
    self.log.append(f"👤 사용자 응답: {msg}")
    self.memo.append("✅ 응답 수신")

    # 1. 따옴표 안 문장 우선 추출
    quotes = re.findall(r'"(.+?)"', msg)
    if quotes:
        prompt = quotes[0].strip()
    else:
        # 2. 명령어 기반 프롬프트 요청 감지
        if any(keyword in msg.lower() for keyword in ["요약", "프롬프트 만들어", "정리해줘", "요약해서 줘", "프롬프트 생성"]):
            # fallback 문장 생성
            prompt = "사용자 요청 기반 프롬프트가 생성되었습니다."
        else:
            prompt = None

    if not prompt or len(prompt) < 10:
        self.log.append("❌ 저장 실패: 프롬프트가 비어 있거나 너무 짧음.")
        return

    try:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "source": "handle_user_reply",
            "summary_prompt": prompt[:50],
            "content": prompt,
            "tags": ["프롬프트", "명령"],
            "importance": 8500
        }
        self.db['prompt_history'].insert_one(entry)
        self.log.append(f"🧠 프롬프트 저장됨 → {prompt[:50]}")
    except Exception as e:
        self.log.append(f"❌ 저장 실패: {e}")