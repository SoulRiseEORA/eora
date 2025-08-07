""" 회상 기반 응답 정확도 강화 버전 """

from datetime import datetime

# ✅ 회상 내용 포맷 (정확한 timestamp + user_input + response 출력)
def format_recall(atom: dict) -> str:
    try:
        ts = atom.get("timestamp", "")
        if isinstance(ts, datetime):
            ts = ts.strftime("%Y-%m-%d %H:%M:%S")
        text = atom.get("text") or atom.get("user_input") or "[텍스트 없음]"
        response = atom.get("response", "[응답 없음]")
        return f"📅 {ts}\n📌 요약: {text}\n🎯 응답: {response}"
    except Exception as e:
        return f"[RECALL FORMAT ERROR] {e}"

# ✅ GPT 시스템 프롬프트 생성 함수 (회상 반영 명령 강화)
def build_system_prompt(base_prompt: str, recall_blocks: list) -> str:
    if not recall_blocks:
        return base_prompt
    return (
        "[회상된 기억들]\n" +
        "\n".join(recall_blocks) +
        "\n\n[지시사항]\n"
        "- 위 회상 내용을 반드시 반영하여 대답하세요.\n"
        "- 회상 내용이 최신 입력보다 중요할 경우 회상 내용을 우선 고려하세요.\n"
        "- 회상 내용이 모호할 경우, 사용자의 최근 질문과 연결해서 답하세요.\n\n" +
        base_prompt
    )