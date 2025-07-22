
from session_memory import update_context, get_context
from memory_db import save_chunk
from memory_loader import load_memory_chunks
from gpt_router import ask
import time

def auto_reply(user_input: str, session_id: str = "ai1", system_prompt: str = "", stream=False) -> str:
    recent_chunks = load_memory_chunks("최근시스템기억")
    recent_prompt = "\n".join(recent_chunks[:5]) if recent_chunks else ""

    if not system_prompt:
        system_prompt = get_context(session_id)

    # ✅ 분석 내용 + 질문을 합친 user prompt 생성
    enhanced_prompt = f"""아래는 첨부된 파일의 자동 분석 내용입니다. 이 내용을 반드시 반영하여 대답하세요.

[분석 요약]
{recent_prompt}

[사용자의 질문]
{user_input}
"""

    print(f"🧠 {session_id} system memory 줄 수: {len(system_prompt.splitlines())}")
    print(f"🧠 {session_id} system memory 길이: {len(system_prompt)}자")

    max_tokens = 512
    if len(user_input) > 800 or len(recent_prompt) > 2000:
        max_tokens = 400
    elif len(user_input) > 1500:
        max_tokens = 300

    reply = ask(
        prompt=enhanced_prompt,
        system_msg=system_prompt,
        stream=stream,
        max_tokens=max_tokens
    )

    print("[DEBUG] GPT 응답 내용:", reply[:300])
    print("[DEBUG] 응답 길이:", len(reply))

    if reply:
        save_chunk("대화학습", reply)

    update_context(session_id, system_prompt)
    return reply if reply else "🤖 GPT가 응답을 생성하지 못했습니다."
