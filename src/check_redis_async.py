import asyncio
import os
import json
from redis.asyncio import Redis
from dotenv import load_dotenv

load_dotenv()
REDIS_URI = os.getenv("REDIS_URI", "redis://localhost:6379/0")

async def main():
    r = Redis.from_url(REDIS_URI, decode_responses=True)
    keys = await r.keys("recall:*")
    print("Redis에 저장된 recall 키들:", keys)
    await r.close()

if __name__ == "__main__":
    asyncio.run(main())
