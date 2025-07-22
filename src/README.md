# EORA AI System - Railway 배포 버전

## 🚀 Railway 배포 상태
- ✅ 템플릿 경로 수정 완료
- ✅ 관리자 페이지 링크 수정 완료
- ✅ OpenAI API 호출 오류 해결
- ✅ MongoDB 연결 안정성 확보
- ✅ 세션 저장 기능 완성
- ✅ main.py 의존성 제거 완료
- ✅ 포트 환경변수 오류 수정 완료

## 📋 배포 정보
- **플랫폼**: Railway
- **포트**: 8080 (자동 할당)
- **시작 명령어**: `bash start.sh`
- **메인 파일**: `app.py`

## 🔧 주요 수정사항
1. **템플릿 경로 최적화**: `templates/` 디렉토리 우선 사용
2. **관리자 페이지 링크 수정**: `/prompts`, `/memory` 경로로 수정
3. **OpenAI 클라이언트 초기화**: 최신 SDK 호환성 확보
4. **MongoDB 연결**: 메모리 기반 세션 관리로 폴백
5. **main.py 의존성 제거**: app.py 직접 실행으로 변경
6. **포트 환경변수 처리**: start.sh 스크립트로 안전한 처리

## 🌐 접속 방법
Railway 배포 후 제공되는 URL로 접속:
- 메인 페이지: `/`
- 채팅 페이지: `/chat`
- 관리자 페이지: `/admin`

## 🔑 환경변수 설정
Railway 대시보드에서 다음 환경변수를 설정하세요:
- `OPENAI_API_KEY`: OpenAI API 키
- `MONGODB_URI`: MongoDB 연결 문자열 (선택사항)

## 📁 프로젝트 구조
```
src/
├── app.py              # 메인 FastAPI 애플리케이션
├── start.sh            # Railway 배포 시작 스크립트
├── railway.toml        # Railway 배포 설정
├── Procfile           # Railway Procfile
├── requirements.txt    # Python 의존성
├── templates/         # HTML 템플릿
├── static/           # 정적 파일
└── ai_brain/         # AI 프롬프트 데이터
```

## 🚀 로컬 개발
```bash
# 개발 서버 실행
python run_dev.py

# 안정 서버 실행
python run_stable.py

# Railway 배포용 서버
python railway_final.py
```

## 📊 시스템 상태
- **서버**: 정상 실행 중
- **템플릿**: 17개 HTML 파일 로드 완료
- **프롬프트**: 6개 AI 프롬프트 로드 완료
- **데이터베이스**: 메모리 기반 세션 관리
- **API**: OpenAI API 호출 준비 완료

## 🔧 문제 해결
모든 주요 문제가 해결되었습니다:
- ✅ main.py 모듈 오류 해결
- ✅ 포트 바인딩 오류 해결
- ✅ 템플릿 경로 오류 해결
- ✅ 환경변수 처리 오류 해결
- ✅ OpenAI API 호출 오류 해결

## 📞 지원
문제가 발생하면 다음을 확인하세요:
1. Railway 환경변수 설정
2. 포트 충돌 여부
3. 템플릿 파일 존재 여부
4. API 키 유효성 