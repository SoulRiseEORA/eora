import asyncio
import nest_asyncio
from EORA.eora_modular.recall_memory_with_enhancements import recall_memory_with_enhancements

def perform_recall(context):
    """
    회상 기능을 동기 컨텍스트에서 안전하게 비동기적으로 호출합니다.
    """
    query = context.get("query") or context.get("user_input") or ""
    if not query.strip():
        return []
    # nest_asyncio를 적용하여 중첩 이벤트 루프를 허용합니다.
    nest_asyncio.apply()
    
    # 현재 스레드의 이벤트 루프를 가져옵니다.
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # 비동기 함수를 실행하고 결과를 반환합니다.
    # context에서 실제 쿼리 텍스트를 추출해야 합니다.
    return loop.run_until_complete(recall_memory_with_enhancements(query, context))
