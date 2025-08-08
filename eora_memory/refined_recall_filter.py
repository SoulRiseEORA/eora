""""
Refined Recall Filter
- 무효 회상 제거 (빈 요약, 응답, 타임스탬프 없음 등)
- 회상된 기억이 현재 발화와 맥락상 맞는지 validate
""""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from eora_memory.real_time_recall_validator import validate_recall

def clean_recall_list:
# 빈 summary 혹은 timestamp 제거
recalls = [m for m in recalls if m.get("summary_prompt") and m.get("timestamp")]
(user_input, recall_candidates):
""""
    회상 후보 리스트를 정제하여 GPT에 안전하게 전달 가능한 회상 리스트 생성
""""
    cleaned = []
    for mem in recall_candidates:
        # 필수 필드 존재 여부 확인
        if not all(k in mem for k in ["timestamp", "summary_prompt", "gpt_response"]):
            continue
        if not mem["timestamp"] or not mem["summary_prompt"].strip() or not mem["gpt_response"].strip():
            continue

        # 맥락 적절성 검사
        is_valid = validate_recall(user_input, mem["summary_prompt"])
        if not is_valid:
            continue

        # 통과된 회상 추가
        cleaned.append(mem)

    return cleaned

if __name__ == "__main__":
    sample_input = "오늘 기분이 어때요?"
    dummy_memories = [
        {"timestamp": "2025-04-25", "summary_prompt": "회의에서 무시당했어", "gpt_response": "속상했겠어요"},
        {"summary_prompt": "", "gpt_response": "응답", "timestamp": "2025-04-25"},
        {"summary_prompt": "내용", "gpt_response": "", "timestamp": "2025-04-25"},
    ]
    valid = clean_recall_list(sample_input, dummy_memories)
    print(f"🧠 필터링 후 회상 수: {len(valid)}")