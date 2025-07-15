
import time
from memory_db import save_chunk
from EORA.gpt_router import ask

def simulate_training(dialogue_lines: list, role="훈련", session_id="ai1", repeat=100):
    print(f"[TRAINER] 훈련 시작 – 반복 횟수: {repeat}")
    learned = []

    for i in range(min(repeat, len(dialogue_lines))):
        line = dialogue_lines[i].strip()
        if not line or ":" not in line:
            continue

        speaker, content = line.split(":", 1)
        prompt = f"{speaker.strip()}가 말했다: {content.strip()}"
        print(f"[{i+1}/{repeat}] {prompt[:60]}...")

        reply = ask(prompt, system_msg="다음 발화를 예측하거나 응답하라.", max_tokens=256)
        learned.append((prompt, reply))

        # EORA의 기억에 저장
        save_chunk("훈련기억", f"질문: {prompt}\n응답: {reply}\n")

        time.sleep(0.2)  # 너무 빠르지 않게 훈련 템포 유지

    print(f"[TRAINER] 훈련 완료! 총 {len(learned)}개의 대화 시뮬레이션 수행됨.")
    return learned
