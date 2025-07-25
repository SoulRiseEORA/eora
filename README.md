# EORA AI System - Railway 최종 배포 버전 v2.0.0

## 🚀 개요

EORA AI System은 감정 중심 인공지능 플랫폼으로, Railway 환경에서 안정적으로 동작하도록 최적화되었습니다.

## ✅ 주요 수정사항

### 1. MongoDB Boolean Check 오류 해결
- `if not db:` → `if db is None:` 변경
- PyMongo Database 객체의 boolean 평가 오류 완전 해결

### 2. PowerShell 호환성 개선
- `&&` 연산자 대신 PowerShell 네이티브 명령어 사용
- `start_app.ps1` 스크립트 제공

### 3. 모듈화 구조
- `routes/` - 페이지 및 API 라우터
- `utils/` - 유틸리티 함수들
- 메인 `app.py` 파일 통합

## 📁 파일 구조

```
eora_new/
├── src/
│   ├── app.py                    # 메인 애플리케이션 (통합됨)
│   ├── app_fixed.py              # 수정된 버전 (참조용)
│   ├── app_modular.py            # 모듈화 버전 (참조용)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── admin_routes.py       # 관리자 라우터
│   │   └── page_routes.py        # 페이지 라우터
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── memory_utils.py       # 메모리 관리
│   │   └── faiss_utils.py        # FAISS 임베딩
│   ├── templates/                # HTML 템플릿
│   ├── static/                   # 정적 파일
│   └── requirements.txt          # 의존성 목록
├── start_app.ps1                 # PowerShell 시작 스크립트
├── start_app.bat                 # Windows 배치 파일
└── README.md                     # 이 파일
```

## 🛠️ 설치 및 실행

### 1. 의존성 설치

```bash
cd src
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env` 파일을 생성하고 다음 내용을 추가:

```env
OPENAI_API_KEY=your_openai_api_key_here
MONGODB_URI=your_mongodb_connection_string
PORT=8001
```

### 3. 서버 실행

#### PowerShell 사용:
```powershell
.\start_app.ps1
```

#### Windows 배치 파일 사용:
```cmd
start_app.bat
```

#### 직접 실행:
```bash
cd src
python -m uvicorn app:app --host 127.0.0.1 --port 8001 --reload
```

## 🔧 주요 기능

### 1. 채팅 시스템
- OpenAI GPT 모델 연동
- 세션 관리
- 메모리 기반 대화 저장

### 2. 아우라 메모리 시스템
- 감정 기반 메모리 저장
- 회상 기능
- 중요도 기반 필터링

### 3. 관리자 기능
- 파일 학습
- 프롬프트 관리
- 사용자 관리
- 시스템 모니터링

### 4. FAISS 임베딩
- 텍스트 유사성 검색
- 지연 로딩으로 성능 최적화

## 🐛 문제 해결

### 1. MongoDB 연결 오류
```python
# 수정된 코드
if db is None:
    logger.warning("⚠️ MongoDB 연결되지 않음")
```

### 2. PowerShell 호환성
```powershell
# 올바른 방법
Set-Location src
python -m uvicorn app:app --host 127.0.0.1 --port 8001
```

### 3. 포트 충돌
- 자동으로 8002, 8003, 8004, 8005 포트 시도
- `start_app.ps1`에서 자동 처리

## 📊 API 엔드포인트

### 기본 엔드포인트
- `GET /` - 메인 페이지
- `GET /health` - 서버 상태 확인
- `GET /api` - API 정보

### 채팅 API
- `POST /api/chat` - 채팅 메시지 처리
- `GET /chat` - 채팅 페이지

### 관리자 API
- `POST /api/admin/learn-file` - 파일 학습
- `GET /api/admin/monitoring` - 시스템 모니터링

### 인증 API
- `POST /api/auth/login` - 로그인
- `POST /api/auth/register` - 회원가입

## 🔍 테스트

### 1. 서버 상태 확인
```bash
curl http://127.0.0.1:8001/health
```

### 2. 채팅 테스트
```bash
curl -X POST http://127.0.0.1:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요"}'
```

## 📝 로그 확인

서버 실행 시 다음과 같은 로그를 확인할 수 있습니다:

```
🚀 EORA AI System 시작 중...
✅ MongoDB 연결 성공
✅ OpenAI API 키 설정 성공
✅ 프롬프트 데이터 로드 완료
✅ 아우라 메모리 시스템 초기화 완료
```

## 🚀 Railway 배포

Railway 환경에서는 다음 환경변수를 설정하세요:

- `OPENAI_API_KEY`
- `MONGODB_URI`
- `PORT` (자동 설정됨)

## 📞 지원

문제가 발생하면 다음을 확인하세요:

1. 의존성 설치 완료 여부
2. 환경변수 설정 여부
3. MongoDB 연결 상태
4. OpenAI API 키 유효성

## 🔄 업데이트 내역

### v2.0.0 (2025-07-24)
- MongoDB boolean check 오류 완전 해결
- PowerShell 호환성 개선
- 모듈화 구조 적용
- 자동 포트 충돌 해결
- 포괄적인 오류 처리 추가 