from aura_memory_service import recall_memory

def recall_related_memories(self, user_text):
    recall_hits = []
    try:
        recalled_atoms = recall_memory(user_text)
        for item in recalled_atoms:
            summary = item.get("summary", "")
            score = item.get("resonance_score", 0.0)
            kw = item.get("trigger_keywords", [])
            line = f"📎 회상됨: {','.join(kw)} → {summary[:80]} (공명 {score:.2f})"
            recall_hits.append(line)
    except Exception as e:
        recall_hits.append(f"⚠️ 회상 실패: {str(e)}")
    return recall_hits[:3]