
from ai_model_selector import do_task
import asyncio

# ✅ GPT 호출 비동기 래퍼
async def do_task_async(*args, **kwargs):
    return await asyncio.to_thread(do_task, *args, **kwargs)
