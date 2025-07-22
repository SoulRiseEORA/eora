import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
import redis
import json
from datetime import datetime

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def redis_key(user_id):
    return f"memory:{user_id}"

def cache_to_redis(user_id, content):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "content": content
    }
    r.rpush(redis_key(user_id), json.dumps(entry))
    r.ltrim(redis_key(user_id), -10, -1)

def recall_from_redis(user_id, top_k=3):
    items = r.lrange(redis_key(user_id), -top_k, -1)
    return [json.loads(i)["content"] for i in items]