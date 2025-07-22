import os, json
from dotenv import load_dotenv
from redis import asyncio as aioredis

load_dotenv()
r = aioredis.Redis.from_url(os.getenv("REDIS_URI"), decode_responses=True)
keys = r.keys("recall:*")
print("캐시된 recall 키들:", keys)
