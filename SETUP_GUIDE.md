# 🚀 EORA AI 시스템 설정 가이드

## 📋 환경 설정

### 1. `.env` 파일 생성
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# OpenAI API Keys (GPT 분할 분리)
OPENAI_API_KEY_1=실제_OpenAI_API_키_1
OPENAI_API_KEY_2=실제_OpenAI_API_키_2
OPENAI_API_KEY_3=실제_OpenAI_API_키_3
OPENAI_API_KEY_4=실제_OpenAI_API_키_4
OPENAI_API_KEY_5=실제_OpenAI_API_키_5

# Primary Key (기본 우선 키 사용 값)
OPENAI_API_KEY=실제_기본_OpenAI_API_키

# Required for project-scoped keys
OPENAI_PROJECT_ID=실제_프로젝트_ID

# GPT 모델 설정
GPT_MODEL=gpt-4o
MAX_TOKENS=2048
TEMPERATURE=0.7

# GitHub 설정 (선택사항)
GITHUB_TOKEN=실제_GitHub_토큰

# Snyk 보안 검사 토큰 (선택사항)
SNYK_TOKEN=실제_Snyk_토큰

# REPLICATE_API_TOKEN (선택사항)
REPLICATE_API_TOKEN=실제_Replicate_토큰

# Redis 캐시 설정
REDIS_URI=redis://127.0.0.1:6379/0
CACHE_TTL_SECONDS=3600

# MongoDB 설정
MONGODB_URI=mongodb://localhost:27017
MONGO_DB=aura_memory
ENABLE_MONGO=true
MONGODB_USERNAME=
MONGODB_PASSWORD=
USER_ID=test_user
```

### 2. OpenAI API 키 발급

1. https://platform.openai.com 접속
2. API Keys 페이지에서 새 키 생성
3. 생성된 키를 `.env` 파일에 추가

### 3. 서버 실행

```bash
python fixed_server.py
```

### 4. 접속 주소

- **홈페이지**: http://127.0.0.1:8300
- **로그인**: http://127.0.0.1:8300/login
- **채팅**: http://127.0.0.1:8300/chat
- **관리자**: http://127.0.0.1:8300/admin

### 5. 기본 관리자 계정

- **이메일**: admin@eora.ai
- **비밀번호**: admin123

## 🎯 주요 기능

- ✅ 관리자 대시보드
- ✅ 프롬프트 관리 시스템 (ai_prompts.json CRUD)
- ✅ 8종 회상 시스템 (키워드, 임베딩, 시퀀스, 메타데이터, 감정, 트리거, 빈도, 신념)
- ✅ 직관, 통찰, 지혜 기능
- ✅ 학습 전용 페이지 (문서/대화 학습)
- ✅ 상세 디버그 로그 시스템
- ✅ 실시간 웹 로그 표시

## 🔧 문제 해결

### 로컬과 서버 차이점
- 로컬에서 실행할 때: `fixed_server.py` 사용
- Railway/클라우드 배포: `railway_perfect.py` 또는 `app.py` 사용
- 환경 변수 설정이 다를 수 있으므로 `.env` 파일 확인 필요

### 포트 충돌 해결
```bash
# 기존 프로세스 종료
Get-Process | Where-Object {$_.Name -eq "python"} | Stop-Process -Force

# 포트 확인
netstat -an | findstr ":8300"
``` 