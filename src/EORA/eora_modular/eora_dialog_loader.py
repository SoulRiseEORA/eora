from docx import Document
import re

def load_dialog_lines(path):
    """
    - 시스템 메시지를 제거하고
    - 반드시 나의 말 → GPT의 말 순서로만 매칭하여 대화 쌍 구성
    """
    if path.endswith(".docx"):
        doc = Document(path)
        text = "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
    else:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

    # 시스템 메시지 제거 (Welcome back 등)
    if text.lower().startswith("welcome") or "ChatGPT의 말:" not in text:
        text = re.sub(r"^.*?(나의 말:)", r"\1", text, flags=re.DOTALL)

    # 나의 말 / ChatGPT의 말로 분리
    pattern = r"(나의 말:|ChatGPT의 말:)"
    segments = re.split(pattern, text)
    segments = [s.strip() for s in segments if s.strip()]

    users, gpts = [], []
    i = 0
    while i < len(segments) - 1:
        if segments[i] == "나의 말:" and i + 2 < len(segments) and segments[i+2] == "ChatGPT의 말:":
            users.append(segments[i+1].strip())
            gpts.append(segments[i+3].strip() if i+3 < len(segments) else "")
            i += 4
        else:
            i += 1

    return users, gpts