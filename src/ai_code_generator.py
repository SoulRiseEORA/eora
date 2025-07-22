#!/usr/bin/env python
"""
ai_code_generator.py
--------------------
- 코드 생성 및 임시파일 실행
- gpt-4-turbo (is_conversation=False)
"""

import os
import asyncio
import subprocess
import tempfile
import time
# from openai import ... # 제거
from ai_model_selector import do_task_async

class AICodeGenerator:
    def __init__(self):
        self.generated_code = ""
        self.max_retries = 3

    async def generate_code_from_description(self, code_description: str) -> str:
        """
        "처음 학습/코드" => is_conversation=False => gpt-3.5
        """
        try:
            prompt = f"전문 코드 생성 AI입니다. 요구사항:\n{code_description}"
            print("🛑 [디버그] /mnt/data/full_src/src/ai_code_generator.py:28 → await 대상 함수 정의 누락 또는 호출 오류 가능")
            print("🛑 [디버그] /mnt/data/full_src/src/ai_code_generator.py:29 → do_task_async 호출됨 (정의 누락 또는 await 오류 가능)")
            # raise RuntimeError("🚨 강제 중단: do_task_async() 호출은 정의되지 않았거나 await 오류 발생 가능")
            code = await do_task_async(prompt, is_conversation=False)
            self.generated_code = f"# Generated code from: {code_description}\n{code}\n"
            return self.generated_code
        except Exception as e:
            print(f"[오류] 코드 생성 실패: {str(e)}")
            return ""

    def save_code_to_temp_file(self, code: str) -> str:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as tf:
                tf.write(code)
                temp_filename = tf.name
            print(f"임시 파일 저장 완료: {temp_filename}")
            return temp_filename
        except Exception as e:
            print(f"[오류] 임시 파일 저장 실패: {str(e)}")
            return ""

    def run_generated_code(self, file_path: str) -> bool:
        attempt = 0
        success = False
        while attempt < self.max_retries and not success:
            attempt += 1
            try:
                print(f"[시도 {attempt}] 실행: {file_path}")
                result = subprocess.run(["python", file_path],
                                        capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"[성공] (시도 {attempt}) => {result.stdout.strip()}")
                    success = True
                else:
                    print(f"[오류] (시도 {attempt}) => {result.stderr.strip()}")
                    self.auto_fix_errors(file_path)
            except subprocess.TimeoutExpired:
                print(f"[타임아웃] (시도 {attempt})")
                self.auto_fix_errors(file_path)
            time.sleep(1)
        return success

    def auto_fix_errors(self, file_path: str):
        try:
            with open(file_path, "r+", encoding="utf-8") as f:
                code = f.read()
                if "print(" not in code:
                    code = "# 자동 수정: print 함수 누락\n" + code
                    f.seek(0)
                    f.write(code)
                    f.truncate()
            print("[자동 오류 수정] 적용됨.")
        except Exception as e:
            print(f"[오류] 자동 수정 실패: {str(e)}")

if __name__ == "__main__":
    import sys
    async def main():
        gen = AICodeGenerator()
        desc = "Hello World 파이썬 코드"
        c = await gen.generate_code_from_description(desc)
        print("[코드]\n", c)
        tmp = gen.save_code_to_temp_file(c)
        success = gen.run_generated_code(tmp)
        print("[결과]", "성공" if success else "실패")

    asyncio.run(main())

# OpenAI 클라이언트 관련 import
from openai import OpenAI
import os
import json
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

def load_existing_session():
    return {}

import asyncio
import subprocess
import tempfile
import time
from ai_model_selector import do_task_async

class AICodeGenerator:
    def __init__(self):
        self.generated_code = ""
        self.max_retries = 3

    async def generate_code_from_description(self, code_description: str) -> str:
        try:
            prompt = f"전문 코드 생성 AI입니다. 요구사항:\n{code_description}"
            code = await do_task_async(prompt, is_conversation=False)
            self.generated_code = f"# Generated code from: {code_description}\n{code}\n"
            return self.generated_code
        except Exception as e:
            print(f"[오류] 코드 생성 실패: {str(e)}")
            return ""

    def save_code_to_temp_file(self, code: str) -> str:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as tf:
                tf.write(code)
                return tf.name
        except Exception as e:
            print(f"[오류] 임시 파일 저장 실패: {str(e)}")
            return ""

    def run_generated_code(self, file_path: str) -> bool:
        attempt = 0
        success = False
        while attempt < self.max_retries and not success:
            attempt += 1
            try:
                result = subprocess.run(["python", file_path],
                                        capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"[성공] (시도 {attempt}) => {result.stdout.strip()}")
                    success = True
                else:
                    print(f"[오류] (시도 {attempt}) => {result.stderr.strip()}")
                    self.auto_fix_errors(file_path)
            except subprocess.TimeoutExpired:
                print(f"[타임아웃] (시도 {attempt})")
                self.auto_fix_errors(file_path)
            time.sleep(1)
        return success

    def auto_fix_errors(self, file_path: str):
        try:
            with open(file_path, "r+", encoding="utf-8") as f:
                code = f.read()
                if "print(" not in code:
                    code = "# 자동 수정: print 함수 누락\n" + code
                    f.seek(0)
                    f.write(code)
                    f.truncate()
            print("[자동 오류 수정] 적용됨.")
        except Exception as e:
            print(f"[오류] 자동 수정 실패: {str(e)}")

def load_prompt(ai_key):
    path = os.path.join("ai_brain", "ai_prompts.json")
    if not os.path.exists(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            db = json.load(f)
        block = db.get(ai_key, {})
        return "\n".join([
            "[시스템]", block.get("system", ""),
            "[역할]", block.get("role", ""),
            "[지침]", block.get("guide", ""),
            "[양식]", block.get("format", "")
        ])
    except Exception as e:
        return f"[프롬프트 오류: {str(e)}]"

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
    return OpenAI(
        api_key=api_key,
        # proxies 인수 제거 - httpx 0.28.1 호환성
    )

class BaseGPT:
    def __init__(self, ai_key, model=None, temp=None):
        self.ai_key = ai_key
        self.model = model or os.getenv("GPT_MODEL", "gpt-4")
        self.temp = float(os.getenv("TEMPERATURE", "0.7"))
        self.system_prompt = load_prompt(ai_key)
        self.client = get_openai_client()

    def ask(self, user_input, chat_history=[]):
        messages = [{"role": "system", "content": self.system_prompt}]
        for turn in chat_history[-5:]:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["reply"]})
        messages.append({"role": "user", "content": user_input})

        try:
            res = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temp
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            return f"❌ GPT 호출 실패: {str(e)}"

class AI1(BaseGPT):
    def __init__(self):
        super().__init__("ai1")

class AI2(BaseGPT):
    def __init__(self):
        super().__init__("ai2")

class AI3(BaseGPT):
    def __init__(self):
        super().__init__("ai3")

class AI4(BaseGPT):
    def __init__(self):
        super().__init__("ai4")

class AI5(BaseGPT):
    def __init__(self):
        super().__init__("ai5")

class AI6(BaseGPT):
    def __init__(self):
        super().__init__("ai6")

EORAAI = AI1

if __name__ == "__main__":
    async def main():
        gen = AICodeGenerator()
        desc = "Hello World 파이썬 코드"
        c = await gen.generate_code_from_description(desc)
        print("[코드]\n", c)
        tmp = gen.save_code_to_temp_file(c)
        success = gen.run_generated_code(tmp)
        print("[결과]", "성공" if success else "실패")

    asyncio.run(main())
