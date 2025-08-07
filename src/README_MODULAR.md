# EORA AI 시스템 - 모듈화된 구조

## 개요
이 프로젝트는 EORA AI 시스템의 모듈화된 버전입니다. 기존의 단일 파일 구조에서 모듈화된 구조로 변경하여 코드의 가독성과 유지보수성을 향상시켰습니다.

## 폴더 구조
```
src/
  ├── api/                  # API 라우트 관련 코드
  │   ├── __init__.py
  │   └── routes.py         # API 엔드포인트 정의
  │
  ├── models/               # 데이터 모델 관련 코드
  │   ├── __init__.py
  │   ├── auth.py           # 인증 관련 모델
  │   └── session.py        # 세션 관련 모델
  │
  ├── services/             # 서비스 관련 코드
  │   ├── __init__.py
  │   └── openai_service.py # OpenAI 서비스
  │
  ├── app.py                # 원본 앱 파일 (모듈화되지 않음)
  ├── app_modular.py        # 모듈화된 메인 앱 파일
  ├── auth_system.py        # 인증 시스템
  ├── database.py           # 데이터베이스 관련 코드
  └── run_modular_server.py # 모듈화된 서버 실행 스크립트
```

## 모듈 설명

### api/routes.py
API 라우트 정의를 포함합니다. FastAPI의 APIRouter를 사용하여 엔드포인트를 정의하고, app_modular.py에서 이를 등록합니다.

### models/auth.py
인증 관련 모델 클래스를 정의합니다. 사용자 등록, 로그인, 토큰 응답 등의 모델이 포함됩니다.

### models/session.py
세션 관련 모델 클래스를 정의합니다. 세션 생성, 메시지 생성, 응답 포맷팅 등의 기능이 포함됩니다.

### services/openai_service.py
OpenAI API와의 통신을 담당하는 서비스 코드를 포함합니다. 응답 생성, 프롬프트 데이터 로드 등의 기능이 포함됩니다.

### app_modular.py
모듈화된 메인 앱 파일입니다. 분리된 모듈들을 import하여 사용하고, FastAPI 앱을 초기화합니다.

### auth_system.py
인증 시스템 관련 코드를 포함합니다. 사용자 인증, 세션 관리, 권한 관리 등의 기능이 포함됩니다.

### database.py
데이터베이스 연결 및 조작 관련 코드를 포함합니다. MongoDB 연결, 세션 및 메시지 저장/조회 등의 기능이 포함됩니다.

### run_modular_server.py
모듈화된 서버를 실행하는 스크립트입니다. app_modular.py에서 FastAPI 앱을 import하여 uvicorn으로 실행합니다.

## 실행 방법
모듈화된 서버를 실행하려면 다음 명령어를 사용하세요:

```bash
python run_modular_server.py
```

또는 Windows에서는 배치 파일을 사용할 수 있습니다:

```bash
start_modular_app.bat
```

## 주의사항
모듈화된 구조로 전환하면서 기존 코드의 동작을 최대한 유지하려고 했습니다. 하지만 일부 기능이 다르게 동작할 수 있으니 주의하세요.

## 중복 코딩 방지 대책
1. **모듈화된 구조**: 각 기능별로 모듈을 분리하여 중복 코딩을 방지합니다.
2. **명확한 책임 분리**: 각 모듈은 명확한 책임을 가지고 있어 중복 구현을 방지합니다.
3. **주석 처리**: 각 모듈 파일 상단에 "[app.py 분리]" 주석을 추가하여 분리된 코드임을 명시합니다.
4. **README 문서화**: 모듈 구조와 책임을 명확히 문서화하여 개발자가 쉽게 이해할 수 있도록 합니다. 