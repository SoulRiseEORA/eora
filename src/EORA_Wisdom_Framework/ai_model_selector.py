import os
import sys
import time
import openai
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI

# 1) .env 탐색: 프로젝트 루트 -> src
script_dir = Path(__file__).resolve().parent
root_env = script_dir.parent / ".env"
src_env  = script_dir / ".env"
env_loaded = False  # ✅ Syntax 오류 수정: 여기서 줄바꿈 빠졌던 부분 수정

# ──────────────────────────────────────────────────────────
# 환경변수 로드
# ──────────────────────────────────────────────────────────
for env_path in (root_env, src_env):
    if env_path.exists():
        try:
            load_dotenv(dotenv_path=env_path)
            env_loaded = True
            break
        except PermissionError as e:
            continue
        except Exception as e:
            continue

if not env_loaded:
    print("❌ .env 파일을 찾을 수 없습니다.")
    sys.exit(1)

# 2) API 키 로드
api_key = os.getenv("OPENAI_API_KEY", "").strip()
if not api_key:
    sys.exit(1)

# 3) 클라이언트 초기화
openai.api_key = api_key
client = OpenAI(
    api_key=api_key,
    # proxies 인수 제거 - httpx 0.28.1 호환성
)  # ✅ OpenAI 1.7.0 이상 기준 project_id 제거


# ──────────────────────────────────────────────────────────
# 요청 메트릭 카운터
# ──────────────────────────────────────────────────────────
request_counter = 0

# ──────────────────────────────────────────────────────────
# GPT 호출 함수 (상세 로깅 포함)
# ──────────────────────────────────────────────────────────
def do_task(
    prompt=None,
    system_message=None,
    messages=None,
    model="gpt-4o",
    temperature=0.7,
    max_tokens=2048
):
    """
    GPT 호출 함수 (상세 로깅 포함)
    - prompt: 사용자 입력 (None 허용, messages 있을 때)
    - system_message: system 메시지
    - messages: 미리 구성된 메시지 리스트
    - model: 사용할 모델
    """
    global request_counter
    request_counter += 1

    if not any([prompt, system_message, messages]):
        raise ValueError("do_task 호출 시 prompt, system_message, messages 중 하나는 제공해야 합니다.")

    if messages is None:
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        if prompt:
            messages.append({"role": "user", "content": prompt})

    start_time = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    elapsed = time.time() - start_time

    print(f"[Metrics] Request #{request_counter:<3} | "
          f"Model={model:<8} | Temp={temperature:<4} | "
          f"MaxTokens={max_tokens:<5} | "
          f"Elapsed={elapsed:.3f}s")

    # 첫 번째 choice의 메시지 컨텐츠를 반환
    return response.choices[0].message.content

# ──────────────────────────────────────────────────────────
# 단순 호출 버전 (중복 정의 복원)
# ──────────────────────────────────────────────────────────
def do_task(prompt=None, system_message=None, messages=None,
            model="gpt-4o", temperature=0.7, max_tokens=2048):
    """
    GPT 호출 함수
    - prompt: 사용자 입력 (None 허용, messages 있을 때)
    - system_message: system 메시지
    - messages: 미리 구성된 메시지 리스트
    - model: 사용할 모델
    """
    if not any([prompt, system_message, messages]):
        raise ValueError("do_task 호출 시 prompt, system_message, messages 중 하나는 제공해야 합니다.")

    if messages is None:
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        if prompt:
            messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content


import asyncio
async def do_task_async(
    prompt=None,
    system_message=None,
    messages=None,
    model="gpt-4o",
    temperature=0.7,
    max_tokens=2048
):
    return await asyncio.to_thread(
        do_task,
        prompt=prompt,
        system_message=system_message,
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )
