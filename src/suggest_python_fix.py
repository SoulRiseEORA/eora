
import os
import re
import json
import traceback
from collections import defaultdict
import openai

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "configs")
GUIDELINE_TXT = os.path.join(CONFIG_DIR, "gpts지침.txt")
PYTHON_XLSX = os.path.join(CONFIG_DIR, "파이썬 교재.xlsx")
COBOT_XLSX = os.path.join(CONFIG_DIR, "코봇_기능_6000개_점수정밀최종.xlsx")

error_count = defaultdict(int)

GPT_PROMPT = (
    "모든 코드는 파이썬에서 IndentationError, SyntaxError, NameError가 절대 발생하지 않도록 "
    "줄 하나하나를 수기로 점검해 작성해줘. 각 블록은 들여쓰기 4칸으로 고정하고, "
    "조건문/반복문 뒤에는 최소한 pass 또는 기본 실행 코드를 포함해줘. "
    "실행 가능한 완성 파일로 만들어줘."
)

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:  # 자동 수정됨
        print("오류 발생:", e)
        return ""

def suggest_python_fix(error_msg: str, faulty_code: str, project_name="default") -> str:
    # global error_count  # global 제거됨 (검토 필요)
    key = error_msg.strip().split("\n")[-1][:60]
    error_count[key] += 1
    count = error_count[key]

    prefix = f"[에러 #{count}]\n"
    detail_log = f"에러메시지: {error_msg}\n"

    try:
        guideline = read_file(GUIDELINE_TXT)
        context = f"## 참고 지침:\n{guideline[:1500]}"

        if 3 <= count < 10:
            context += f"\n\n📘 파이썬 교재 참조 권장: {PYTHON_XLSX}"
        elif count >= 10:
            context += f"\n\n🚨 동일 에러 반복 → 기존 코드 삭제. 기능설계서 기반 재작성 권장: {COBOT_XLSX}"

        messages = [
            {"role": "system", "content": GPT_PROMPT + "\n" + context},
            {"role": "user", "content": f"이 코드를 수정해줘:\n\n{faulty_code}\n\n에러: {error_msg}"}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.3
        )
        fixed_code = response['choices'][0]['message']['content']
        return prefix + fixed_code
    except Exception as e:
        return prefix + f"[❌ GPT 요청 실패]\n{traceback.format_exc()}"