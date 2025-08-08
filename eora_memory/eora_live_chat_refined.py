"""
EORA 완전 실행본 - 자동 탐색 경로 안전 버전
"""

import os, sys, types, importlib.util, random
from bson import ObjectId

def dynamic_import(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

SRC_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EORA_DIR = os.path.join(SRC_DIR, "eora_memory")

# -------- locate file anywhere under src --------
def locate_file(filename):
    for r, _, files in os.walk(SRC_DIR):
        if filename in files:
            return os.path.join(r, filename)
    raise FileNotFoundError(filename)

# -------- ensure aura_system pkg patch ----------
mem_struct_path = locate_file("memory_structurer_advanced_emotion_code.py")
mem_struct_mod  = dynamic_import("memory_structurer_advanced_emotion_code", mem_struct_path)

if "aura_system" not in sys.modules:
    sys.modules["aura_system"] = types.ModuleType("aura_system")
sys.modules["aura_system.memory_structurer_advanced_emotion_code"] = mem_struct_mod

# -------- load remaining modules ----------------
emotion_integrator = dynamic_import("emotion_system_full_integrator",
                                    os.path.join(EORA_DIR, "emotion_system_full_integrator.py"))
complex_emotion   = dynamic_import("complex_emotion_encoder",
                                    os.path.join(EORA_DIR, "complex_emotion_encoder.py"))
emotion_recall    = dynamic_import("emotion_based_memory_recaller",
                                    os.path.join(EORA_DIR, "emotion_based_memory_recaller.py"))
recall_filter     = dynamic_import("refined_recall_filter",
                                    os.path.join(EORA_DIR, "refined_recall_filter.py"))
recall_validator  = dynamic_import("real_time_recall_validator",
                                    os.path.join(EORA_DIR, "real_time_recall_validator.py"))
reason_linker     = dynamic_import("memory_context_linker",
                                    os.path.join(EORA_DIR, "memory_context_linker.py"))
strength_linker   = dynamic_import("memory_link_strengthener",
                                    os.path.join(EORA_DIR, "memory_link_strengthener.py"))

def run_full_auto_session():
    print("💬 EORA (자동 탐색 실행 모드) 시작")
    while True:
        msg = input("\n👤 사용자: ")
        if msg.lower() == "exit":
            break
        rsp = input("🤖 GPT 응답: ")
        mem = emotion_integrator.save_enhanced_memory(msg, rsp)
        complex_emotion.save_memory_with_multiple_emotions(ObjectId(mem["_id"]))
        if random.random() < 0.05:
            emo = random.choice(["불안","기쁨","슬픔","분노"])
            raws = emotion_recall.recall_memories_by_emotion(emo)
            valids = recall_filter.clean_recall_list(msg, raws)
            for m in valids:
                if recall_validator.validate_recall(msg, m["summary_prompt"]):
                    print("✅ 회상:", m["summary_prompt"])
                    reason_linker.link_memory_with_reason(str(mem["_id"]), str(m["_id"]), f"감정({emo})")
                    strength_linker.strengthen_memory_link(str(mem["_id"]), str(m["_id"]), round(random.uniform(0.7,1.0),3))

if __name__ == "__main__":
    run_full_auto_session()