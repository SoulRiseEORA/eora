import redis
import json

def safe_redis_set(client, key, value):
    try:
        # 문자열 또는 JSON 직렬화 후 저장
        if not isinstance(value, str):
            value = json.dumps(value)
        client.set(key, value)
        print(f"✅ Redis에 저장 성공: {key}")
    except Exception as e:
        print(f"[⚠️ Redis 캐시 저장 오류] key={key} → {e}")
