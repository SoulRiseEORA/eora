# Railway 배포 및 MongoDB 연결 종합 가이드

## 🚀 개요

이 가이드는 EORA AI 시스템을 Railway에 배포하고 MongoDB를 연결하는 전체 과정을 설명합니다.

## 📋 현재 상황

### ✅ 완료된 작업
- Railway MongoDB 서비스 추가
- GitHub 저장소 설정
- 서버 코드 업데이트 (Railway MongoDB 연결 지원)
- 배포 스크립트 준비

### ❌ 해결해야 할 문제
- Railway MongoDB 연결 실패
- 컬렉션이 생성되지 않음
- GitHub 배포 상태 확인 필요

## 🔧 단계별 해결 방법

### 1단계: GitHub 배포 확인

```bash
# GitHub에 코드 배포
deploy_to_github.bat
```

**확인사항:**
- GitHub 저장소에 코드가 업로드되었는지 확인
- Railway 대시보드에서 GitHub 저장소 연결 상태 확인

### 2단계: Railway 환경변수 확인

Railway 대시보드에서 다음 환경변수들을 확인하세요:

```
MONGO_INITDB_ROOT_PASSWORD="HYxotmUHxMxbYAejsOxEnHwrgKpAochC"
MONGO_INITDB_ROOT_USERNAME="mongo"
RAILWAY_TCP_PROXY_DOMAIN="실제_도메인_값"
RAILWAY_TCP_PROXY_PORT="실제_포트_값"
RAILWAY_PRIVATE_DOMAIN="실제_내부_도메인_값"
```

### 3단계: MongoDB 연결 테스트

#### 방법 1: 간단한 테스트
```bash
python simple_mongo_test.py
```

#### 방법 2: 상세 테스트
```bash
python check_railway_deployment.py
```

#### 방법 3: 환경변수 설정 후 테스트
```bash
setup_railway_env.bat
```

### 4단계: 서버 실행

```bash
# Railway MongoDB 연결로 서버 실행
run_server_with_railway_mongo.bat
```

## 🔍 문제 해결

### MongoDB 연결 실패 시

#### 1. Authentication failed
**원인:** 사용자명/비밀번호 오류
**해결방법:**
- Railway 대시보드에서 `MONGO_INITDB_ROOT_PASSWORD` 확인
- Railway 대시보드에서 `MONGO_INITDB_ROOT_USERNAME` 확인

#### 2. getaddrinfo failed
**원인:** 호스트 주소를 찾을 수 없음
**해결방법:**
- Railway 대시보드에서 `RAILWAY_TCP_PROXY_DOMAIN` 확인
- Railway 대시보드에서 `RAILWAY_TCP_PROXY_PORT` 확인

#### 3. Connection timeout
**원인:** 서비스가 실행되지 않거나 네트워크 문제
**해결방법:**
- Railway 대시보드에서 MongoDB 서비스 상태 확인
- Railway 프로젝트가 실행 중인지 확인

### GitHub 배포 실패 시

#### 1. 저장소 접근 권한 오류
**해결방법:**
- GitHub 개인 액세스 토큰 생성
- Git 자격 증명 설정

#### 2. Railway 연결 실패
**해결방법:**
- Railway 대시보드에서 GitHub 저장소 재연결
- Railway 프로젝트 설정 확인

## 📊 예상 결과

### 성공 시나리오

```
🔗 Railway MongoDB 연결 테스트
📝 연결 URL: mongodb://mongo:***@실제_도메인:실제_포트
✅ MongoDB 연결 성공!
📋 현재 컬렉션 목록: []
✅ 테스트 사용자 생성 성공: [ObjectId]
✅ 테스트 사용자 삭제 완료
📋 최종 컬렉션 목록: ['users']
🎉 Railway MongoDB 연결이 성공했습니다!
```

### 서버 실행 성공 시

```
🔗 MongoDB 연결 시도: Railway 공개 URL (자동 구성)
📝 연결 URL: mongodb://mongo:***@실제_도메인:실제_포트
✅ MongoDB 연결 성공: Railway
✅ 관리자 계정 생성 (MongoDB): admin@eora.ai (ID: admin, PW: admin1234)
🚀 EORA AI 최종 서버를 시작합니다...
📍 주소: http://localhost:8010
```

## 🌐 배포된 서비스 접속

### 로컬 개발 환경
- **홈**: http://localhost:8010/
- **로그인**: http://localhost:8010/login
- **대시보드**: http://localhost:8010/dashboard
- **관리자**: http://localhost:8010/admin

### Railway 배포 환경
- **메인 사이트**: https://www.eora.life
- **API 문서**: https://www.eora.life/docs
- **헬스 체크**: https://www.eora.life/health

## 📝 중요 참고사항

### 1. Railway 환경변수
- Railway의 `${{}}` 구문은 자동으로 실제 값으로 치환됩니다
- 로컬 개발 환경에서는 실제 값들을 직접 입력해야 합니다

### 2. MongoDB 연결
- Railway 내부 URL은 Railway 내부에서만 접근 가능합니다
- 로컬 개발 환경에서는 공개 URL을 사용해야 합니다

### 3. 보안
- 실제 운영 환경에서는 환경변수를 통해 민감한 정보를 관리하세요
- GitHub에 민감한 정보가 업로드되지 않도록 주의하세요

## 🔄 다음 단계

1. **Railway 배포 확인**: `check_railway_deployment.py` 실행
2. **MongoDB 연결 테스트**: `simple_mongo_test.py` 실행
3. **서버 실행**: `run_server_with_railway_mongo.bat` 실행
4. **관리자 로그인**: admin@eora.ai / admin1234

## 📞 문제 발생 시

1. Railway 대시보드에서 서비스 상태 확인
2. Railway 로그에서 오류 메시지 확인
3. GitHub 저장소에서 최신 코드 확인
4. 환경변수 설정 재확인

---

**💡 팁:** Railway 대시보드에서 실시간으로 서비스 상태와 로그를 확인할 수 있습니다. 