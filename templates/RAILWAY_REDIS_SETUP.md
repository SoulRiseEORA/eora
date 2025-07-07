# Railway Redis 설정 가이드

## 🚀 Railway에서 Redis 설정하기

### 1. Railway Redis 서비스 추가

1. **Railway 대시보드에서 프로젝트 선택**
2. **"New Service" 클릭**
3. **"Database" 선택**
4. **"Redis" 선택**
5. **서비스 이름 설정 (예: "eora-redis")**

### 2. 환경 변수 설정

Redis 서비스가 생성되면 자동으로 다음 환경 변수가 설정됩니다:

```bash
REDIS_URL=redis://default:password@redis-host:port
REDIS_HOST=redis-host
REDIS_PORT=port
REDIS_PASSWORD=password
```

### 3. 애플리케이션 서비스에 Redis 연결

1. **애플리케이션 서비스 선택**
2. **"Variables" 탭 클릭**
3. **Redis 서비스에서 제공하는 환경 변수들을 복사**

### 4. 배포 확인

Redis가 설정되면 애플리케이션 로그에서 다음 메시지를 확인할 수 있습니다:

```
✅ Redis 연결 성공
```

## 🔧 로컬 개발 환경

### Redis 설치 (Windows)

1. **WSL2 또는 Docker 사용 권장**
2. **Docker로 Redis 실행:**
   ```bash
   docker run -d --name redis -p 6379:6379 redis:alpine
   ```

### Redis 설치 (macOS)

```bash
brew install redis
brew services start redis
```

### Redis 설치 (Linux)

```bash
sudo apt-get install redis-server
sudo systemctl start redis-server
```

## 🧪 Redis 연결 테스트

### Python으로 테스트

```python
import redis.asyncio as redis
import asyncio

async def test_redis():
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        await r.ping()
        print("✅ Redis 연결 성공")
    except Exception as e:
        print(f"❌ Redis 연결 실패: {e}")

asyncio.run(test_redis())
```

### Redis CLI로 테스트

```bash
redis-cli ping
# 응답: PONG
```

## 🚨 문제 해결

### Redis 연결 실패 시

1. **Redis 서비스가 실행 중인지 확인**
2. **포트가 올바른지 확인 (기본: 6379)**
3. **방화벽 설정 확인**
4. **환경 변수 설정 확인**

### Railway에서 Redis 연결 실패 시

1. **Redis 서비스 상태 확인**
2. **환경 변수 재설정**
3. **애플리케이션 재배포**

## 📊 Redis 사용 사례

### 세션 저장
```python
await redis_manager.set(f"session:{session_id}", session_data, ex=3600)
```

### 캐시 저장
```python
await redis_manager.set(f"cache:{key}", data, ex=300)
```

### 사용자 상태 저장
```python
await redis_manager.set(f"user:{user_id}:status", "online", ex=1800)
```

## 🔒 보안 고려사항

1. **Redis 비밀번호 설정**
2. **네트워크 접근 제한**
3. **SSL/TLS 사용 (프로덕션)**
4. **정기적인 백업**

## 💡 성능 최적화

1. **적절한 만료 시간 설정**
2. **메모리 사용량 모니터링**
3. **연결 풀 설정**
4. **캐시 전략 최적화** 