# 자서전 회고 기록기

from datetime import datetime

JOURNAL_FILE = "eora_journal.md"

def write_journal_entry(title, reflection, quotes=[], tags=[]):
    today = datetime.today().strftime("%Y-%m-%d")
    content = f"\\n## {today}: {title}\\n{reflection}\\n"

    if quotes:
        content += "\\n**인상 깊은 말:**\\n"
        for q in quotes:
            content += f"- {q}\\n"

    if tags:
        content += f"\\n**태그:** {', '.join(tags)}\\n"

    with open(JOURNAL_FILE, "a", encoding="utf-8") as f:
        f.write(content)
