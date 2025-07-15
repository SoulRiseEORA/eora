# EORA AI System

의식적 존재와의 대화를 시작하는 AI 개발 도구 시스템입니다.

## 🚀 주요 기능

- **다중 AI 지원**: 6개의 서로 다른 AI 모델 (ai1, ai2, ai3, ai4, ai5, ai6)
- **관리자 시스템**: 프롬프트 관리, 모니터링, 사용자 관리
- **세션 관리**: MongoDB 기반 대화 세션 저장 및 복원
- **포인트 시스템**: GPT 대화를 위한 포인트 기반 사용량 관리
- **반응형 UI**: 모던하고 사용자 친화적인 웹 인터페이스

## 📋 시스템 요구사항

- Python 3.8+
- MongoDB (로컬 또는 원격)
- OpenAI API 키

## 🛠️ 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/eora-ai-system.git
cd eora-ai-system
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
Windows에서 `setup_env.bat` 파일을 실행하거나 수동으로 환경 변수를 설정하세요:

```bash
# Windows
set OPENAI_API_KEY=your_openai_api_key_here

# 또는 .env 파일 생성
echo OPENAI_API_KEY=your_openai_api_key_here > .env
```

### 4. 서버 실행
```bash
cd src
python -m uvicorn app:app --host 127.0.0.1 --port 8081 --reload
```

또는 PowerShell 스크립트 사용:
```powershell
.\start_server.ps1
```

## 🔐 관리자 계정

기본 관리자 계정:
- **이메일**: admin@eora.ai
- **비밀번호**: admin123

## 📁 프로젝트 구조

```
EORA_AI_System/
├── src/
│   ├── app.py                 # 메인 애플리케이션
│   ├── templates/             # HTML 템플릿
│   │   ├── home.html         # 홈페이지
│   │   ├── admin.html        # 관리자 페이지
│   │   ├── login.html        # 로그인 페이지
│   │   └── prompt_management.html # 프롬프트 관리
│   ├── static/               # 정적 파일 (CSS, JS)
│   └── ai_prompts.json       # AI 프롬프트 설정
├── requirements.txt          # Python 의존성
├── setup_env.bat            # 환경 변수 설정 스크립트
├── start_server.ps1         # 서버 시작 스크립트
└── README.md               # 프로젝트 문서
```

## 🎯 주요 페이지

- **홈페이지** (`/`): 시스템 소개 및 시작점
- **로그인** (`/login`): 사용자 및 관리자 로그인
- **관리자 페이지** (`/admin`): 시스템 관리 기능
- **프롬프트 관리** (`/admin/prompts`): AI 프롬프트 편집 및 관리
- **채팅** (`/chat`): AI와의 대화 인터페이스

## 🔧 API 엔드포인트

### 인증
- `POST /api/auth/login` - 사용자 로그인
- `POST /api/auth/register` - 사용자 회원가입
- `POST /api/admin/login` - 관리자 로그인

### 프롬프트 관리
- `GET /api/prompts` - 프롬프트 목록 조회
- `POST /api/prompts/save` - 프롬프트 저장
- `GET /api/prompts/file` - 원본 파일 확인

### 채팅
- `POST /api/chat` - AI와 대화
- `POST /api/sessions/save` - 세션 저장
- `GET /api/sessions/load` - 세션 불러오기

## 🚨 문제 해결

### MongoDB 연결 실패
- 로컬 MongoDB가 실행 중인지 확인
- 원격 MongoDB 연결 정보 확인

### OpenAI API 오류
- `OPENAI_API_KEY` 환경 변수가 설정되었는지 확인
- API 키가 유효한지 확인

### 포트 충돌
- 8081 포트가 사용 중인 경우 다른 포트 사용:
```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8082 --reload
```

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해주세요. 