from docx import Document

def load_dialog_lines(path):
    """
    워드(.docx), 텍스트(.txt), 마크다운(.md) 파일에서 사용자-GPT 대화 라인 분리
    - 기준: "나의 말:", "ChatGPT의 말:"
    - 시스템 메시지, 중복 응답 제거
    """
    if path.endswith(".docx"):
        doc = Document(path)
        lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    else:
        with open(path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]

    users, gpts = [], []
    user_line, gpt_line = "", ""

    for line in lines:
        if line.startswith("나의 말:"):
            if user_line and gpt_line:
                users.append(user_line.strip())
                gpts.append(gpt_line.strip())
                user_line, gpt_line = "", ""
            user_line = line.replace("나의 말:", "").strip()

        elif line.startswith("ChatGPT의 말:"):
            gpt_line = line.replace("ChatGPT의 말:", "").strip()

        elif user_line and not gpt_line:
            user_line += " " + line.strip()
        elif gpt_line:
            gpt_line += " " + line.strip()

    # 마지막 잔여 발화 처리
    if user_line and gpt_line:
        users.append(user_line.strip())
        gpts.append(gpt_line.strip())

    return users, gpts