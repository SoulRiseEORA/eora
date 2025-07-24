# 🗄️ Railway MongoDB 환경변수 설정 가이드

## 🚨 세션 삭제 및 포인트 시스템 문제 해결

### 필수 MongoDB 환경변수 추가

Railway 대시보드 > Service > Variables에서 다음 환경변수들을 **추가**로 설정하세요:

#### 1️⃣ 기본 MongoDB 연결
```
Key: MONGODB_URI
Value: mongodb://localhost:27017

Key: DATABASE_NAME
Value: eora_ai
```

#### 2️⃣ Railway MongoDB 서비스 연결 (MongoDB 서비스가 있는 경우)
```
Key: MONGO_URL
Value: mongodb://mongo:password@mongodb.railway.internal:27017

Key: MONGO_PUBLIC_URL
Value: mongodb://mongo:password@trolley.proxy.rlwy.net:port

Key: MONGO_INITDB_ROOT_USERNAME
Value: mongo

Key: MONGO_INITDB_ROOT_PASSWORD
Value: your-mongodb-password
```

#### 3️⃣ 포인트 시스템 활성화
```
Key: ENABLE_POINTS_SYSTEM
Value: true

Key: DEFAULT_POINTS
Value: 100000
```

#### 4️⃣ 세션 관리 설정
```
Key: SESSION_SECRET
Value: eora_railway_session_secret_key_2024

Key: MAX_SESSIONS_PER_USER
Value: 50
```

## 🔧 설정 방법

### 방법 1: Railway 대시보드에서 직접 설정
1. **https://railway.app/dashboard** 접속
2. EORA 프로젝트 선택
3. **Service** → **Variables** 탭
4. **"New Variable"** 버튼으로 각 변수 추가

### 방법 2: Railway CLI 사용
```bash
railway variables set MONGODB_URI="mongodb://localhost:27017"
railway variables set DATABASE_NAME="eora_ai"
railway variables set ENABLE_POINTS_SYSTEM="true"
railway variables set DEFAULT_POINTS="100000"
```

## 🧪 설정 후 확인 방법

### 1. 재배포 대기
- 환경변수 설정 후 **1-2분** 대기 (자동 재배포)

### 2. 기능 테스트
- **세션 삭제**: ✅ 체크박스 선택 후 삭제 버튼 클릭
- **세션 생성**: ✅ "➕ 새 세션" 버튼 클릭
- **홈 버튼**: ✅ 네비게이션에서 홈 클릭
- **포인트 표시**: ✅ 우상단 포인트 수치 확인

### 3. 브라우저 개발자 도구 확인
1. **F12** 키 눌러서 개발자 도구 열기
2. **Console** 탭에서 JavaScript 오류 확인
3. **Network** 탭에서 API 요청 상태 확인

## 🚀 즉시 테스트 방법

환경변수 설정 후 다음 URL들로 테스트:

```
✅ 채팅 페이지: https://web-production-40c0.up.railway.app/chat
✅ API 상태: https://web-production-40c0.up.railway.app/api/status
✅ 사용자 포인트: https://web-production-40c0.up.railway.app/api/user/points
```

## 🔍 문제 지속 시 체크리스트

- [ ] OPENAI_API_KEY 설정됨
- [ ] MONGODB_URI 설정됨  
- [ ] DATABASE_NAME 설정됨
- [ ] Railway 서비스 재배포 완료
- [ ] 브라우저 캐시 새로고침 (Ctrl+F5)
- [ ] 개발자 도구에서 JavaScript 오류 없음
- [ ] Network 탭에서 static 파일들 200 응답

---

**💡 중요**: 환경변수 설정 후 반드시 재배포가 완료될 때까지 기다리세요! 