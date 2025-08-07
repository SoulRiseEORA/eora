
import os

TARGETS = [
    "run_test_gpt4o_goldgpt.py",
    "run_test_gpt4o_goldgpt_casefix.py",
    "run_test_gpt4o_goldgpt_final.py",
    "run_test_gpt4o_goldgpt_fixed.py",
    "run_test_gpt4o_goldgpt_protected.py",
    "run_test_gpt4o_goldgpt_safe.py",
    "run_test_gpt4o_goldgpt_syncfix.py",
    "test_env_check.py"
]

for fname in TARGETS:
    path = os.path.join(".", fname)
    if os.path.exists(path):
        try:
            os.remove(path)
            print(f"🗑️ 삭제됨: {fname}")
        except Exception as e:
            print(f"⚠️ 삭제 실패: {fname} - {e}")
    else:
        print(f"✅ 없음: {fname}")
