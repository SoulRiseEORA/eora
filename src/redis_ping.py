from redis import Redis

try:
    r = Redis(host="127.0.0.1", port=6379, decode_responses=True)
    if r.ping():
        print("✅ Redis 연결 성공")
    else:
        print("❌ Redis 연결 실패")
except Exception as e:
    print(f"❌ Redis 연결 오류: {e}")
