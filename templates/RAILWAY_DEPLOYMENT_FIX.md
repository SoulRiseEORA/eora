# Railway 배포 오류 해결 가이드

## 🚨 최근 발생한 오류들과 해결책

### 1. OpenAI API 클라이언트 초기화 오류
**오류**: `AsyncClient.__init__() got an unexpected keyword argument 'proxies'`

**원인**: OpenAI API 1.0.0+ 버전에서 클라이언트 초기화 방식이 변경됨

**해결책**: ✅ **수정 완료**
- `main.py`에서 OpenAI 클라이언트 초기화 코드를 1.0.0+ 버전에 맞게 업데이트
- `proxies` 인수 제거 및 새로운 클라이언트 구조 적용

### 2. MongoDB 연결 오류
**오류**: `Port must be an integer between 0 and 65535: '26594"MONGO_INITDB_ROOT_PASSWORD="HYxotmUHxMxbYAejsOxEnHwrgKpAochC'`

**원인**: Railway 환경변수에서 MongoDB URL 파싱 문제

**해결책**: ✅ **수정 완료**
- MongoDB URL에서 따옴표 제거 로직 추가
- 연결 타임아웃 설정 강화
- 연결 테스트 추가

### 3. 템플릿 디렉토리 문제
**오류**: `Templates directory not found!`

**원인**: Railway 환경에서 템플릿 경로 설정 문제

**해결책**: ✅ **수정 완료**
- Railway 환경에서 대체 경로 시도 로직 추가
- 템플릿 초기화 오류 처리 강화
- 정적 파일 마운트 최적화

## 🔧 수정된 주요 파일들

### main.py 주요 변경사항
1. **OpenAI 클라이언트 초기화 개선**
   ```python
   # OpenAI 1.0.0+ 버전 호환 코드
   if hasattr(openai, 'OpenAI'):
       openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
   else:
       openai.api_key = OPENAI_API_KEY
   ```

2. **MongoDB 연결 강화**
   ```python
   # Railway 환경에서 MongoDB URL 파싱 문제 해결
   if MONGODB_URL and '"' in MONGODB_URL:
       MONGODB_URL = MONGODB_URL.strip('"').strip("'")
   ```

3. **템플릿 경로 최적화**
   ```python
   # Railway 환경에서 대체 경로 시도
   templates_path = Path(__file__).parent
   if not templates_path.exists():
       templates_path = Path("/app")
   ```

4. **Railway 환경 감지**
   ```python
   # Railway 환경 감지 및 최적화
   is_railway = os.environ.get("RAILWAY_ENVIRONMENT", "").lower() in ["production", "true", "1"]
   ```

### nixpacks.toml 최적화
- 불필요한 패키지 설치 제거
- 빌드 과정 단순화
- 핵심 의존성만 설치하도록 변경

## 🚀 배포 단계별 체크리스트

### 1단계: 코드 업데이트 확인
- [x] `main.py` 최신 버전 확인
- [x] `nixpacks.toml` 최적화 완료
- [x] `requirements.txt` 의존성 확인

### 2단계: Railway 환경변수 설정
- [ ] `OPENAI_API_KEY` 설정
- [ ] `MONGODB_URL` 설정 (따옴표 없이)
- [ ] `PORT` 환경변수 확인 (자동 설정됨)

### 3단계: 배포 실행
- [ ] Railway 대시보드에서 배포 시작
- [ ] 빌드 로그 확인
- [ ] 서버 시작 로그 확인

### 4단계: 기능 테스트
- [ ] `/health` 엔드포인트 테스트
- [ ] `/` 홈페이지 접속 테스트
- [ ] `/chat` 채팅 페이지 테스트
- [ ] 세션 생성/삭제 테스트

## 🔍 문제 해결 방법

### 로그 확인 방법
1. Railway 대시보드 → 프로젝트 → Deployments
2. 최신 배포 클릭 → Logs 탭
3. 오류 메시지 확인

### 일반적인 문제들

#### 1. 포트 충돌
**증상**: `[Errno 10048] error while attempting to bind`
**해결**: Railway에서 자동으로 포트 할당되므로 문제없음

#### 2. MongoDB 연결 실패
**증상**: `MongoDB 연결 실패`
**해결**: 
- Railway 환경변수에서 `MONGODB_URL` 확인
- 따옴표가 포함되어 있다면 제거
- MongoDB 서비스가 Railway에서 실행 중인지 확인

#### 3. OpenAI API 오류
**증상**: `OpenAI API 호출 실패`
**해결**:
- `OPENAI_API_KEY` 환경변수 확인
- API 키 유효성 확인
- OpenAI 계정 크레딧 확인

## 📊 성능 최적화

### Railway 환경 최적화
1. **단일 워커 사용**: `workers=1`
2. **Reload 비활성화**: `reload=False`
3. **색상 로그 비활성화**: `use_colors=False`
4. **필수 패키지만 설치**

### 메모리 사용량 최적화
1. **Redis 선택적 사용**: 연결 실패 시 메모리 캐시로 대체
2. **FAISS 선택적 사용**: 설치 실패 시 기본 기능으로 대체
3. **불필요한 모듈 로드 방지**

## 🎯 성공적인 배포 후 확인사항

### 1. 서버 상태 확인
```bash
curl https://your-app.railway.app/health
```

### 2. API 상태 확인
```bash
curl https://your-app.railway.app/api/status
```

### 3. 웹페이지 접속 확인
- 홈페이지: `https://your-app.railway.app/`
- 채팅페이지: `https://your-app.railway.app/chat`

## 📞 추가 지원

문제가 지속되는 경우:
1. Railway 로그 전체 복사
2. 환경변수 설정 확인
3. GitHub 이슈 생성 또는 문의

---

**마지막 업데이트**: 2025-07-08
**버전**: 2.0 (Railway 최적화) 