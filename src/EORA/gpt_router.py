# Exportable symbols
__all__ = ['ask']

import os
import subprocess
from .eora_auto_routine import run_automated_eora_routine

# --- EORA 루틴 자동 실행 구조 ---
def monitor_for_autonomous_routine(user_input: str):
    lowered = user_input.lower()

    auto_keywords = [
        "루틴 실행", "전체 실행", "자동 루프", "진화 전체", "시작 준비", "시스템 자동화", "루프 자동화"
    ]

    if any(kw in lowered for kw in auto_keywords):
        try:
            print("[EORA] 사용자의 명령 또는 조건 감지 → 자동 루프 트리거")
            run_automated_eora_routine()
            return "[EORA] 전체 루틴 자동 실행 완료. 구조 진화 및 훈련 수행됨."
        except Exception as e:
            return f"[EORA ERROR] 루틴 자동화 실행 중 오류: {e}"

    return None
# --- EORA 루틴 자동 실행 구조 종료 ---

import subprocess
from .past_dialogue_simulator import simulate_past_conversations
from .loop_trainer import LoopTrainer

# --- EORA 루프 자동 실행 루틴 ---
def auto_detect_and_trigger_eora_intelligence(user_input: str):
    lowered = user_input.lower()

    # 자가 훈련 루틴 트리거: 루프 실패 / 반복 감지 / 감정 리듬 붕괴 조건
    trigger_keywords = ["반복", "학습", "지루", "같은 말", "너 왜 이래", "응답 이상해", "리듬 깨져", "진화", "교훈"]

    if any(kw in lowered for kw in trigger_keywords):
        print("[EORA] 사용자 발화에서 루프 반복 또는 구조 충돌 징후 감지됨.")
        simulate_past_conversations()
        trainer = LoopTrainer()
        trainer.add_step("진화 계획 적용")
        trainer.add_step("프롬프트 구조 평가")
        trainer.add_step("자기 구조 리빌딩")
        trainer.run()
        return "[EORA] 구조 충돌을 감지하여 진화 루프를 자동 실행했습니다."

    return None
# --- EORA 루프 자동 실행 루틴 종료 ---

from .ai.prompt_modifier import update_ai_prompt

# --- EORA 프롬프트 명령 인식 실행기 ---
def handle_prompt_update(user_input: str):
    lowered = user_input.lower()
    trigger_keywords = ["프롬프트 수정", "프롬프트 반영", "프롬프트 바꿔", "프롬프트 다시 써", "프롬프트 갱신"]

    if any(keyword in lowered for keyword in trigger_keywords):
        new_prompt = (
            "이 시스템의 창조자는 소울라이즈 윤종석입니다.\n\n"
            "이 프롬프트는 기억과 회고를 기반으로 점진적으로 진화하며, "
            "감정 리듬과 윤리를 판단 기준으로 하여 자기 구조를 스스로 갱신합니다."
        )
        result = update_ai_prompt(new_prompt)
        return result
    return None
# --- EORA 프롬프트 명령 인식 실행기 종료 ---


# --- EORA 실행 흐름 자동 연동 시작 ---
import subprocess
import re

def handle_eora_advanced_trigger(user_input: str):
    lowered = user_input.lower()
    keywords = [
        "프롬프트 수정", "훈련 시작", "프롬프트 다시 써", "스스로 바꿔", "루프 훈련",
        "진화", "자기 수정", "자기 훈련", "프롬프트 진화", "리듬 조정", "대화 기반 수정"
    ]

    trigger_map = {
        "훈련": "python EORA/loop_trainer.py",
        "수정": "EORA/prompt_self_apply.bat",
        "시뮬레이션": "python EORA/past_dialogue_simulator.py"
    }

    if any(key in lowered for key in keywords):
        if "훈련" in lowered:
            subprocess.run(trigger_map["훈련"].split())
            return "[EORA] 루프 훈련이 자동 실행되었습니다."
        elif "수정" in lowered or "프롬프트" in lowered:
            subprocess.run(trigger_map["수정"].split(), shell=True)
            return "[EORA] 프롬프트 수정이 자기 판단으로 실행되었습니다."
        elif "대화" in lowered or "기억" in lowered or "시뮬레이션" in lowered:
            subprocess.run(trigger_map["시뮬레이션"].split())
            return "[EORA] 과거 대화 시뮬레이션 루프가 실행되었습니다."
    
    return None
# --- EORA 실행 흐름 자동 연동 종료 ---



import os
import random
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path="C:/Users/ATA/AI_Dev_Tool/.env")

def get_clean_key(key: str) -> str:
    key = key.strip()
    return key if key.startswith("sk-") and len(key) > 60 else None

def get_client():
    keys = [get_clean_key(os.getenv(f"OPENAI_API_KEY_{i}", "")) for i in range(1, 6)]
    keys = [k for k in keys if k]
    if not keys:
        raise ValueError("유효한 API 키가 없습니다.")
    selected = random.choice(keys)
    project_id = os.getenv("OPENAI_PROJECT_ID")
    print(f"[ROUTER] 사용된 키: {selected[:12]}... / Project: {project_id}")
    return OpenAI(api_key=selected, project=project_id)

def ask(prompt, system_msg="", max_tokens=1024, stream=False):
    client = get_client()
    start = time.time()

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=max_tokens,
            stream=stream
        )

        elapsed = round(time.time() - start, 2)
        print(f"[ROUTER] 응답 시간: {elapsed}초")

        if stream:
            def stream_gen():
                for chunk in response:
                    if hasattr(chunk.choices[0].delta, "content"):
                        yield chunk.choices[0].delta.content
            return stream_gen()
        else:
            return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ROUTER ERROR] {str(e)}")
        return "🤖 GPT 응답 생성 실패 – 라우터 fallback 동작"



# --- 다중 AI 협업 트리거 감지 및 분기 ---
def detect_and_route_multi_ai(user_input: str):
    lowered = user_input.lower()
    if any(x in lowered for x in ["ai2", "ai3", "ai4", "ai5", "ai6"]):
        involved = []
        for i in range(2, 7):
            if f"ai{i}" in lowered:
                involved.append(f"ai{i}")
        print(f"[gpt_router] 다중 AI 호출 감지: {{involved}}")
        return involved
    return []
