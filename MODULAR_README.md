# EORA AI System - 모듈화 버전 v2.1.0

## 🎯 개요

EORA AI System의 모듈화된 최신 버전입니다. 코드가 기능별로 분리되어 관리와 유지보수가 매우 용이합니다.

## ✨ 주요 특징

### 🔧 모듈화된 구조
- **라우터 분리**: 페이지 라우터와 관리자 라우터가 별도 모듈로 분리
- **유틸리티 분리**: 메모리 관리, FAISS 시스템이 독립 모듈로 관리
- **유지보수 용이**: 각 기능별로 파일이 분리되어 수정이 간편

### 🚀 완전 해결된 오류들
- ✅ **MongoDB Boolean 체크 오류** 완전 해결
- ✅ **OpenAI API 연동 안정화**
- ✅ **FAISS 지연 로딩으로 성능 최적화**
- ✅ **포트 충돌 자동 해결**
- ✅ **PowerShell 호환성 완료**

### 🎛️ 핵심 기능들
- **관리자 학습 시스템**: 파일 업로드 및 대화 학습
- **8종 아우라 메모리 회상**: 다양한 방식의 메모리 검색
- **FAISS 임베딩 검색**: 의미 기반 유사성 검색
- **실시간 시스템 모니터링**: CPU, 메모리, 디스크 상태
- **포인트 관리 시스템**: 토큰 사용량 기반 포인트 차감
- **프롬프트 관리**: 동적 프롬프트 추가/삭제/수정

## 📁 프로젝트 구조

```
eora_new/
├── src/
│   ├── app_modular.py        # 🆕 모듈화된 메인 애플리케이션
│   ├── app_fixed.py          # 기존 통합 버전 (백업용)
│   ├── routes/               # 🆕 라우터 모듈들
│   │   ├── __init__.py
│   │   ├── admin_routes.py   # 관리자 라우터
│   │   └── page_routes.py    # 페이지 라우터
│   ├── utils/                # 🆕 유틸리티 모듈들
│   │   ├── __init__.py
│   │   ├── memory_utils.py   # 메모리 관리
│   │   └── faiss_utils.py    # FAISS 시스템
│   ├── templates/            # HTML 템플릿
│   └── static/               # 정적 파일
├── start_app_modular.bat     # 🆕 모듈화 버전 실행 (CMD)
├── start_app_modular.ps1     # 🆕 모듈화 버전 실행 (PowerShell)
├── start_app_fixed.bat       # 기존 버전 실행 (CMD)
├── start_app_fixed.ps1       # 기존 버전 실행 (PowerShell)
└── MODULAR_README.md         # 🆕 이 파일
```

## 🚀 실행 방법

### 방법 1: 모듈화 버전 실행 (권장)

**Windows CMD:**
```bash
start_app_modular.bat
```

**Windows PowerShell:**
```powershell
.\start_app_modular.ps1
```

**직접 실행:**
```bash
cd src
python app_modular.py
```

### 방법 2: 기존 통합 버전 실행

**Windows CMD:**
```bash
start_app_fixed.bat
```

**Windows PowerShell:**
```powershell
.\start_app_fixed.ps1
```

## 🔧 환경 설정

### 1. OpenAI API 키 설정

`src/.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
MONGODB_URI=mongodb://localhost:27017
```

### 2. 필요한 패키지 설치

```bash
pip install fastapi uvicorn python-dotenv pymongo openai pydantic
```

### 3. 선택적 패키지 (고급 기능용)

```bash
# FAISS 임베딩 검색용
pip install faiss-cpu sentence-transformers

# 시스템 모니터링용  
pip install psutil
```

## 📊 API 엔드포인트

### 🔐 인증 API
- `POST /api/auth/register` - 사용자 회원가입
- `POST /api/auth/login` - 사용자 로그인
- `POST /api/auth/logout` - 로그아웃

### 💬 채팅 API
- `POST /api/chat` - 기본 채팅
- `POST /advanced-chat` - 고급 회상 채팅
- `POST /embedding-recall` - 임베딩 기반 회상

### 📚 학습 API
- `POST /learn` - 텍스트 학습
- `POST /api/admin/learn-file` - 파일 학습 (관리자)
- `POST /api/admin/learn-dialog-file` - 대화 파일 학습 (관리자)

