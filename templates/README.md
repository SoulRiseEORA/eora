# EORA AI System - 감정 중심 인공지능 플랫폼

## 🚀 최신 업데이트 (2024년 12월)

### ✅ 해결된 주요 문제들:
- **MongoDB ObjectId 직렬화 오류** - JSON 응답에서 ObjectId 처리 개선
- **PowerShell `&&` 구문 오류** - Windows 호환성 개선
- **누락된 API 엔드포인트** - 프론트엔드 요청 API 추가
- **서버 재시작 문제** - 파일 변경 감지 최적화
- **헬스체크 타임아웃** - Railway 배포 설정 개선

### 🔧 추가된 기능:
- 기본 세션 및 메시지 API (인증 없이)
- 사용자 정보 API (더미 데이터)
- 아우라 시스템 API
- 포인트 시스템 API
- 대화 관리 API

## 📋 빠른 시작

### 1. 로컬 테스트
```powershell
# PowerShell에서 (명령어 분리 실행)
cd ..
python test_server.py
```

### 2. 배포
```powershell
# 간단한 배포 스크립트 사용 (권장)
.\simple_deploy.bat

# 또는 수동 배포
cd ..
git add .
git commit -m "배포 업데이트: 최종 수정사항 적용"
git push origin main
```

## 🌟 주요 기능

### 🤖 AI 채팅 시스템
- OpenAI GPT API 통합
- 실시간 웹소켓 통신
- 대화 기록 저장 및 관리

### 🧠 FAISS 임베딩 시스템
- 대화 내용 임베딩
- 유사 대화 검색
- 컨텍스트 기반 응답

### 💾 데이터베이스 통합
- MongoDB: 메시지 및 세션 저장
- Redis: 캐싱 및 세션 관리 (Graceful Fallback 지원)

### 🎨 웹 인터페이스
- 반응형 디자인
- 실시간 채팅
- 대시보드 및 관리 페이지

## 🛠️ 기술 스택

- **Backend**: FastAPI, Python 3.11
- **Database**: MongoDB, Redis
- **AI**: OpenAI GPT, FAISS, Sentence Transformers
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Railway, GitHub Actions

## 📁 프로젝트 구조

```
src/
├── main.py              # 메인 서버 파일
├── test_server.py       # 테스트 서버
├── requirements.txt     # Python 의존성
├── railway.json        # Railway 배포 설정
├── deploy.bat          # 배포 스크립트
├── simple_deploy.bat   # 간단 배포 스크립트
└── templates/          # HTML 템플릿
    ├── home.html       # 홈페이지
    ├── chat.html       # 채팅 페이지
    ├── dashboard.html  # 대시보드
    └── ...
```

## 🔧 환경변수 설정

### Railway 환경변수:
- `OPENAI_API_KEY`: OpenAI API 키
- `MONGODB_URL`: MongoDB 연결 URL
- `REDIS_URL`: Redis 연결 URL (선택사항)
- `JWT_SECRET`: JWT 시크릿 키

## 🚀 배포 방법

### 1. 자동 배포 (권장)
```powershell
.\simple_deploy.bat
```

### 2. 수동 배포
```powershell
# PowerShell에서 명령어 분리 실행
cd ..
git add .
git commit -m "배포 업데이트"
git push origin main
```

### 3. 배포 확인
- Railway 대시보드에서 배포 상태 확인
- `/health` 엔드포인트로 헬스체크
- `/api/status`로 API 상태 확인

## 🔍 문제 해결

### 배포 실패 시:
1. Railway 로그 확인
2. 환경변수 재설정
3. 코드 재배포

### 로컬 실행 문제:
1. 포트 충돌 확인 (8000, 8003 등)
2. 의존성 설치 확인
3. 환경변수 설정 확인

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. Railway 로그
2. 환경변수 설정
3. 코드 문법 오류

## 📄 라이선스

MIT License

---

**EORA AI System** - 감정 중심 인공지능 플랫폼으로 더 나은 대화 경험을 제공합니다. 