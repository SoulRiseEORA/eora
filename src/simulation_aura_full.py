"""
simulation_aura_full.py

AURA DB 시뮬레이션 스크립트 (ace_tools 제거 버전)
- ace_tools 의존성 제거
- 매 시나리오별 recalled 개수 및 파라미터를 콘솔에 출력
- 결과는 CSV 파일(scenario_results.csv)로 저장
"""

import os
import sys
import uuid
import datetime
import pandas as pd
from pymongo import MongoClient

# 프로젝트 src 폴더를 PYTHONPATH에 추가
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# EORA 모듈 import
from EORA.aura_multi_stage import multi_stage_selector
from EORA.eora_dynamic_params import decide_chat_params
from EORA.aura_structurer import store_memory_atom

# MongoDB 설정
client_db = MongoClient("mongodb://localhost:27017/")
db = client_db["EORA"]

# 시스템 메시지
SYSTEM_PROMPT = (
    "아래 [과거 대화 요약] 메시지는 참고하여, 필요하다고 판단되는 경우에만 답변에 반영하라. "
    "특히, 날씨/시간/장소/감정 등 맥락이 중요한 경우에는 과거 대화를 적극적으로 활용하라.\n"
    "아래 [과거 대화 요약] 사용자 질문이 1개 이상의 회상 답변을 요구 하는지 판단하여 대화에 필요하다고 판단되는 경우 1개 이상 3개까지 답변에 반영하라.\n"
    "너는 이오라(EORA)라는 이름을 가진 AI이며, 프로그램 자동 개발 시스템의 총괄 디렉터다."
)

# 테스트 시나리오 (예시)
scenarios = [
    "안녕, 오늘 날씨가 궁금해",
    "새로운 모바일 앱 기획 아이디어가 필요해",
    "파이썬으로 데이터 분석하는 방법 알려줘",
    "디버깅 중인 코드에서 IndexError를 해결해줘",
    "마케팅 캠페인 전략을 제안해줘",
    "CI/CD 파이프라인 구축하기",
    "머신러닝 모델의 과적합 문제를 해결하려면?",
    "보안 취약점 스캔 도구 추천",
    "UX 디자인 팁을 알려줘",
    "프로젝트 관리 도구 비교",
    # 필요에 따라 시나리오를 확장하세요 (최대 50개)
]

# 결과 수집용 리스트
results = []

for idx, user_input in enumerate(scenarios, 1):
    user_id = os.getenv("USER_ID", "default_user")
    conversation_id = str(uuid.uuid4())

    # 1) memory recall
    recalled_atoms = multi_stage_selector(user_id, user_input)
    recalled_count = len(recalled_atoms)
    recalled_texts = [atom["content"] for atom in recalled_atoms]

    # 2) 메시지 구성
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for txt in recalled_texts:
        messages.append({"role": "system", "content": txt})
    messages.append({"role": "user", "content": user_input})

    # 3) dynamic params 결정
    params = decide_chat_params(messages)
    temperature = params.get("temperature")
    top_p = params.get("top_p")

    # 4) GPT 호출 (모의 응답)
    response = f"[시뮬레이션 응답 for '{user_input}']"

    # 5) 로그 저장
    timestamp = datetime.datetime.utcnow()
    db.conversation_logs.insert_one({
        "conversation_id": conversation_id,
        "user_id": user_id,
        "messages": messages + [{"role": "assistant", "content": response, "timestamp": timestamp}],
        "params": params,
        "timestamp": timestamp
    })

    # 6) 메모리 저장
    store_memory_atom(
        user_id=user_id,
        conversation_id=conversation_id,
        content=response,
        source="assistant",
        timestamp=timestamp
    )

    # 결과 기록
    results.append({
        "scenario": user_input,
        "recalled": recalled_count,
        "temperature": temperature,
        "top_p": top_p
    })
    print(f"[{idx}/{len(scenarios)}] '{user_input}' → recalled: {recalled_count}, temp: {temperature}, top_p: {top_p}")

# DataFrame 생성 및 파일 저장
df = pd.DataFrame(results)
csv_path = os.path.join(ROOT_DIR, "scenario_results.csv")
df.to_csv(csv_path, index=False, encoding="utf-8-sig")
print(f"\n✅ 시뮬레이션 완료. 결과 CSV 저장: {csv_path}")
print(df.to_string(index=False))