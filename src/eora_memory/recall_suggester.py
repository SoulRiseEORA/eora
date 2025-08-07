"""
EORA 회상 제안 시스템 (간소화 버전)
- GPT 호출 없이 빠르게 판단
"""

def suggest_recall(memory_list, user_message):
    """
    회상 후보 중 event_score > 0.75 및 summary 존재 시 허용
    """
    for memory in memory_list:
        summary = memory.get("summary", "")
        if memory.get("event_score", 0) > 0.75 and summary and "[요약 자동 생성]" not in summary:
            return True
    return False