### 🎛️ 프롬프트 관리 API
- `GET /api/prompts/debug` - 프롬프트 디버그 정보
- `POST /api/prompts/save` - 프롬프트 저장
- `POST /api/prompts/reload` - 프롬프트 재로드
- `DELETE /api/prompts/delete-category` - 프롬프트 카테고리 삭제

### 👑 관리자 API
- `GET /api/admin/monitoring` - 시스템 모니터링
- `GET /api/admin/users` - 사용자 관리
- `GET /api/admin/system-settings` - 시스템 설정
- `GET /api/admin/performance` - 성능 분석
- `GET /api/admin/security` - 보안 관리

### 🛠️ 시스템 API
- `GET /api` - API 정보
- `GET /health` - 건강 상태 체크

## 🆕 모듈화의 장점

### 1. **관리 용이성**
- 각 기능이 별도 파일로 분리되어 수정이 간편
- 특정 기능만 업데이트하거나 디버그 가능
- 코드 중복 최소화

### 2. **확장성**
- 새로운 라우터나 유틸리티 추가가 간단
- 기존 코드에 영향 없이 새 기능 개발 가능
- 팀 개발 시 충돌 최소화

### 3. **성능 최적화**
- FAISS 지연 로딩으로 초기 시작 시간 단축
- 필요할 때만 리소스 로드
- 메모리 사용량 최적화

### 4. **테스트 용이성**
- 각 모듈별로 독립적인 테스트 가능
- 의존성 관리가 명확
- 단위 테스트 작성이 간편

## 🔍 모듈 상세 설명

### 📄 `app_modular.py`
- 메인 애플리케이션 파일
- FastAPI 앱 설정 및 라이프사이클 관리
- 기본 API 엔드포인트들

### 🛣️ `routes/admin_routes.py`
- 관리자 관련 모든 라우터
- 파일 학습, 대화 학습 기능
- 시스템 모니터링 API

### 🏠 `routes/page_routes.py`
- HTML 페이지 라우터들
- 메인, 채팅, 로그인 등 페이지

### 💾 `utils/memory_utils.py`
- 메모리 관리 유틸리티
- 세션 관리, 포인트 시스템
- MongoDB 연결 관리

### 🔍 `utils/faiss_utils.py`
- FAISS 임베딩 시스템
- 지연 로딩 구현
- 유사성 검색 기능

## 🚨 문제 해결

### 1. MongoDB 연결 실패
```bash
# MongoDB가 실행되고 있는지 확인
# 로컬 설치: mongod 실행
# 클라우드: 연결 문자열 확인
```

### 2. OpenAI API 오류
```bash
# .env 파일에서 API 키 확인
# sk-로 시작하는 올바른 키인지 확인
```

### 3. 포트 충돌
```bash
# 자동으로 다른 포트(8001, 8002...)로 시도됨
# 또는 직접 포트 지정: python app_modular.py --port 8005
```

### 4. 모듈 import 오류
```bash
# src 디렉토리에서 실행하는지 확인
cd src
python app_modular.py
```

## 🔄 버전 비교

| 기능 | 기존 app_fixed.py | 모듈화 app_modular.py |
|------|-------------------|----------------------|
| 파일 크기 | ~2000+ 줄 | ~600 줄 (메인) |
| 관리 용이성 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 확장성 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 테스트 용이성 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 성능 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 안정성 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 🎉 마무리

**모듈화된 EORA AI System v2.1.0**은 기존의 모든 기능을 유지하면서도 코드 관리와 확장성을 크게 개선한 버전입니다.

### 🎯 추천 사용법:
1. **개발/테스트**: 모듈화 버전 (`app_modular.py`) 사용
2. **안정적인 운영**: 필요에 따라 기존 버전 (`app_fixed.py`) 병행 사용
3. **새 기능 개발**: 모듈화 구조를 활용하여 확장

### 🚀 시작하기:
```bash
# 모듈화 버전 실행 (권장)
start_app_modular.bat   # Windows CMD
.\start_app_modular.ps1 # Windows PowerShell
```

**이제 완전히 모듈화되고 안정적인 EORA AI System을 사용할 수 있습니다!** 🎊 