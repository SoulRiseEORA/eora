
import os
import json

# 기본 경로
CONFIG_DIR = os.path.join(os.path.dirname(__file__), "configs")
GUIDE_FILE = os.path.join(CONFIG_DIR, "gpts지침.txt")

def suggest_gpts_guidelines(phase: str, keyword: str = "") -> list:
    """
    phase: planning / generation / error_fix
    keyword: UI / DB / API 등 특정 주제 키워드
    """
    results = []

    try:
        with open(GUIDE_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            line_lower = line.lower()
            if phase in line_lower or keyword.lower() in line_lower:
                results.append(line.strip())

        if not results:
            results = [f"[지침 없음] '{phase}', '{keyword}' 관련된 문장은 찾지 못했습니다."]

        return results[:10]

    except Exception as e:
        return [f"[❌ 지침 로딩 실패]: {e}"]
