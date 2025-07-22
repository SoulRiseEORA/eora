
import os
import re

def load_ai_brain_prompt(ai_key: str, base_path="ai_brain"):
    path = os.path.join(base_path, f"{ai_key}.txt")
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    result = {"system": "", "instruction": "", "role": "", "opinion": "", "temperature": ""}
    sections = re.split(r"\[([a-zA-Z_]+)\]", text)
    for i in range(1, len(sections), 2):
        key = sections[i].lower().strip()
        val = sections[i + 1].strip()
        if key in result:
            result[key] = val
    return result
