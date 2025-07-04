# 🚂 Railway 환경변수 설정 가이드

## 필수 환경변수 목록

### 1. OpenAI API 키
```
OPENAI_API_KEY=sk-proj-your-actual-openai-api-key-here
```

### 2. MongoDB 연결 정보
```
MONGO_URL=mongodb://mongo:password@mongodb.railway.internal:27017
MONGO_PUBLIC_URL=mongodb://mongo:password@trolley.proxy.rlwy.net:26594
MONGO_INITDB_ROOT_USERNAME=mongo
MONGO_INITDB_ROOT_PASSWORD=your-mongodb-password
```

### 3. 서버 설정
```
PORT=8080
PYTHONUNBUFFERED=1
```

## 설정 방법

1. **Railway 대시보드 접속**
   - https://railway.app/dashboard
   - EORA 프로젝트 선택

2. **환경변수 설정**
   - Service > Variables 탭 클릭
   - "New Variable" 버튼으로 각 변수 추가

3. **재배포**
   - 환경변수 설정 후 자동 재배포됨
   - 또는 "Deploy" 버튼으로 수동 재배포

## 확인 방법

### 1. 서버 로그 확인
Railway 대시보드 > Service > Deployments > 최신 배포 > Logs

### 2. API 상태 확인
```
https://your-railway-url.railway.app/api/status
```

### 3. 채팅 API 테스트
```bash
curl -X POST https://your-railway-url.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요", "session_id": "test"}'
```

## 문제 해결

### OpenAI API 키 문제
- API 키가 올바른지 확인
- API 키에 충분한 크레딧이 있는지 확인
- API 키가 활성화되어 있는지 확인

### MongoDB 연결 문제
- MongoDB 서비스가 Railway에서 실행 중인지 확인
- 연결 문자열이 올바른지 확인
- 네트워크 접근 권한이 있는지 확인

### 포트 문제
- Railway에서 자동으로 포트를 할당하므로 PORT=8080 설정
- Dockerfile에서 EXPOSE 8080 확인 