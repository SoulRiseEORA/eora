# diagnostic_recall_system.py
# 목적: 회상 시스템의 주요 구성 요소 진단 및 점검

import os
import json
from aura_system.meta_store import get_all_atom_ids, get_atoms_by_ids
from aura_system.vector_store import FaissIndex

print("🔎 회상 시스템 진단 시작")

# 1. Mongo 메모 수
atom_ids = get_all_atom_ids()
print(f"📄 MongoDB 메모 개수: {len(atom_ids)}")

# 2. FAISS 로딩
index = FaissIndex()
try:
    test_query = [0.1] * 1536  # 벡터 차원 확인
    results = index.search(test_query, top_k=3)
    print(f"📦 FAISS 인덱스 정상 작동: 반환된 결과 {len(results)}개")
except Exception as e:
    print("❌ FAISS 오류:", str(e))

# 3. 메모 embedding 존재 여부 확인
atoms = get_atoms_by_ids(atom_ids[:5])
for a in atoms:
    if "embedding" not in a or not a["embedding"]:
        print("⚠️  embedding 없음:", a.get("_id"))
    else:
        print("✅  embedding 있음:", a.get("_id"))

print("✅ 회상 시스템 진단 완료")