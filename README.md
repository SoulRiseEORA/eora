# EORA AI System - 모듈화된 구조

## 개요

EORA AI System은 FastAPI 기반의 AI 채팅 및 메모리 시스템입니다. 이 프로젝트는 기존의 단일 파일 구조에서 모듈화된 구조로 리팩토링되었으며, Railway 환경에서의 배포를 최적화하였습니다.

## 디렉토리 구조

```
src/
├── api/                # API 라우트
│   └── routes.py       # API 엔드포인트 정의
├── models/             # Pydantic 모델
│   ├── auth.py         # 인증 관련 모델
│   └── session.py      # 세션 관련 모델
├── services/           # 서비스 레이어
│   └── openai_service.py  # OpenAI API 통합
├── templates/          # HTML 템플릿
├── static/             # 정적 파일
├── app_modular.py      # FastAPI 앱 메인 파일
├── auth_system.py      # 인증 시스템
├── aura_memory_system.py  # 아우라 메모리 시스템
├── database.py         # 데이터베이스 관리
└── run_railway_server.py  # Railway 최적화 서버 실행 스크립트
```

## 주요 컴포넌트

### 1. FastAPI 앱 (app_modular.py)

FastAPI 애플리케이션의 메인 파일로, 미들웨어 설정, 라우터 등록, 정적 파일 및 템플릿 설정을 담당합니다.

### 2. API 라우트 (api/routes.py)

API 엔드포인트를 정의하는 파일로, 세션 관리, 채팅, 인증 관련 API를 포함합니다.

### 3. 인증 시스템 (auth_system.py)

사용자 인증, JWT 토큰 생성 및 검증, 세션 관리를 담당합니다.

### 4. 데이터베이스 관리 (database.py)

MongoDB 연결 및 데이터 관리를 담당합니다. 사용자, 세션, 메시지 등의 CRUD 작업을 처리합니다.

### 5. OpenAI 서비스 (services/openai_service.py)

OpenAI API 통합 및 응답 생성, 프롬프트 관리를 담당합니다.

### 6. 아우라 메모리 시스템 (aura_memory_system.py)

사용자 대화 기억 및 회상 기능을 담당합니다. FAISS 기반 임베딩 검색을 지원합니다.

### 7. 모델 (models/)

Pydantic 기반 데이터 모델을 정의합니다. 세션, 인증 등의 모델을 포함합니다.

### 8. Railway 최적화 서버 (run_railway_server.py)

Railway 환경에 최적화된 서버 실행 스크립트로, 포트 자동 감지, 환경 감지 등의 기능을 제공합니다.

## 주요 기능

- **사용자 인증**: 회원가입, 로그인, 로그아웃, JWT 토큰 기반 인증
- **세션 관리**: 세션 생성, 조회, 삭제, 이름 변경
- **채팅**: OpenAI API를 활용한 AI 응답 생성
- **메모리 시스템**: 아우라 메모리 시스템을 통한 대화 저장 및 회상
- **관리자 기능**: 관리자 페이지, 프롬프트 관리

## 환경 변수

- `OPENAI_API_KEY`: OpenAI API 키
- `MONGODB_URL`: MongoDB 연결 URL
- `PORT`: 서버 포트 (기본값: 8002)
- `SECRET_KEY`: JWT 토큰 암호화 키

## 실행 방법

### 로컬 환경

```bash
cd src
python run_railway_server.py
```

### Railway 환경

Railway 환경에서는 자동으로 환경을 감지하여 최적화된 설정으로 실행됩니다.

## 개선사항

1. **모듈화**: 단일 파일에서 모듈화된 구조로 리팩토링하여 유지보수성 향상
2. **Railway 최적화**: Railway 환경에 최적화된 설정 및 에러 처리
3. **오류 처리 강화**: 다양한 예외 상황에 대한 처리 개선
4. **세션 관리 개선**: 세션 데이터 영구 저장 및 관리 기능 강화
5. **아우라 메모리 시스템**: 고급 메모리 및 회상 시스템 구현
6. **관리자 기능**: 관리자 페이지 및 프롬프트 관리 기능 추가 "# eora"  
