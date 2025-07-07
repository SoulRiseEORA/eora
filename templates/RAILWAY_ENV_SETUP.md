# Railway 환경변수 설정 가이드

## 1. Railway 대시보드에서 환경변수 설정

### 필수 환경변수
```
OPENAI_API_KEY=sk-your-openai-api-key-here
DATABASE_NAME=eora_ai
PORT=8000
```

### MongoDB 환경변수 (Railway MongoDB 플러그인 사용 시)
```
MONGO_PUBLIC_URL=mongodb://username:password@host:port/database
MONGO_URL=mongodb://username:password@host:port/database
MONGO_ROOT_USERNAME=your_username
MONGO_ROOT_PASSWORD=your_password
```

### Redis 환경변수 (Railway Redis 플러그인 사용 시)
```
REDIS_URL=redis://username:password@host:port
```

### 선택적 환경변수
```
JWT_SECRET=your-secret-key-here
```

## 2. Railway 플러그인 추가 방법

### MongoDB 플러그인 추가
1. Railway 대시보드 → 프로젝트 선택
2. "New" → "Database" → "MongoDB"
3. 생성 후, 환경변수 자동 주입 확인

### Redis 플러그인 추가 (선택사항)
1. Railway 대시보드 → 프로젝트 선택  
2. "New" → "Database" → "Redis"
3. 생성 후, REDIS_URL 환경변수 자동 주입 확인

## 3. 환경변수 확인 방법

### Railway CLI 사용
```bash
railway variables list
```

### Railway 대시보드에서 확인
1. 프로젝트 → Settings → Variables
2. 모든 환경변수가 올바르게 설정되었는지 확인

## 4. 배포 후 확인

### 로그 확인
```bash
railway logs
```

### 헬스체크
```
https://your-app.railway.app/health
```

## 5. 문제 해결

### OpenAI API 키 오류
- API 키가 올바른지 확인
- OpenAI 계정에서 API 키 생성 및 복사
- Railway 환경변수에 정확히 입력

### MongoDB 연결 오류
- MongoDB 플러그인이 추가되었는지 확인
- 연결 URL이 올바른지 확인
- 네트워크 접근 권한 확인

### Redis 연결 오류
- Redis 플러그인이 추가되었는지 확인
- REDIS_URL 환경변수 확인
- Redis 없이도 서비스는 정상 동작

### faiss 설치 오류
- nixpacks.toml 파일이 프로젝트에 포함되었는지 확인
- 빌드 로그에서 faiss 설치 과정 확인 