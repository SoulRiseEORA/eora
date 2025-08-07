# Railway MongoDB 연결 설정 가이드

## 🚀 개요

이 가이드는 Railway에서 제공하는 MongoDB 서비스와 EORA AI 시스템을 연결하는 방법을 설명합니다.

## 📋 Railway MongoDB 연결 정보

Railway에서 제공하는 실제 환경변수들:

```
MONGO_INITDB_ROOT_PASSWORD="HYxotmUHxMxbYAejsOxEnHwrgKpAochC"
MONGO_INITDB_ROOT_USERNAME="mongo"
MONGO_PUBLIC_URL="mongodb://${{MONGO_INITDB_ROOT_USERNAME}}:${{MONGO_INITDB_ROOT_PASSWORD}}@${{RAILWAY_TCP_PROXY_DOMAIN}}:${{RAILWAY_TCP_PROXY_PORT}}"
MONGO_URL="mongodb://${{MONGO_INITDB_ROOT_USERNAME}}:${{MONGO_INITDB_ROOT_PASSWORD}}@${{RAILWAY_PRIVATE_DOMAIN}}:27017"
MONGOHOST="${{RAILWAY_PRIVATE_DOMAIN}}"
MONGOPASSWORD="${{MONGO_INITDB_ROOT_PASSWORD}}"
MONGOPORT="27017"
MONGOUSER="${{MONGO_INITDB_ROOT_USERNAME}}"
```

**중요**: `${{}}` 구문은 Railway에서 자동으로 실제 값으로 치환됩니다.

## 🔧 연결 방법

### 1. 자동 설정 (권장)

Railway의 실제 환경변수 값들을 입력하여 설정합니다:

```bash
# Railway 환경변수 설정 및 연결 테스트
setup_railway_env.bat

# 또는 직접 연결 테스트
python setup_railway_mongo.py

# 서버 실행 (MongoDB 연결)
run_server_with_railway_mongo.bat
```

### 2. 수동 설정

PowerShell에서 Railway의 실제 환경변수 값들을 설정:

```powershell
# Railway 대시보드에서 확인한 실제 값들을 입력하세요
$env:MONGO_INITDB_ROOT_PASSWORD="실제_비밀번호"
$env:MONGO_INITDB_ROOT_USERNAME="실제_사용자명"
$env:RAILWAY_TCP_PROXY_DOMAIN="실제_도메인"
$env:RAILWAY_TCP_PROXY_PORT="실제_포트"
$env:RAILWAY_PRIVATE_DOMAIN="실제_내부_도메인"
```

### 3. .env 파일 설정

프로젝트 루트에 `.env` 파일 생성:

```env
# Railway 대시보드에서 확인한 실제 값들을 입력하세요
MONGO_INITDB_ROOT_PASSWORD=실제_비밀번호
MONGO_INITDB_ROOT_USERNAME=실제_사용자명
RAILWAY_TCP_PROXY_DOMAIN=실제_도메인
RAILWAY_TCP_PROXY_PORT=실제_포트
RAILWAY_PRIVATE_DOMAIN=실제_내부_도메인
```

## 🧪 연결 테스트

### 1. 자동 설정 및 테스트

```bash
setup_railway_env.bat
```

### 2. 직접 테스트

```bash
python setup_railway_mongo.py
```

## ✅ 성공 시나리오

MongoDB 연결이 성공하면 다음과 같은 메시지가 표시됩니다:

```
🔗 Railway MongoDB 연결 테스트 시작...
📝 연결 URL: mongodb://mongo:***@trolley.proxy.rlwy.net:26594
✅ MongoDB 연결 성공!
📋 현재 컬렉션 목록: []
✅ 테스트 사용자 생성 성공: [ObjectId]
✅ 테스트 사용자 삭제 완료
🎉 Railway MongoDB 연결이 성공했습니다!
```

## ❌ 실패 시나리오

연결에 실패하면 다음과 같은 메시지가 표시됩니다:

```
❌ MongoDB 연결 실패: [오류 메시지]
🔍 상세 오류: [오류 타입]
❌ Railway MongoDB 연결에 실패했습니다.
```

## 🔍 문제 해결

### 1. 연결 실패 시 확인사항

- Railway 프로젝트에서 MongoDB 서비스가 실행 중인지 확인
- 연결 정보(사용자명, 비밀번호, 호스트, 포트)가 올바른지 확인
- 네트워크 연결 상태 확인
- 방화벽 설정 확인

### 2. 일반적인 오류

#### Authentication failed
- 사용자명과 비밀번호가 올바른지 확인
- Railway에서 MongoDB 인증 정보 재확인

#### Connection timeout
- 네트워크 연결 상태 확인
- Railway 서비스 상태 확인

#### Host not found
- 호스트 주소가 올바른지 확인
- DNS 설정 확인

## 📊 데이터베이스 구조

연결 성공 시 다음과 같은 컬렉션이 자동으로 생성됩니다:

- `users`: 사용자 정보
- `points`: 포인트 정보
- `sessions`: 세션 정보
- `chat_logs`: 채팅 로그

## 🔐 관리자 계정

서버 시작 시 자동으로 관리자 계정이 생성됩니다:

- **이메일**: admin@eora.ai
- **사용자 ID**: admin
- **비밀번호**: admin1234
- **권한**: 관리자 (is_admin: true)

## 🌐 서버 접속

서버 실행 후 다음 주소로 접속:

- **홈**: http://localhost:8010/
- **로그인**: http://localhost:8010/login
- **대시보드**: http://localhost:8010/dashboard
- **관리자**: http://localhost:8010/admin

## 📝 참고사항

- Railway의 내부 URL(`mongodb.railway.internal`)은 Railway 내부에서만 접근 가능
- 로컬 개발 환경에서는 공개 URL(`trolley.proxy.rlwy.net`)을 사용
- 프로덕션 환경에서는 환경변수를 통해 안전하게 관리 