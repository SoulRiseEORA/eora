# 🔧 Railway MongoDB 연결 문제 해결 가이드

## 🚨 현재 문제
```
❌ MongoDB 연결 실패: Port must be an integer between 0 and 65535: ''
❌ MongoDB 연결 실패: A password is required.
```

## 🔧 해결 방법

### 1. Railway MongoDB 서비스 확인
1. **Railway 대시보드** 접속: https://railway.app/dashboard
2. **EORA 프로젝트** 선택
3. **MongoDB 서비스**가 있는지 확인
   - 없다면: "New Service" → "Database" → "MongoDB" 추가

### 2. MongoDB 환경변수 설정
Railway 대시보드 > Service > Variables에서 다음 변수들을 **정확히** 설정:

#### 필수 환경변수
```
MONGO_URL=mongodb://mongo:YOUR_PASSWORD@mongodb.railway.internal:27017
MONGO_PUBLIC_URL=mongodb://mongo:YOUR_PASSWORD@trolley.proxy.rlwy.net:YOUR_PORT
MONGO_INITDB_ROOT_USERNAME=mongo
MONGO_INITDB_ROOT_PASSWORD=YOUR_ACTUAL_PASSWORD
```

#### 예시 (실제 값으로 변경 필요)
```
MONGO_URL=mongodb://mongo:MySecurePassword123@mongodb.railway.internal:27017
MONGO_PUBLIC_URL=mongodb://mongo:MySecurePassword123@trolley.proxy.rlwy.net:26594
MONGO_INITDB_ROOT_USERNAME=mongo
MONGO_INITDB_ROOT_PASSWORD=MySecurePassword123
```

### 3. MongoDB 연결 정보 확인 방법
1. **Railway MongoDB 서비스** 클릭
2. **Connect** 탭에서 연결 정보 확인
3. **Internal URL**과 **Public URL** 복사
4. 위의 환경변수에 **정확히** 입력

### 4. 재배포
환경변수 설정 후:
1. **Deploy** 버튼 클릭
2. 또는 자동 재배포 대기 (1-2분)

### 5. 연결 확인
배포 완료 후 다음 URL로 확인:
- https://eora.life/api/status
- MongoDB 연결 상태가 `true`로 변경되어야 함

## 🚀 빠른 해결 스크립트

### Railway CLI 사용 (권장)
```bash
# Railway CLI 설치
npm install -g @railway/cli

# 로그인
railway login

# 환경변수 설정
railway variables set MONGO_URL="mongodb://mongo:YOUR_PASSWORD@mongodb.railway.internal:27017"
railway variables set MONGO_PUBLIC_URL="mongodb://mongo:YOUR_PASSWORD@trolley.proxy.rlwy.net:YOUR_PORT"
railway variables set MONGO_INITDB_ROOT_USERNAME="mongo"
railway variables set MONGO_INITDB_ROOT_PASSWORD="YOUR_ACTUAL_PASSWORD"
```

## 📞 지원
문제가 지속되면 Railway MongoDB 서비스의 정확한 연결 정보를 확인해주세요. 