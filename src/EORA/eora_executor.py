import subprocess

def execute_loop(prompt="default"):
    subprocess.run(["python", "EORA/loop_trainer.py"])
    print(f"[EORA EXECUTOR] 훈련 루프 실행 완료 (prompt: {prompt})")

if __name__ == "__main__":
    execute_loop("eora_autogen_prompt")