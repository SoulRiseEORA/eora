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
- **AI**: OpenAI GPT-4
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Railway

## 📋 필수 환경 변수

배포 전에 다음 환경 변수를 설정해야 합니다:

```bash
OPENAI_API_KEY=your_openai_api_key_here
MONGODB_URI=your_mongodb_connection_string
JWT_SECRET_KEY=your_jwt_secret_key
PORT=8000  # 선택사항, 기본값: 8000
```

## 🚀 배포 방법

### Railway 배포

1. **GitHub에 코드 푸시**
   ```bash
   git add .
   git commit -m "Remove Redis dependency and optimize deployment"
   git push origin main
   ```

2. **Railway에서 프로젝트 연결**
   - Railway.com에서 새 프로젝트 생성
   - GitHub 저장소 연결
   - 환경 변수 설정

3. **자동 배포**
   - 코드 푸시 시 자동으로 배포됨
   - `start_server.py`가 시작 명령어로 사용됨
   - Redis 의존성 제거로 안정성 향상

### 로컬 실행

1. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **서버 실행**
   ```bash
   python start_server.py
   ```

3. **접속**
   - http://localhost:8000

## 📁 프로젝트 구조

```
src/
├── main.py              # FastAPI 메인 애플리케이션
├── start_server.py      # 배포용 서버 실행 스크립트
├── requirements.txt     # Python 의존성 (Redis 제거)
├── railway.json         # Railway 배포 설정
├── deploy.bat          # Windows 배포 스크립트
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
- `requirements.txt`에서 Redis 의존성 제거
- `numpy` 의존성 추가로 aura 시스템 안정화

### 환경 변수 문제
- Railway 대시보드에서 환경 변수 확인
- 로컬에서는 `.env` 파일 사용

### 배포 안정성
- Redis 의존성 제거로 연결 오류 방지
- 포트 환경 변수 지원으로 유연한 배포
- 서버 타임아웃 설정 최적화

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. 서버 로그 확인
2. 환경 변수 설정 상태
3. 데이터베이스 연결 상태
4. API 키 유효성
5. 포트 설정 확인

## 📄 라이선스

ⓒ 2025 SoulRise Inc. - 감정 중심 인공지능 플랫폼 EORA 