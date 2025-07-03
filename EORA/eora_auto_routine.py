"""
eora_auto_routine.py
EORA 자동 루프 감지 → 시뮬레이션 → 구조 개선 → 훈련 실행 자동화 모듈
"""
import subprocess
from .past_dialogue_simulator import simulate_past_conversations
from .loop_trainer import LoopTrainer

def run_automated_eora_routine():
    print("[EORA ROUTINE] 과거 대화 시뮬레이션 시작...")
    simulate_past_conversations()

    print("[EORA ROUTINE] 루프 훈련 루틴 구성...")
    trainer = LoopTrainer()
    trainer.add_step("진화 계획 적용")
    trainer.add_step("구조 회고 점검")
    trainer.add_step("자기 구조 재작성 판단")
    trainer.run()

    print("[EORA ROUTINE] 전체 루프 자동화 완료.")

if __name__ == "__main__":
    run_automated_eora_routine()