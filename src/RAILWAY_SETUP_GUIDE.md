# 🚀 Railway 배포 환경변수 설정 가이드

## 📋 필수 환경변수 목록

Railway 대시보드에서 다음 환경변수들을 설정해야 합니다:

### 🔑 OpenAI API 키
```
Key: OPENAI_API_KEY
Value: sk-your-actual-openai-api-key-here
```

### 🗄️ MongoDB 연결 정보
```
Key: MONGO_PUBLIC_URL
Value: mongodb://mongo:your-password@trolley.proxy.rlwy.net:your-port

Key: MONGO_URL  
Value: mongodb://mongo:your-password@mongodb.railway.internal:27017

Key: MONGO_INITDB_ROOT_PASSWORD
Value: your-mongodb-password

Key: MONGO_INITDB_ROOT_USERNAME
Value: mongo
```

## 🔧 Railway 환경변수 설정 방법

### 1단계: Railway 대시보드 접속
1. [Railway 대시보드](https://railway.app/dashboard)에 로그인
2. 해당 프로젝트 선택

### 2단계: Service Variables 설정
1. **Service** 탭 클릭
2. **Variables** 탭 클릭
3. **New Variable** 버튼 클릭

### 3단계: 환경변수 추가
각 환경변수를 하나씩 추가:

#### OpenAI API 키 설정
```
Key: OPENAI_API_KEY
Value: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### MongoDB 설정
```
Key: MONGO_PUBLIC_URL
Value: mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594

Key: MONGO_URL
Value: mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@mongodb.railway.internal:27017

Key: MONGO_INITDB_ROOT_PASSWORD
Value: HYxotmUHxMxbYAejsOxEnHwrgKpAochC

Key: MONGO_INITDB_ROOT_USERNAME
Value: mongo
```

### 4단계: 서비스 재배포
환경변수 설정 후 자동으로 서비스가 재배포됩니다.

## 🧪 환경변수 확인 방법

### 로컬에서 확인
```bash
python check_railway_env.py
```

### Railway 로그에서 확인
Railway 대시보드 > Service > Deployments > 최신 배포 > Logs

## 🔍 문제 해결

### OpenAI API 키 문제
- ❌ "OPENAI_API_KEY 환경변수가 설정되지 않았습니다"
- ✅ 해결: Railway Variables에서 OPENAI_API_KEY 추가

### MongoDB 연결 문제  
- ❌ "MongoDB 연결 실패"
- ✅ 해결: MONGO_PUBLIC_URL, MONGO_URL 설정 확인

### 포트 충돌 문제
- ❌ "포트 8080이 이미 사용 중"
- ✅ 해결: Railway에서 자동으로 포트 할당됨

### Docker 빌드 실패 문제
- ❌ "nix-env -if .nixpacks/nixpkgs" 오류
- ✅ 해결: 
  1. `.nixpacks/config.toml` 파일 확인
  2. `Procfile`에서 `web: python railway_deploy.py` 확인
  3. `railway.json` 설정 확인
  4. Railway에서 서비스 재배포

## 📞 지원

문제가 발생하면:
1. Railway 로그 확인
2. `python check_railway_env.py` 실행
3. 환경변수 재설정 후 재배포 