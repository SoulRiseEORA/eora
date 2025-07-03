import json
import os

STATE_FILE = "macro_resume_state.json"

def save_execution_state(step: str, context: dict):
    """실행 중단 시 상태 저장"""
    state = {
        "last_step": step,
        "context": context
    }
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_execution_state():
    """재시작 시 상태 불러오기"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def clear_execution_state():
    """완료 후 상태 삭제"""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
