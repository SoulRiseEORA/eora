
from ai_chat_key import get_openai_client
from ai_chat_generator import do_task_async
from ai_chat_recall import perform_recall
from ai_chat_response_filter import clean_response
from ai_memory_wrapper import (
    create_memory_atom_async,
    insert_atom_async,
    embed_text_async
)
from EORA.prompt_storage_modifier import update_ai1_prompt
from EORA.eora_auto_prompt_trigger import EORATriggerAgent

import asyncio
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class AIChatRouter:
    def __init__(self, ai_key="ai1", memory_store=None):
        self.client = get_openai_client()
        self.ai_key = ai_key
        self.memory_store = memory_store
        self.faiss = None  # FAISS가 필요하면 여기에 추가
        self.recaller = EORATriggerAgent()  # 회상 트리거 조건용

    async def chat(self, context: str, user_prompt: str) -> str:
        if not context:
            logger.warning("❗ Context is empty. Recall and memory operations will be skipped.")
            return "⚠️ No context provided."

        # 🔁 1. 회상 수행
        recalled_memories = perform_recall(context)
        logger.info(f"🔄 Recalled Memories: {recalled_memories}")

        # 🧠 2. GPT 응답 생성
        response = await do_task_async(context + "\n" + user_prompt)
        cleaned = clean_response(response)
        logger.info(f"✅ GPT Response: {cleaned}")

        # 🧬 3. 메모리 저장
        try:
            atom = await create_memory_atom_async(user_prompt, cleaned, self.ai_key)
            await insert_atom_async(atom)
            logger.info("💾 Memory atom stored successfully.")
        except Exception as e:
            logger.error(f"⚠️ Memory storage failed: {e}")

        # 💡 4. 프롬프트 저장 조건 확인 후 저장
        if "프롬프트" in user_prompt or len(user_prompt.strip()) > 10:
            try:
                update_ai1_prompt(user_prompt)
                logger.info("📝 Prompt saved to DB.")
            except Exception as e:
                logger.warning(f"⚠️ Prompt saving failed: {e}")

        return cleaned
