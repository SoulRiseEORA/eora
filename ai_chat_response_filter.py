
import re

def clean_response(text: str) -> str:
    # 🚿 기본 필터링 예시
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
