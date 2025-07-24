# 🚨 Railway 배포 문제 해결 가이드

## 📋 현재 문제점
1. **세션 삭제 버튼이 클릭되지 않음** ❌
2. **GPT 대화가 작동하지 않음** ❌  
3. **로컬에서는 정상 작동함** ✅

## 🔍 문제 원인
**Railway 환경변수가 설정되지 않아서 발생하는 문제**

### 누락된 필수 환경변수
```
❌ OPENAI_API_KEY: 설정되지 않음
❌ MONGO_PUBLIC_URL: 설정되지 않음  
❌ MONGO_URL: 설정되지 않음
❌ MONGO_INITDB_ROOT_PASSWORD: 설정되지 않음
❌ MONGO_INITDB_ROOT_USERNAME: 설정되지 않음
```

## 🔧 해결 방법

### 1단계: Railway 대시보드 접속
1. **https://railway.app/dashboard** 접속
2. **로그인** 후 EORA 프로젝트 선택
3. **Service** 탭 클릭 → **Variables** 탭 클릭

### 2단계: 필수 환경변수 설정

#### 🔑 OpenAI API 키 (가장 중요!)
```
Key: OPENAI_API_KEY
Value: sk-proj-your-actual-openai-api-key-here
```

#### 🗄️ MongoDB 연결 정보
```
Key: MONGO_URL
Value: mongodb://mongo:password@mongodb.railway.internal:27017

Key: MONGO_PUBLIC_URL  
Value: mongodb://mongo:password@trolley.proxy.rlwy.net:26594

Key: MONGO_INITDB_ROOT_USERNAME
Value: mongo

Key: MONGO_INITDB_ROOT_PASSWORD
Value: your-mongodb-password
```

#### 🚀 서버 설정
```
Key: PORT
Value: 8080

Key: PYTHONUNBUFFERED
Value: 1
```

### 3단계: MongoDB 서비스 추가 (없는 경우)
1. Railway 대시보드에서 **"New Service"** 클릭
2. **"Database"** → **"MongoDB"** 선택
3. MongoDB 서비스 생성 후 **Connect** 탭에서 연결 정보 복사
4. 위의 MONGO_* 환경변수에 실제 값 입력

### 4단계: 재배포
- 환경변수 설정 후 **자동 재배포** 대기 (1-2분)
- 또는 **"Deploy"** 버튼 클릭하여 수동 재배포

## 🧪 확인 방법

### 1. 서비스 상태 확인
```
https://web-production-40c0.up.railway.app/api/status
```

### 2. 채팅 기능 테스트
```
https://web-production-40c0.up.railway.app/chat
```

### 3. Railway 로그 확인
- Railway 대시보드 → **Service** → **Deployments** → **최신 배포** → **Logs**
- 다음 메시지들이 보여야 함:
  ```
  ✅ OpenAI API 키가 환경변수에서 로드되었습니다.
  ✅ MongoDB 연결 성공
  ✅ EORA AI System 시작 완료
  ```

## 🚨 긴급 임시 해결책

환경변수 설정이 어려운 경우, 코드에서 직접 설정:

### app.py 파일 수정
```python
# 임시로 API 키 하드코딩 (보안상 위험하니 배포 후 즉시 환경변수로 변경)
OPENAI_API_KEY = "sk-proj-your-actual-api-key-here"
```

## 📞 추가 지원

### Railway CLI 사용 (고급 사용자용)
```bash
# Railway CLI 설치
npm install -g @railway/cli

# 로그인
railway login

# 환경변수 설정
railway variables set OPENAI_API_KEY="sk-proj-your-api-key-here"
railway variables set MONGO_URL="mongodb://mongo:password@mongodb.railway.internal:27017"
```

### 문제 지속 시 확인사항
1. **OpenAI API 키 유효성** 확인
2. **API 키 사용량/크레딧** 확인  
3. **MongoDB 서비스 상태** 확인
4. **Railway 서비스 로그** 상세 확인

## ✅ 성공 시 예상 결과
- 🔄 세션 삭제 버튼 정상 작동
- 💬 GPT 대화 정상 응답
- 📊 포인트 시스템 정상 작동
- 💾 대화 내용 저장 기능 작동

---

**⚠️ 중요**: 환경변수 설정 후 반드시 **재배포**를 진행해야 변경사항이 적용됩니다! 