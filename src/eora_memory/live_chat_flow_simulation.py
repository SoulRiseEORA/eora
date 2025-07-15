"""
EORA 실시간 대화 흐름 통합 시뮬레이션
- 대화 입력
- 감정+신념+강화 메모리 저장
- 특정 감정 기반 기억 회상 자동 연결
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
from eora_memory.emotion_system_full_integrator import save_enhanced_memory
from eora_memory.emotion_based_memory_recaller import recall_memories_by_emotion
import random

def simulate_chat_turn(user_msg, gpt_response, session_id="세션20250502-01"):
    print(f"👤 사용자: {user_msg}")
    print(f"🤖 GPT 응답: {gpt_response}")

    # 대화 끝나면 강화 메모리 저장
    save_enhanced_memory(user_msg, gpt_response)

    # 확률적으로 감정 기반 회상 시도 (30% 확률)
    if random.random() < 0.3:
        target_emotion = random.choice(["불안", "기쁨", "슬픔", "분노"])
        memories = recall_memories_by_emotion(target_emotion)
        if memories:
            print(f"🧠 감정({target_emotion}) 관련 회상 결과:")
            for memory in memories:
                print(f"   - {memory['summary_prompt']}")
        else:
            print(f"🔍 감정({target_emotion}) 관련 기억 없음")

if __name__ == "__main__":
    while True:
        user_input = input("\n👤 사용자 입력 (종료는 'exit'): ")
        if user_input.lower() == "exit":
            print("👋 종료합니다.")
            break

        gpt_response = input("🤖 GPT 응답 입력: ")
        simulate_chat_turn(user_input, gpt_response)