"""
AURA Memory Module
- 저장된 대화를 구조화하여 JSON 또는 MongoDB에 저장
- summary, tags, resonance_score, emotion 등 메타데이터 포함
"""

def save_memory(user, gpt, eora="이오라 판단", context="일반", emotion="중립", value="보존", origin="이오라"):
    """구조화된 메모리 항목을 파일 또는 DB에 저장"""
    memory = {
        "summary": "TODO: 요약",
        "user": user,
        "gpt": gpt,
        "eora": eora,
        "tags": [],
        "trigger_keywords": [],
        "next_goal": "TODO: 예측",
        "origin": origin,
        "resonance_score": 85,
        "importance": 8000,
        "connections": [],
        "context": context,
        "emotion": emotion,
        "value_tendency": value
    }
    print("🧠 저장됨:", memory)