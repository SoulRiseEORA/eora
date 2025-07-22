
"""debug_retrieve.py
* 모든 메모 임베딩이 비어있는지 확인하고 FAISS 에 재색인
"""
import numpy as np
from aura_system.meta_store import get_all_atom_ids, load_atom, save_embedding
from aura_system.vector_store import FaissIndex

index = FaissIndex()
ids = get_all_atom_ids()
print(f">>> Atom count: {len(ids)}")
new_vecs, new_ids = [], []
for aid in ids:
    doc = load_atom(aid)
    emb = doc.get("embedding")
    if emb:
        index.add(emb, aid)
    else:
        new_ids.append(aid)
if new_ids:
    print(f"⚠️   {len(new_ids)} atoms missing embedding.")
index.save()
