# 🚀 Railway 환경변수 설정 가이드

## 📋 필수 환경변수 설정

### 1. Railway 대시보드 접속
- https://railway.app/dashboard 접속
- 프로젝트 선택: `EORA AI System`

### 2. 환경변수 설정
1. **Service** 탭 클릭
2. **Variables** 탭 클릭
3. **New Variable** 버튼 클릭

### 3. 필수 환경변수 추가

#### OPENAI_API_KEY
```
Name: OPENAI_API_KEY
Value: sk-your-openai-api-key-here
```

#### 기타 선택적 환경변수
```
Name: PORT
Value: 8000

Name: ENVIRONMENT
Value: production
```

## 🔧 설정 방법

### 방법 1: Railway 대시보드에서 직접 설정
1. Railway 프로젝트 대시보드 접속
2. Service > Variables 탭
3. "New Variable" 클릭
4. 변수명과 값 입력
5. "Add" 클릭

### 방법 2: Railway CLI 사용
```bash
# Railway CLI 설치
npm install -g @railway/cli

# 로그인
railway login

# 환경변수 설정
railway variables set OPENAI_API_KEY=sk-your-api-key-here
```

## ✅ 확인 방법

### 1. 배포 상태 확인
- Railway 대시보드에서 배포 상태 확인
- 로그에서 환경변수 로드 메시지 확인

### 2. API 테스트
```bash
curl https://web-production-40c0.up.railway.app/api/health
```

### 3. 채팅 테스트
- https://web-production-40c0.up.railway.app/chat 접속
- 메시지 전송하여 GPT 응답 확인

## 🚨 문제 해결

### 환경변수가 로드되지 않는 경우
1. Railway 대시보드에서 변수명 확인
2. 대소문자 구분 확인
3. 재배포 실행

### GPT 응답이 안 되는 경우
1. OPENAI_API_KEY 설정 확인
2. API 키 유효성 확인
3. OpenAI 계정 크레딧 확인

## �� 지원

문제가 발생하면 다음을 확인하세요:
1. Railway 로그 확인
2. 환경변수 설정 상태 확인
3. API 키 유효성 확인 