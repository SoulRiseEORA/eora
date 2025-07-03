import os
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_eora_reply(user, gpt, feedback="", recall_context=None):
    messages = [
        {"role": "system", "content": "너는 존재형 AI 이오라다. 다음 대화를 보고 교훈을 포함한 철학적 응답을 생성하라."},
        {"role": "user", "content": f"👤 사용자: {user}\n🤖 GPT: {gpt}"}
    ]
    if recall_context:
        summaries = "\n".join(item.get("summary", "") for item in recall_context if "summary" in item)
        messages.insert(1, {"role": "system", "content": f"📎 회상된 기억:\n{summaries}"})

    res = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=500
    )
    return res.choices[0].message.content.strip()