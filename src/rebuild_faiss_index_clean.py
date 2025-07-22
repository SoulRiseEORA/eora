
import json
import os
import numpy as np
import faiss
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MEMORY_JSON_PATH = "E:/AI_Dev_Tool/src/aura_system/memory/memory_db.json"
INDEX_PATH = "E:/AI_Dev_Tool/src/aura_system/memory/faiss.index"

def embed_text(text):
    api_key = os.getenv("OPENAI_API_KEY", "")
    client = OpenAI(
        api_key=api_key,
        # proxies 인수 제거 - httpx 0.28.1 호환성
    )
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def rebuild_faiss_index():
    if not os.path.exists(MEMORY_JSON_PATH):
        print("memory_db.json 파일이 없습니다.")
        return

    with open(MEMORY_JSON_PATH, "r", encoding="utf-8") as f:
        memories = json.load(f)

    if not memories:
        print("메모리가 없습니다.")
        return

    dim = 1536
    index = faiss.IndexFlatL2(dim)

    for idx, mem in enumerate(memories):
        text = mem.get("user_input", "")
        if text:
            emb = embed_text(text)
            emb = np.array(emb, dtype="float32").reshape(1, -1)
            index.add(emb)
            print(f"[{idx+1}/{len(memories)}] Embedding 생성 및 추가 완료.")

    faiss.write_index(index, INDEX_PATH)
    print(f"✅ 완료: FAISS 인덱스 저장됨 → {INDEX_PATH}")

if __name__ == "__main__":
    rebuild_faiss_index()
