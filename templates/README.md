# EORA AI System

감정 중심 인공지능 플랫폼 EORA - 당신의 감정을 이해하는 AI 동반자

## 🚀 주요 기능

- **심리 상태 분석 및 감정 기반 대화**: AI가 감정 상태를 분석하고 공감적 대화 제공
- **전문 코칭 기반 성장 상담**: 전문적인 코칭 방법론을 바탕으로 한 성장 지향적 상담
- **맞춤형 챗봇 대화 인터페이스**: 자연스럽고 직관적인 대화 인터페이스
- **상담 기록 저장 및 회고 기능**: 모든 대화 내용을 안전하게 저장하고 회고
- **개인정보 보호를 위한 안전한 시스템**: 최고 수준의 보안 시스템
- **감정 목표 추적 및 동기 부여 시스템**: 감정과 목표를 연결한 실질적인 변화

## 🛠️ 기술 스택

- **Backend**: FastAPI, Python 3.11
- **Database**: MongoDB
- **Cache**: Redis (Graceful Fallback 지원)
- **AI**: OpenAI GPT-4
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Railway

## 📋 필수 환경 변수

배포 전에 다음 환경 변수를 설정해야 합니다:

```bash
# 필수
OPENAI_API_KEY=your_openai_api_key_here
MONGODB_URI=your_mongodb_connection_string
JWT_SECRET_KEY=your_jwt_secret_key

# 선택사항
PORT=8000  # 기본값: 8000

# Redis (선택사항 - 없으면 메모리 모드로 실행)
REDIS_URL=your_redis_connection_string
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0
```

## 🚀 배포 방법

### Railway 배포

1. **GitHub에 코드 푸시**
   ```bash
   git add .
   git commit -m "Add Redis graceful fallback support"
   git push origin main
   ```

2. **Railway에서 프로젝트 연결**
   - Railway.com에서 새 프로젝트 생성
   - GitHub 저장소 연결
   - 환경 변수 설정

3. **Redis 설정 (선택사항)**
   - Railway에서 Redis 서비스 추가
   - `RAILWAY_REDIS_SETUP.md` 참조

4. **자동 배포**
   - 코드 푸시 시 자동으로 배포됨
   - `start_server.py`가 시작 명령어로 사용됨
   - Redis 연결 실패 시 자동으로 메모리 모드로 전환

### 로컬 실행

1. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **Redis 설정 (선택사항)**
   ```bash
   # Docker로 Redis 실행
   docker run -d --name redis -p 6379:6379 redis:alpine
   ```

3. **서버 실행**
   ```bash
   python start_server.py
   ```

4. **접속**
   - http://localhost:8000

## 📁 프로젝트 구조

```
src/
├── main.py              # FastAPI 메인 애플리케이션
├── start_server.py      # 배포용 서버 실행 스크립트
├── redis_manager.py     # Redis 연결 관리자 (Graceful Fallback)
├── requirements.txt     # Python 의존성
├── railway.json         # Railway 배포 설정
├── deploy.bat          # Windows 배포 스크립트
├── RAILWAY_REDIS_SETUP.md # Redis 설정 가이드
├── templates/           # HTML 템플릿
│   ├── home.html        # 홈페이지
│   ├── chat.html        # 채팅 인터페이스
│   ├── dashboard.html   # 대시보드
│   ├── login.html       # 로그인 페이지
│   └── ...
└── ...
```

## 🔧 API 엔드포인트

- `GET /` - 홈페이지
- `GET /chat` - 채팅 인터페이스
- `GET /dashboard` - 사용자 대시보드
- `GET /health` - 서버 상태 확인
- `POST /api/chat` - 채팅 API
- `POST /api/auth/login` - 로그인 API
- `GET /api/sessions` - 세션 목록 API

## 🐛 문제 해결

### 서버 재시작 문제
- `--reload` 옵션을 비활성화하여 안정성 확보
- `start_server.py`에서 `reload=False` 설정

### 의존성 문제
- `requirements.txt`에 모든 필요한 패키지 포함
- `numpy` 의존성 추가로 aura 시스템 안정화

### 환경 변수 문제
- Railway 대시보드에서 환경 변수 확인
- 로컬에서는 `.env` 파일 사용

### Redis 연결 문제
- **Graceful Fallback**: Redis 연결 실패 시 자동으로 메모리 모드로 전환
- **Railway Redis**: `RAILWAY_REDIS_SETUP.md` 참조하여 Redis 서비스 추가
- **로컬 Redis**: Docker 또는 로컬 Redis 서버 설치

### 배포 안정성
- Redis 의존성 유지하면서 graceful fallback 지원
- 포트 환경 변수 지원으로 유연한 배포
- 서버 타임아웃 설정 최적화

## 🔄 Redis Graceful Fallback

시스템은 Redis 연결 실패 시 자동으로 메모리 모드로 전환됩니다:

```
⚠️ Redis 연결 실패: Connection refused
🔄 Redis 없이 메모리 모드로 실행됩니다.
```

### 메모리 모드 특징:
- **세션 데이터**: 애플리케이션 메모리에 임시 저장
- **캐시**: 메모리 기반 캐시 사용
- **성능**: Redis보다 제한적이지만 기본 기능은 정상 작동
- **재시작 시**: 메모리 데이터 초기화

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. 서버 로그 확인
2. 환경 변수 설정 상태
3. 데이터베이스 연결 상태
4. API 키 유효성
5. 포트 설정 확인
6. Redis 연결 상태 (선택사항)

## 📄 라이선스

ⓒ 2025 SoulRise Inc. - 감정 중심 인공지능 플랫폼 EORA 