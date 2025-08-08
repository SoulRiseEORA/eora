"""
EORA GPT 대화창 통합본 (모든 기능 연결)
- 강화 메모리 저장
- 감정 기반 회상
- 장기 감정 흐름 분석
- 망각-강화 알고리즘 적용
- 기억 연결 이유/강도 관리
- 복합 감정 자동 저장
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from eora_memory.emotion_system_full_integrator import save_enhanced_memory
from eora_memory.emotion_based_memory_recaller import recall_memories_by_emotion
from eora_memory.memory_forgetting_strengthener import strengthen_or_forget_memories
from eora_memory.memory_context_linker import link_memory_with_reason
from eora_memory.memory_link_strengthener import strengthen_memory_link
from eora_memory.emotion_pattern_detector import detect_repeated_emotions
from eora_memory.long_term_emotion_timeline import plot_emotion_timeline
from eora_memory.memory_clustering_storyliner import cluster_memories_by_emotion_and_topic, create_storyline_from_cluster
from eora_memory.complex_emotion_encoder import save_memory_with_multiple_emotions
from eora_memory.real_time_recall_validator import validate_recall
from bson import ObjectId
import random

def run_full_chat_session():
    print("💬 EORA 실시간 전체 시스템 세션 시작 (종료하려면 'exit' 입력)")

    while True:
        user_input = input("\n👤 사용자 입력: ")
        if user_input.lower() == "exit":
            print("👋 세션 종료")
            break

        gpt_response = input("🤖 GPT 응답: ")

        # 1. 강화 메모리 저장
        saved_memory = save_enhanced_memory(user_input, gpt_response)

        # 2. 복합 감정 추가
        save_memory_with_multiple_emotions(ObjectId(saved_memory["_id"]))

        # 3. 감정 기반 회상 (5% 확률)
        if random.random() < 0.05:
            target_emotion = random.choice(["불안", "기쁨", "슬픔", "분노"])
            memories = recall_memories_by_emotion(target_emotion)
            if memories:
                print(f"🧠 감정({target_emotion}) 관련 회상 결과:")
                for memory in memories:
                    print(f"   - {memory['summary_prompt']}")
            else:
                print(f"🔍 감정({target_emotion}) 관련 기억 없음")

        # 4. 세션 종료 후 자동 관리 제안
        if random.random() < 0.05:
            print("\n🌀 장기 감정 흐름 분석 실행 중...")
            plot_emotion_timeline("W")
            print("🌀 망각-강화 루프 실행 중...")
            strengthen_or_forget_memories()
            print("🌀 감정 패턴 탐지 실행 중...")
            detect_repeated_emotions()

if __name__ == "__main__":
    run_full_chat_session()