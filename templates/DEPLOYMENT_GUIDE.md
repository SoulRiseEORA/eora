# EORA AI System 배포 가이드

## 🚀 배포 방법

### Windows PowerShell에서 배포

**⚠️ 중요: PowerShell에서는 `&&` 구문을 사용할 수 없습니다. 명령어를 분리해서 실행하세요.**

```powershell
# 1. 상위 디렉토리로 이동
cd ..

# 2. Git 상태 확인
git status

# 3. 변경사항 추가
git add .

# 4. 커밋
git commit -m "배포 업데이트: ObjectId 직렬화 문제 해결 및 API 엔드포인트 추가"

# 5. GitHub에 푸시
git push origin main
```

### 배치 파일 사용 (권장)

```powershell
# 배치 파일 실행
.\deploy.bat
```

## 📋 배포 전 확인사항

### 1. 환경변수 설정 확인
- `OPENAI_API_KEY`: OpenAI API 키
- `MONGODB_URL`: MongoDB 연결 URL
- `REDIS_URL`: Redis 연결 URL (선택사항)
- `JWT_SECRET`: JWT 시크릿 키

### 2. 파일 구조 확인
```
src/
├── main.py              # 메인 서버 파일
├── requirements.txt     # Python 의존성
├── railway.json        # Railway 배포 설정
├── deploy.bat          # 배포 스크립트
└── templates/          # HTML 템플릿
    ├── home.html
    ├── chat.html
    └── ...
```

### 3. 주요 수정사항 확인

#### ✅ 해결된 문제들:
- MongoDB ObjectId 직렬화 오류
- 누락된 API 엔드포인트 404 오류
- PowerShell `&&` 구문 오류
- 서버 재시작 문제
- 헬스체크 타임아웃 문제

#### 🔧 추가된 기능:
- 기본 세션 및 메시지 API (인증 없이)
- 사용자 정보 API (더미 데이터)
- 아우라 시스템 API
- 포인트 시스템 API
- 대화 관리 API

## 🌐 배포 후 확인

### 1. Railway 대시보드
- 배포 상태 확인
- 로그 확인
- 환경변수 설정 확인

### 2. 헬스체크
- `/health` 엔드포인트 접속
- 서비스 상태 확인

### 3. API 테스트
- `/api/status` - API 상태 확인
- `/api/sessions` - 세션 목록
- `/api/chat` - 채팅 기능

## 🔍 문제 해결

### 배포 실패 시:
1. Railway 로그 확인
2. 환경변수 재설정
3. 코드 재배포

### 서버 오류 시:
1. 로그 확인
2. 의존성 설치 확인
3. 포트 충돌 확인

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. Railway 로그
2. 환경변수 설정
3. 코드 문법 오류 