import os
import sys
import time
import openai
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI
from tiktoken import encoding_for_model

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
            print(f"🔄 Loaded .env from: {env_path}")
            env_loaded = True
            break
        except PermissionError as e:
            print(f"⚠️ .env 파일 읽기 권한 없음: {env_path} ({e})", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ .env 로드 실패 ({env_path}): {e}", file=sys.stderr)

if not env_loaded:
    print("⚠️ Warning: .env 파일을 찾거나 로드하지 못했습니다. 환경 변수를 확인하세요.", file=sys.stderr)

# 2) API 키 로드
api_key = os.getenv("OPENAI_API_KEY", "").strip()
if not api_key:
    print("❌ OPENAI_API_KEY가 설정되지 않았습니다. .env 또는 시스템 환경 변수를 확인하세요.", file=sys.stderr)
    sys.exit(1)

# 3) 클라이언트 초기화
openai.api_key = api_key
client = OpenAI(
    api_key=api_key,
    # proxies 인수 제거 - httpx 0.28.1 호환성
)  # ✅ OpenAI 1.7.0 이상 기준 project_id 제거

print("✅ OpenAI API 키 로드 완료")

# ──────────────────────────────────────────────────────────
# 요청 메트릭 카운터
# ──────────────────────────────────────────────────────────
request_counter = 0

# ──────────────────────────────────────────────────────────
# GPT 호출 함수 (상세 로깅 포함)
# ──────────────────────────────────────────────────────────

# 토큰 계산을 위한 인코더 초기화
enc = encoding_for_model("gpt-3.5-turbo")

def count_tokens(text: str) -> int:
    """텍스트의 토큰 수를 계산"""
    try:
        return len(enc.encode(text))
    except Exception:
        return len(text.split()) * 1.3

def count_message_tokens(messages: list) -> int:
    """메시지 리스트의 총 토큰 수를 계산"""
    total = 0
    for msg in messages:
        if isinstance(msg.get("content"), str):
            total += count_tokens(msg["content"])
    return total

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

    # 토큰 수 계산 및 제한
    total_tokens = count_message_tokens(messages)
    if total_tokens > 6000:  # 안전 마진을 두고 제한
        print(f"⚠️ 경고: 메시지 토큰 수({total_tokens})가 너무 큽니다. 일부 메시지가 제거될 수 있습니다.")
        # 시스템 메시지는 유지하고 나머지 메시지 제한
        system_msg = messages[0] if messages and messages[0]["role"] == "system" else None
        filtered_messages = [system_msg] if system_msg else []
        current_tokens = count_tokens(system_msg["content"]) if system_msg else 0
        
        for msg in messages[1:]:
            msg_tokens = count_tokens(msg["content"])
            if current_tokens + msg_tokens > 6000:
                break
            filtered_messages.append(msg)
            current_tokens += msg_tokens
        
        messages = filtered_messages

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
          f"InputTokens={total_tokens:<5} | "
          f"Elapsed={elapsed:.3f}s")

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
