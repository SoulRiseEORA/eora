import os, time, json
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from openai._exceptions import APIError, APIConnectionError, RateLimitError

from aura_system.meta_store import (
    get_all_atom_ids, load_atom, save_embedding
)
from aura_system.vector_store import FaissIndex

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
faiss = FaissIndex()

ids = get_all_atom_ids()
print(f">>> Atom count: {len(ids)}")

def embed(text, attempt=1, max_retry=5):
    try:
        resp = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return resp.data[0].embedding
    except (APIConnectionError, RateLimitError, APIError) as e:
        if attempt < max_retry:
            wait = 2 ** attempt
            print(f"⏳ Retry {attempt} in {wait}s...")
            time.sleep(wait)
            return embed(text, attempt+1, max_retry)
        raise e

failed = []
updated = 0

for oid in ids:
    doc = load_atom(oid)
    if not doc or doc.get("embedding") or not doc.get("content"):
        continue

    try:
        vec = embed(doc["content"])
        save_embedding(oid, vec)
        faiss.add(vec, oid)
        updated += 1
    except Exception as e:
        failed.append((oid, str(e)))
        print(f"❌ {oid} {e.__class__.__name__}: {e}")

print(f"✅ {updated} atoms updated.")
print(f"⚠️  {len(failed)} failures.")
with open("embedding_failed.json", "w", encoding="utf-8") as f:
    json.dump(failed, f, indent=2, ensure_ascii=False)
print("📝 실패 목록: embedding_failed.json")