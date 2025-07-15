# EORA AI 시스템 배포 가이드

## 🚀 빠른 배포 방법

### 1. 자동 배포 스크립트 사용 (권장)

```bash
# 배포 스크립트 실행
install_git_and_deploy.bat
```

스크립트가 다음 작업을 자동으로 수행합니다:
- Git 설치 확인
- Git 저장소 초기화
- .gitignore 파일 생성
- 파일들을 Git에 추가
- GitHub 원격 저장소 연결
- GitHub에 푸시

### 2. 수동 배포 방법

#### 2.1 Git 설치
- https://git-scm.com/download/win 에서 Git 다운로드 및 설치

#### 2.2 Git 저장소 초기화
```bash
git init
git add .
git commit -m "Initial commit: EORA AI 시스템"
```

#### 2.3 GitHub 저장소 생성
1. GitHub.com에서 새 저장소 생성
2. 저장소 URL 복사 (예: https://github.com/username/eora-ai.git)

#### 2.4 GitHub에 푸시
```bash
git remote add origin https://github.com/username/eora-ai.git
git branch -M main
git push -u origin main
```

## 🚂 Railway 배포

### 1. Railway 프로젝트 생성
1. https://railway.app 접속
2. "New Project" 클릭
3. "Deploy from GitHub repo" 선택
4. GitHub 저장소 연결

### 2. 환경변수 설정
Railway 대시보드 > Variables에서 다음 환경변수 설정:

```
OPENAI_API_KEY=sk-your-openai-api-key-here
MONGO_URL=mongodb://username:password@mongodb.railway.internal:27017
MONGO_PUBLIC_URL=mongodb://username:password@trolley.proxy.rlwy.net:port
MONGO_INITDB_ROOT_USERNAME=your-mongo-username
MONGO_INITDB_ROOT_PASSWORD=your-mongo-password
```

### 3. MongoDB 추가
1. Railway 대시보드에서 "New Service" 클릭
2. "Database" > "MongoDB" 선택
3. MongoDB 서비스 생성 후 환경변수 자동 설정

### 4. 배포 확인
- Railway 대시보드에서 배포 상태 확인
- 제공된 URL로 접속하여 서비스 동작 확인

## 📋 배포 후 확인 사항

### 1. 기본 페이지 접속
- 홈: `https://your-app.railway.app/`
- 로그인: `https://your-app.railway.app/login`
- 채팅: `https://your-app.railway.app/chat`
- 테스트: `https://your-app.railway.app/test-chat`

### 2. API 엔드포인트 확인
- 상태 확인: `https://your-app.railway.app/api/status`
- 채팅 API: `https://your-app.railway.app/api/chat`

### 3. 관리자 계정
- 이메일: admin@eora.ai
- 비밀번호: admin1234

## 🔧 문제 해결

### 1. 배포 실패 시
- Railway 로그 확인
- 환경변수 설정 재확인
- requirements.txt 의존성 확인

### 2. MongoDB 연결 실패 시
- Railway MongoDB 서비스 상태 확인
- 환경변수 URL 형식 확인
- 네트워크 연결 확인

### 3. OpenAI API 오류 시
- API 키 유효성 확인
- API 키 할당량 확인
- 환경변수 설정 확인

## 📞 지원

문제가 발생하면 다음을 확인해주세요:
1. Railway 로그
2. 환경변수 설정
3. GitHub 저장소 상태
4. MongoDB 연결 상태

---

**배포 완료 후 EORA AI 시스템이 온라인에서 정상적으로 동작합니다! 🎉** 