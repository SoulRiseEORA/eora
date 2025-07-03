from aura_system.vector_store import embed_text
from aura_system.resonance_engine import estimate_emotion, extract_belief_vector, calculate_resonance
from datetime import datetime
import os

# ✅ 첨부 학습 내용을 회상 가능한 메모리 형태로 저장
def send_attachment_to_db(filename, db, callback=None):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            text = f.read()

        # 기본 요약 처리
        summary = text[:500].strip().replace("\n", " ") if len(text) > 500 else text.strip()
        embedding = embed_text(text)
        belief = extract_belief_vector(text)
        resonance = calculate_resonance(embedding, embed_text(summary))
        emotion = estimate_emotion(text)

        memory = {
            "user": "[첨부파일]",
            "gpt": "[첨부파일 요약]",
            "eora": summary,
            "summary": summary,
            "importance": 0.85,
            "emotion_score": emotion,
            "resonance_score": resonance,
            "belief_vector": belief,
            "semantic_embedding": embedding,
            "timestamp": datetime.utcnow(),
            "type": "aura_memory",
            "source": os.path.basename(filename),
            "chain_id": os.path.basename(filename),
            "linked_ids": []
        }

        db["memory_atoms"].insert_one(memory)
        if callback:
            callback(f"✅ 첨부 학습 저장 완료: {filename}")
    except Exception as e:
        if callback:
            callback(f"❌ 첨부 저장 실패: {e}")