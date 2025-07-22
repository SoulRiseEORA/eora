import uuid
import datetime
from pymongo import MongoClient, InsertOne
from EORA.eora_dynamic_params import decide_chat_params
from EORA.aura_multi_stage import multi_stage_selector

client = MongoClient("mongodb://localhost:27017/")
db = client["EORA"]

# 50개 시나리오 예시 (생략 가능)
scenarios = [
    "안녕, 오늘 날씨가 궁금해",
    "새로운 모바일 앱 기획 아이디어가 필요해",
    # ... 이하 생략 ...
]

conv_ops = []
mem_ops = []

for user_input in scenarios:
    uid = "test-user-001"
    cid = str(uuid.uuid4())
    ts = datetime.datetime.utcnow()

    # 회상
    atoms = multi_stage_selector(uid, user_input)
    sys_msgs = [ {"role":"system","content":a["content"]} for a in atoms ]

    # 메시지 구성
    messages = [{"role":"system","content":"너는 이오라(EORA)..." }] + sys_msgs + [{"role":"user","content":user_input}]

    # 파라미터 결정
    params = decide_chat_params(messages)

    # 가상 응답 생성
    response = f"[응답 for {user_input}]"

    # bulk insert for conversation_logs
    conv_ops.append(InsertOne({
        "conversation_id": cid,
        "user_id": uid,
        "messages": messages + [{"role":"assistant","content":response,"timestamp":ts}],
        "params": params,
        "timestamp": ts
    }))

    # bulk insert for memory_atoms
    mem_ops.append(InsertOne({
        "memory_id": str(uuid.uuid4()),
        "user_id": uid,
        "conversation_id": cid,
        "content": response,
        "tags": ["simulation"],
        "resonance_score": params["temperature"],
        "timestamp": ts,
        "source": "assistant"
    }))

# Bulk write
db.conversation_logs.bulk_write(conv_ops)
db.memory_atoms.bulk_write(mem_ops)

print("✅ Batch insert 완료")