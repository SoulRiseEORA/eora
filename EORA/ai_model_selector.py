import os
import sys
import time
import openai
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI

# 1) .env 탐색: 프로젝트 루트 -> src
script_dir = Path(__file__).resolve().parent
root_env = script_dir.parent / ".env"
src_env  = script_dir / ".env"
env_loaded = False  # ✅ Syntax 오류 수정: 여기서 줄바꿈 빠졌던 부분 수정

# ──────────────────────────────────────────────────────────
request_counter = 0

# GPT 호출 함수 (상세 로깅 포함)
# ──────────────────────────────────────────────────────────
def do_task(
    prompt=None,
    system_message=None,
    messages=None,
    model="gpt-4o",
    temperature=0.7,
    max_tokens=2048
):
    global request_counter
    request_counter += 1

    if not any([prompt, system_message, messages]):
        raise ValueError("do_task 호출 시 prompt, system_message, messages 중 하나는 제공해야 합니다.")

    if messages is None:
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        if prompt:
            messages.append({"role": "user", "content": prompt})

    start_time = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    elapsed = time.time() - start_time

    print(f"[Metrics] Request #{request_counter:<3} | "
          f"Model={model:<8} | Temp={temperature:<4} | "
          f"MaxTokens={max_tokens:<5} | "
          f"Elapsed={elapsed:.3f}s")

    return response.choices[0].message.content

# ✅ 비동기 대응용 wrapper
import asyncio
async def do_task_async(*args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: do_task(*args, **kwargs))

