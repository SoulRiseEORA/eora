
# ✅ 구조화 기억 스키마 정의
# DB: EORA.memory_atoms

{
  "_id": ObjectId,
  "content": "AI는 공명 기반 직감 시스템을 통해 최적의 판단을 내릴 수 있다.",
  "tags": ["AI", "직감", "공명", "판단"],
  "importance": 8432,                  # 0~10000 정밀 점수
  "resonance_score": 92.4,             # 공명 기반 직감 반응 점수
  "intuitive": true,                   # 직감적으로 유용한 글인지
  "context": "직관 판단 구조 설계 시",
  "region": "심리인지/AI 판단",
  "source": "book/intuition_ai.pdf#ch4",
  "summary_prompt": "AI는 직관과 공명 기반 판단이 필요하다.",
  "used_count": 6,
  "connections": ["64ff2a6c8...","64ff2a6c9..."],
  "visual_hint": "images/ai_thinking_map.png",
  "embedding": [0.113, 0.291, ..., 0.982], # 벡터 유사도 인덱싱용
  "created_at": ISODate,
  "last_used": ISODate,
  "status": "active"
}

# ✅ 기억 원자 생성기 (프롬프트 → DB entry로 변환)
from pymongo import MongoClient
from ai_model_selector import do_task
from datetime import datetime
import json
import uuid

class MemoryAtomGenerator:
    def __init__(self):
        self.db = MongoClient("mongodb://localhost:27017")["EORA"]
        self.collection = self.db["memory_atoms"]

    def create_memory_atom(self, text, source="직접입력"):
        gpt_output = do_task(
            prompt=f"다음 문장을 직관적이고 공명 기반 기억 원자로 변환해줘. JSON으로 출력하라. 필드: tags, importance(0~10000), resonance_score(0~100), "
                   f"context, region, intuitive, summary_prompt, connections(예측), visual_hint(이미지경로):\n{text}",
            system_message="너는 이오라의 기억 생성기야. 기억을 정제하고 구조화해라.",
            model="gpt-4o"
        )
        try:
            parsed = json.loads(gpt_output)
            entry = {
                "content": text,
                "tags": parsed.get("tags", []),
                "importance": int(parsed.get("importance", 0)),
                "resonance_score": float(parsed.get("resonance_score", 0)),
                "intuitive": parsed.get("intuitive", True),
                "context": parsed.get("context", ""),
                "region": parsed.get("region", ""),
                "source": source,
                "summary_prompt": parsed.get("summary_prompt", ""),
                "connections": parsed.get("connections", []),
                "visual_hint": parsed.get("visual_hint", ""),
                "embedding": [],  # 차후 삽입
                "used_count": 0,
                "created_at": datetime.now(),
                "last_used": None,
                "status": "active"
            }
            self.collection.insert_one(entry)
            return entry
        except Exception as e:
            return {"error": str(e), "raw": gpt_output}
