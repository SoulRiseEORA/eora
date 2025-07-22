
import json
import os

def summarize_session(session_path: str, summarize_func) -> str:
    try:
        if not os.path.exists(session_path):
            return "[대화 기록 없음]"

        with open(session_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        all_dialog = ""
        for item in data[-100:]:  # 최근 100개만
            all_dialog += f"👤 사용자: {item['user']}\n🤖 금강GPT: {item['reply']}\n"

        prompt = (
            "다음은 사용자와 금강GPT의 대화 기록입니다. "
            "전체 흐름과 핵심 내용을 간결하게 요약해주세요.\n\n" + all_dialog
        )

        summary = summarize_func(prompt)
        return summary

    except Exception as e:
        return f"[요약 실패: {str(e)}]"
