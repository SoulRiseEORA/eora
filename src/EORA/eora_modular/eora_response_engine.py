def generate_eora_reply(user, gpt, ai2=""):
    base = f"요청: {user[:30]}... | GPT: {gpt[:30]}..."
    if ai2:
        base += f" | AI2: {ai2[:30]}..."
    return base + " → 이오라: 기록 및 판단 완료"

def summarize_gpt_response(user, gpt):
    return gpt[:100] + ("..." if len(gpt) > 100 else "")
