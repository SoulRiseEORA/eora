import faiss
import numpy as np
from pymongo import MongoClient
import os
import pickle

# 설정
mongo_uri = "mongodb://localhost:27017"
db_name = "aura_memory"
collection_name = "memories"
embedding_key = "semantic_embedding"
index_file = "faiss_index.idx"
id_map_file = "faiss_id_map.pkl"

# Mongo 연결
client = MongoClient(mongo_uri)
collection = client[db_name][collection_name]

# 임베딩 수집
embeddings = []
ids = []

for doc in collection.find({embedding_key: {"$exists": True}}):
    emb = doc[embedding_key]
    if isinstance(emb, list) and all(isinstance(x, float) for x in emb):
        embeddings.append(np.array(emb, dtype="float32"))
        ids.append(str(doc["_id"]))

# 인덱스 빌드
if embeddings:
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    vectors = np.stack(embeddings)
    index.add(vectors)
    faiss.write_index(index, index_file)
    with open(id_map_file, "wb") as f:
        pickle.dump(ids, f)
    print(f"✅ 인덱스 생성 완료: {len(embeddings)}개 벡터 → {index_file}")
else:
    print("❌ 유효한 벡터가 없습니다. faiss index 생성 실패.")