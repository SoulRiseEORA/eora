# Railway 환경변수 설정 가이드

## 🔐 보안 중요사항
- **절대 API 키를 GitHub에 올리지 마세요!**
- `.env` 파일은 `.gitignore`에 포함되어 있어 GitHub에 업로드되지 않습니다.
- Railway 환경변수를 통해 안전하게 API 키를 관리하세요.

## 🚀 Railway 환경변수 설정 방법

### 1. Railway 대시보드 접속
1. [Railway.app](https://railway.app)에 로그인
2. 프로젝트 선택
3. **Service** 탭 클릭

### 2. 환경변수 추가
**Variables** 섹션에서 다음 환경변수들을 추가하세요:

#### 필수 환경변수
```
OPENAI_API_KEY=sk-your-openai-api-key-here
```

#### MongoDB 환경변수 (이미 설정됨)
```
MONGO_INITDB_ROOT_PASSWORD=your-mongo-password
MONGO_INITDB_ROOT_USERNAME=mongo
MONGO_PUBLIC_URL=mongodb://mongo:password@trolley.proxy.rlwy.net:26594
MONGO_URL=mongodb://mongo:password@mongodb.railway.internal:27017
RAILWAY_TCP_PROXY_DOMAIN=trolley.proxy.rlwy.net
RAILWAY_TCP_PROXY_PORT=26594
RAILWAY_PRIVATE_DOMAIN=mongodb.railway.internal
```

### 3. 환경변수 설정 순서
1. **Variables** 섹션에서 **"New Variable"** 클릭
2. **Name**: `OPENAI_API_KEY`
3. **Value**: `sk-`로 시작하는 실제 OpenAI API 키
4. **Save** 클릭

### 4. 배포 확인
1. 환경변수 설정 후 **Deploy** 버튼 클릭
2. 배포 완료 후 서비스 URL로 접속
3. `/api/status` 엔드포인트에서 OpenAI 연결 상태 확인

## 🔧 로컬 테스트 방법

### PowerShell에서 환경변수 설정
```powershell
$env:OPENAI_API_KEY="sk-your-openai-api-key-here"
python final_server.py
```

### 배치 파일 사용
```batch
run_server_with_env.bat
```

## 📋 확인 사항

### 서버 시작 시 정상 메시지
```
✅ OpenAI API 키 설정 성공 및 연결 확인 완료
📝 API 키: sk-xxxx...
```

### API 상태 확인
```
GET /api/status
```
응답에서 `"openai": {"available": true}` 확인

### 채팅 테스트
1. http://localhost:8011/chat 접속
2. 메시지 입력
3. 실제 GPT-4o 응답이 나오는지 확인

## ❌ 문제 해결

### OpenAI API 키가 설정되지 않음
- Railway 환경변수에 `OPENAI_API_KEY`가 제대로 등록되었는지 확인
- API 키가 `sk-`로 시작하는지 확인
- 배포 후 서버 재시작 확인

### 기본 응답만 나옴
- 환경변수가 제대로 로드되지 않은 상태
- 서버 로그에서 "⚠️ OpenAI API 키가 설정되지 않음" 메시지 확인

### Railway 배포 실패
- Dockerfile이 올바르게 설정되었는지 확인
- requirements.txt에 필요한 패키지가 모두 포함되었는지 확인 