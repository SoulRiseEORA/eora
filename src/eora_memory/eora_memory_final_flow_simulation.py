"""
EORA 메모리 최종 통합 흐름 시뮬레이션
- 대화 입력
- 소주제 Two-Track 분석
- memory 저장
- sub_topic 기반 recall
- 기억 요약
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from eora_memory.sub_topic_two_track_selector import decide_subtopic
from eora_memory.sub_topic_memory_saver import save_memory_with_subtopic
from eora_memory.sub_topic_based_recaller import recall_chain_by_subtopic
from eora_memory.recall_summarizer import summarize_memory_chain
import random

# 가상의 사용자 입력 및 설정
user_msg = "이번 프로젝트의 색상 톤을 조금 더 부드럽게 하고 싶어요."
gpt_msg = "네, 기존보다 부드러운 톤 조정을 통해 감성적 느낌을 강화할 수 있습니다."
emotion = "positive"
belief_tags = ["감성강화", "톤조정"]
event_score = round(random.uniform(0.7, 0.95), 4)
session_id = "세션20250501-01"

# 1. 소주제 결정
final_subtopic = decide_subtopic(user_msg)

# 2. 메모리 저장
memory = save_memory_with_subtopic(
    user_msg=user_msg,
    gpt_msg=gpt_msg,
    emotion=emotion,
    belief_tags=belief_tags,
    event_score=event_score,
    final_subtopic=final_subtopic,
    session_id=session_id
)

print(f"✅ 메모리 저장 완료: {memory['sub_topic']}")

# 3. 소주제 기반 기억 연쇄 회상
chain = recall_chain_by_subtopic(final_subtopic, depth=5)

# 4. 기억 요약
if chain:
    summary = summarize_memory_chain(chain)
    print("\n🧠 회상 요약 결과:")
    print(summary)
else:
    print("⚡ 관련 기억 없음 (최초 저장)")