import os
import json

class LoopTrainer:
    def __init__(self):
        self.steps = []
        self.memory = []

    def add_step(self, step):
        self.steps.append(step)

    def run(self, log_func=print):
        log_func("[EORA] 루프 훈련 시작")
        for step in self.steps:
            log_func(f"[LOOP] 실행 중: {step}")
        self.process_learning_input(log_func)
        self.generate_prompt_patch(log_func)
        log_func("[EORA] 루프 훈련 완료")

    def process_learning_input(self, log_func):
        try:
            if os.path.exists("EORA/learn_input.txt"):
                with open("EORA/learn_input.txt", "r", encoding="utf-8") as f:
                    content = f.read()
                summary = content[:300] + "..." if len(content) > 300 else content
                log_func("[회고] 입력 요약:")
                log_func(summary)
                self.memory.append(summary)
            else:
                log_func("[회고] 입력 없음.")
        except Exception as e:
            log_func(f"[ERROR] 학습 입력 처리 실패: {e}")

    def generate_prompt_patch(self, log_func):
        try:
            if not self.memory:
                log_func("[회고] 프롬프트 수정 생략 (메모리 없음)")
                return
            patch = {
                "modification": "system_prompt_update",
                "target": "ai1.prompt",
                "description": "최근 학습 내용을 기반으로 시스템 프롬프트를 개선",
                "additions": self.memory
            }
            with open("EORA/prompt_meta_patch.json", "w", encoding="utf-8") as f:
                json.dump(patch, f, ensure_ascii=False, indent=2)
            log_func("[회고] 프롬프트 수정 제안이 생성되었습니다.")
        except Exception as e:
            log_func(f"[ERROR] 프롬프트 패치 생성 실패: {e}")