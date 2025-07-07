# EORA AI System

감정 중심 인공지능 플랫폼 EORA - 당신의 감정을 이해하는 AI 동반자

## 🚀 주요 기능

- **심리 상태 분석 및 감정 기반 대화**: AI가 감정 상태를 분석하고 공감적 대화 제공
- **전문 코칭 기반 성장 상담**: 전문적인 코칭 방법론을 바탕으로 한 성장 지향적 상담
- **맞춤형 챗봇 대화 인터페이스**: 자연스럽고 직관적인 대화 인터페이스
- **상담 기록 저장 및 회고 기능**: 모든 대화 내용을 안전하게 저장하고 회고
- **개인정보 보호를 위한 안전한 시스템**: 최고 수준의 보안 시스템
- **감정 목표 추적 및 동기 부여 시스템**: 감정과 목표를 연결한 실질적인 변화
- **FAISS 임베딩 기반 대화 관리**: 과거 대화 내용을 임베딩으로 저장하고 유사한 대화 검색
- **지능형 대화 회상 시스템**: 문맥을 이해하고 관련된 과거 대화를 참조하여 더 나은 응답 제공

## 🛠️ 기술 스택

- **Backend**: FastAPI, Python 3.11
- **Database**: MongoDB
- **Cache**: Redis (Graceful Fallback 지원)
- **AI**: OpenAI GPT-4
- **Embedding**: FAISS, Sentence Transformers
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
   git commit -m "Add FAISS embedding system and optimize deployment"
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
├── main.py              # FastAPI 메인 애플리케이션 (FAISS 임베딩 시스템 포함)
├── start_server.py      # 배포용 서버 실행 스크립트
├── redis_manager.py     # Redis 연결 관리자 (Graceful Fallback)
├── requirements.txt     # Python 의존성 (FAISS, Sentence Transformers 포함)
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
- `POST /api/chat` - 채팅 API (FAISS 임베딩 기반)
- `POST /api/auth/login` - 로그인 API
- `GET /api/sessions` - 세션 목록 API
- `WebSocket /ws/{session_id}` - 실시간 채팅

## 🧠 FAISS 임베딩 시스템

### 주요 기능
- **대화 임베딩 저장**: 모든 대화를 벡터로 변환하여 저장
- **유사도 검색**: 현재 대화와 유사한 과거 대화 검색
- **컨텍스트 제공**: 관련된 과거 대화를 참조하여 더 나은 응답 생성
- **실시간 학습**: 새로운 대화가 추가될 때마다 임베딩 인덱스 업데이트

### 기술적 특징
- **Sentence Transformers**: 한국어에 최적화된 임베딩 모델 사용
- **FAISS**: Facebook AI Similarity Search로 빠른 벡터 검색
- **Cosine Similarity**: 벡터 간 유사도 계산
- **메타데이터 저장**: 각 임베딩에 대화 정보 저장

### 사용 예시
```python
# 메시지 임베딩 추가
embedding_manager.add_message("안녕하세요", "user", "session_123")

# 유사한 대화 검색
similar_messages = embedding_manager.search_similar("안녕하세요", k=5)

# AI 응답 생성 시 컨텍스트 활용
context = "관련된 과거 대화:\n"
for msg in similar_messages:
    context += f"{msg['role']}: {msg['message']}\n"
```

## 🐛 문제 해결

### 서버 재시작 문제
- `--reload` 옵션을 비활성화하여 안정성 확보
- `start_server.py`에서 `reload=False` 설정
- 타임아웃 및 연결 제한 설정 최적화

### 의존성 문제
- `requirements.txt`에 모든 필요한 패키지 포함
- `faiss-cpu`, `sentence-transformers` 의존성 추가
- `numpy` 의존성 추가로 aura 시스템 안정화

### 환경 변수 문제
- Railway 대시보드에서 환경 변수 확인
- 로컬에서는 `.env` 파일 사용

### Redis 연결 문제
- **Graceful Fallback**: Redis 연결 실패 시 자동으로 메모리 모드로 전환
- **Railway Redis**: `RAILWAY_REDIS_SETUP.md` 참조하여 Redis 서비스 추가
- **로컬 Redis**: Docker 또는 로컬 Redis 서버 설치

### FAISS 모듈 문제
- **CPU 버전 사용**: `faiss-cpu`로 메모리 사용량 최적화
- **모델 다운로드**: 첫 실행 시 Sentence Transformers 모델 자동 다운로드
- **메모리 관리**: 대용량 임베딩 데이터의 경우 메모리 사용량 모니터링

### 배포 안정성
- Redis 의존성 유지하면서 graceful fallback 지원
- 포트 환경 변수 지원으로 유연한 배포
- 서버 타임아웃 설정 최적화
- FAISS 임베딩 시스템 초기화 실패 시 기본 모드로 전환

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
7. FAISS 임베딩 시스템 상태

## 📄 라이선스

ⓒ 2025 SoulRise Inc. - 감정 중심 인공지능 플랫폼 EORA 