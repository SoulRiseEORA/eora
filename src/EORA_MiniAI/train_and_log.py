
from ir_core import simulate_intuition
from datetime import datetime

def run_training_session():
    accuracy, used = simulate_intuition()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    log = f"[{now}] 정확도: {accuracy}, 응답 수: {used}\n"

    with open("training_log.txt", "a", encoding="utf-8") as f:
        f.write(log)
    print(log)

if __name__ == "__main__":
    run_training_session()
