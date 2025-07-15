from memory_manager import select_top_recall_summaries
from EORA.aura_trigger import detect_recall_trigger
from eora_memory.recall_suggester import suggest_recall
from EORA.eora_modular.recall_memory_with_enhancements import recall_memory_with_enhancements


def recall_memory_full_pipeline(user_input: str, memory_manager, trigger_check=True) -> list:
    """
    속도 개선된 회상 파이프라인:
    - GPT 없이 빠르게 판단
    - 트리거 조건 기반 실행
    """
    if trigger_check and not detect_recall_trigger(user_input):
        return []

    recall_hits = recall_memory_with_enhancements(user_input, memory_manager)
    if not recall_hits:
        return []

    approved = []
    for m in recall_hits:
        if suggest_recall([m], user_input):
            approved.append(m)

    # ✅ 요약 정렬 및 전송 제한 적용
    # GPT에 보낼 때는 중요도 순으로 3000자 내에서 자르기
    approved = [{"summary": s} for s in select_top_recall_summaries(approved)]

    return approved
    """
    속도 개선된 회상 파이프라인:
    - GPT 없이 빠르게 판단
    - 트리거 조건 기반 실행
    """
    if trigger_check and not detect_recall_trigger(user_input):
        return []

    recall_hits = recall_memory_with_enhancements(user_input, memory_manager)
    if not recall_hits:
        return []

    approved = []
    for m in recall_hits:
        if suggest_recall([m], user_input):
            approved.append(m)

    return approved