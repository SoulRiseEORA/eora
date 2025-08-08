"""
EORA 감정+신념+메모리 통합 시스템 (언팩 오류 완전 수정)
원본 로직 유지, 경로 보강
"""

import sys, os, importlib.util, types, random, datetime
from pymongo import MongoClient

# ── 경로 보강 ─────────────────────────────
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (
    SRC_DIR,
    os.path.join(SRC_DIR, "belief_memory_engine"),
    os.path.join(SRC_DIR, "emotion_system"),
):
    if p not in sys.path:
        sys.path.insert(0, p)
# ─────────────────────────────────────────

from aura_system.memory_structurer_advanced_emotion_code import create_memory_atom
from belief_detector      import extract_belief_phrases
from belief_reframer      import suggest_reframe
from emotion_logic_module import estimate_emotion
from emotion_system.memory_structurer_advanced_emotion_code import EMOTION_CODE_MAP

mongo_client = MongoClient("mongodb://localhost:27017")
collection   = mongo_client["aura_memory"]["memory_atoms"]

def save_enhanced_memory(user_input: str, gpt_response: str, origin_type="user"):
    # estimate_emotion 은 2값(label, score) 또는 3값(label, code, score) 반환
    tmp = estimate_emotion(user_input)
    if len(tmp) == 3:
        emo_label, emo_code, emo_score = tmp
    else:
        emo_label, emo_score = tmp
        emo_code = EMOTION_CODE_MAP.get(emo_label, {}).get("code", "EXXX")

    detected_belief = extract_belief_phrases(user_input)
    reframed_belief = suggest_reframe(detected_belief) if detected_belief else None

    memory = create_memory_atom(user_input, gpt_response, origin_type)

    # 보정: summary_prompt / timestamp 비어 있으면 기본값 세팅
    if not memory.get("summary_prompt", "").strip():
        memory["summary_prompt"] = (memory.get("gpt_response") or "…")[:120]
    if not memory.get("timestamp"):
        memory["timestamp"] = datetime.datetime.utcnow().isoformat()

    memory.update(
        {
            "emotion_label":   emo_label,
            "emotion_code":    emo_code,
            "emotion_score":   emo_score,
            "belief_detected": detected_belief,
            "belief_reframed": reframed_belief,
        }
    )

    _id = collection.insert_one(memory).inserted_id
    print(f"✅ 메모리 저장 완료 (감정: {emo_label}, 신념: {detected_belief or '없음'})")
    return {**memory, "_id": _id}

# ── 단독 실행 테스트 ─────────────────────
if __name__ == "__main__":
    ui = input("👤 사용자 입력: ")
    gr = input("🤖 GPT 응답: ")
    save_enhanced_memory(ui, gr)
