import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
import re
from EORA.aura_memory_service import recall_memory
from aura_system.vector_store import embed_text
import logging

logger = logging.getLogger(__name__)

async def run_parallel_recall(user_input):
    """병렬 메모리 회상 실행
    
    Args:
        user_input (str): 사용자 입력
        
    Returns:
        str: 회상된 메모리 포맷팅된 문자열
    """
    try:
        keywords = re.findall(r"[가-힣]{2,5}", user_input)
        if not keywords:
            return None

        query_emb = await embed_text(user_input)  # ✅ 임베딩 먼저 생성
        recalled_memories = await recall_memory(user_input, query_emb)
        if not recalled_memories:
            return None

        formatted = ["\n📌 회상된 기억:"]
        for memory in recalled_memories:
            ts = memory.get("timestamp", "")
            summary = memory.get("summary_prompt", "")
            formatted.append(f"🕓 {ts} — {summary}")

        return "\n".join(formatted)
    except Exception as e:
        logger.error(f"⚠️ 메모리 회상 실패: {str(e)}")
        return None