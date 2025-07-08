# Railway 환경 변수 설정 가이드

## 🎯 목표
Railway에서 EORA AI 시스템이 MongoDB에 정상적으로 연결되도록 환경 변수를 설정합니다.

## 📋 필수 환경 변수 목록

### 1. MongoDB 연결 정보
```
MONGODB_URL=mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594
```

### 2. 개별 MongoDB 변수 (선택사항)
```
MONGO_HOST=trolley.proxy.rlwy.net
MONGO_PORT=26594
MONGO_INITDB_ROOT_PASSWORD=HYxotmUHxMxbYAejsOxEnHwrgKpAochC
```

### 3. OpenAI API 키
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. 포트 설정
```
PORT=8080
```

## 🛠️ 설정 방법

### 방법 1: Railway 대시보드 (권장)

1. **Railway 대시보드 접속**
   - https://railway.app/dashboard
   - EORA AI 프로젝트 선택

2. **Variables 탭 클릭**
   - 프로젝트 페이지에서 "Variables" 탭 선택

3. **환경 변수 추가**
   - "New Variable" 버튼 클릭
   - 위의 변수들을 하나씩 추가

### 방법 2: Railway CLI

1. **Railway CLI 설치**
   ```bash
   npm install -g @railway/cli
   ```

2. **로그인**
   ```bash
   railway login
   ```

3. **프로젝트 연결**
   ```bash
   railway link
   ```

4. **환경 변수 설정**
   ```bash
   # MongoDB URL
   railway variables set MONGODB_URL="mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594"
   
   # OpenAI API 키
   railway variables set OPENAI_API_KEY="your_api_key_here"
   
   # 포트
   railway variables set PORT="8080"
   ```

### 방법 3: 자동 스크립트 실행

```bash
# 스크립트 실행 권한 부여
chmod +x railway_env_setup.sh

# 스크립트 실행
./railway_env_setup.sh
```

## 🔍 설정 확인

### Railway 대시보드에서 확인
- Variables 탭에서 설정된 변수들 확인
- 각 변수의 값이 올바른지 검증

### CLI로 확인
```bash
railway variables list
```

## 🚀 배포 후 확인

환경 변수 설정 후:

1. **자동 재배포**
   - Railway가 자동으로 새로운 환경 변수로 재배포

2. **로그 확인**
   - 배포 로그에서 MongoDB 연결 성공 메시지 확인
   - 오류가 있다면 환경 변수 값 재확인

3. **Health Check**
   - 애플리케이션이 정상적으로 응답하는지 확인

## ⚠️ 주의사항

1. **보안**
   - API 키와 비밀번호는 절대 코드에 하드코딩하지 마세요
   - 환경 변수로만 관리하세요

2. **형식**
   - MongoDB URL의 형식을 정확히 지켜주세요
   - 포트 번호는 문자열로 설정하세요

3. **재배포**
   - 환경 변수 변경 후 자동 재배포가 필요할 수 있습니다

## 🆘 문제 해결

### MongoDB 연결 실패 시
1. 환경 변수 값 확인
2. MongoDB 서비스가 Railway에서 실행 중인지 확인
3. 네트워크 연결 상태 확인

### OpenAI API 오류 시
1. API 키가 올바른지 확인
2. API 키에 충분한 크레딧이 있는지 확인
3. API 사용량 제한 확인 