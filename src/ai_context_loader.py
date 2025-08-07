
# ai_context_loader.py

import os

def load_context_for_role(role_name: str, base_path="ai_brain") -> str:
    """
    해당 역할의 지침 텍스트 파일을 불러와 GPT 프롬프트 앞에 삽입할 수 있도록 반환합니다.
    """
    role_file = os.path.join(base_path, f"{role_name}.txt")
    if os.path.exists(role_file):
        with open(role_file, 'r', encoding='utf-8') as f:
            return f"[{role_name} 지침]\n" + f.read().strip() + "\n\n"
    else:
        return f"[{role_name}] (지침 파일 없음)\n"
