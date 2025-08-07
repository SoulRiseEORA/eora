# 🚀 EORA AI GitHub 배포 단계별 가이드

## 1단계: Git 설치

### Windows용 Git 설치
1. https://git-scm.com/download/win 접속
2. "Click here to download" 클릭
3. 다운로드된 설치 파일 실행
4. 기본 설정으로 설치 진행
5. 설치 완료 후 컴퓨터 재시작

### 설치 확인
```bash
git --version
```

## 2단계: GitHub 저장소 생성

### GitHub에서 새 저장소 만들기
1. https://github.com 접속 및 로그인
2. 우측 상단 "+" 버튼 클릭 → "New repository"
3. 저장소 이름 입력 (예: `eora-ai`)
4. "Public" 또는 "Private" 선택
5. "Create repository" 클릭
6. 저장소 URL 복사 (예: `https://github.com/username/eora-ai.git`)

## 3단계: 로컬 Git 저장소 설정

### 현재 디렉토리에서 Git 초기화
```bash
# 현재 디렉토리 확인
pwd

# Git 저장소 초기화
git init

# 파일들을 Git에 추가
git add .

# 첫 번째 커밋 생성
git commit -m "Initial commit: EORA AI 시스템 배포"
```

### GitHub 원격 저장소 연결
```bash
# 원격 저장소 추가 (YOUR_GITHUB_URL을 실제 URL로 변경)
git remote add origin https://github.com/username/eora-ai.git

# 메인 브랜치로 설정
git branch -M main

# GitHub에 푸시
git push -u origin main
```

## 4단계: Railway 배포

### Railway 프로젝트 생성
1. https://railway.app 접속
2. "New Project" 클릭
3. "Deploy from GitHub repo" 선택
4. GitHub 계정 연결
5. EORA AI 저장소 선택

### 환경변수 설정
Railway 대시보드 > Variables에서 다음 설정:

```
OPENAI_API_KEY=sk-your-openai-api-key-here
MONGO_URL=mongodb://username:password@mongodb.railway.internal:27017
MONGO_PUBLIC_URL=mongodb://username:password@trolley.proxy.rlwy.net:port
MONGO_INITDB_ROOT_USERNAME=your-mongo-username
MONGO_INITDB_ROOT_PASSWORD=your-mongo-password
```

### MongoDB 추가
1. Railway 대시보드에서 "New Service" 클릭
2. "Database" > "MongoDB" 선택
3. MongoDB 서비스 생성

## 5단계: 배포 확인

### 기본 페이지 접속
- 홈: `https://your-app.railway.app/`
- 로그인: `https://your-app.railway.app/login`
- 채팅: `https://your-app.railway.app/chat`
- 테스트: `https://your-app.railway.app/test-chat`

### 관리자 계정
- 이메일: `admin@eora.ai`
- 비밀번호: `admin1234`

## 🔧 문제 해결

### Git 관련 문제
```bash
# Git 설정 확인
git config --list

# 사용자 정보 설정
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Railway 배포 실패
1. Railway 로그 확인
2. 환경변수 설정 재확인
3. requirements.txt 의존성 확인

### MongoDB 연결 실패
1. Railway MongoDB 서비스 상태 확인
2. 환경변수 URL 형식 확인
3. 네트워크 연결 확인

## 📞 지원

문제가 발생하면 다음을 확인해주세요:
1. Git 설치 상태
2. GitHub 저장소 권한
3. Railway 환경변수 설정
4. MongoDB 연결 상태

---

**배포 완료 후 EORA AI 시스템이 온라인에서 정상적으로 동작합니다! 🎉** 