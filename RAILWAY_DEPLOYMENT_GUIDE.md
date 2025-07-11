# 🚀 Railway 배포 가이드

## 📋 사전 준비

### 1. Railway 계정 생성
- https://railway.app 접속
- GitHub 계정으로 로그인

### 2. GitHub 저장소 준비
- 프로젝트를 GitHub에 푸시
- `railway_requirements.txt` 파일이 포함되어 있는지 확인

## 🔧 배포 단계

### 1. Railway 프로젝트 생성
1. Railway 대시보드에서 "New Project" 클릭
2. "Deploy from GitHub repo" 선택
3. GitHub 저장소 선택

### 2. 환경변수 설정
Railway 대시보드에서 다음 환경변수들을 설정:

```
OPENAI_API_KEY=sk-your-openai-api-key-here
MONGODB_URL=mongodb://localhost:27017/eora_ai
PORT=8000
ENVIRONMENT=production
```

### 3. 배포 설정 확인
- **Build Command**: `pip install -r railway_requirements.txt`
- **Start Command**: `python railway_main.py`
- **Port**: `8000`

## 🚨 문제 해결

### itsdangerous 모듈 오류
만약 다음과 같은 오류가 발생한다면:
```
ModuleNotFoundError: No module named 'itsdangerous'
```

**해결 방법:**
1. `railway_requirements.txt`에 다음 라인 추가:
```
itsdangerous==2.1.2
```

2. GitHub에 변경사항 푸시
3. Railway에서 자동 재배포 대기

### 기타 의존성 문제
필요한 경우 다음 패키지들도 추가:
```
starlette==0.27.0
python-dotenv==1.0.0
aiofiles==23.2.1
```

## ✅ 배포 확인

### 1. 배포 상태 확인
- Railway 대시보드에서 배포 로그 확인
- "Deployments" 탭에서 배포 상태 모니터링

### 2. 애플리케이션 테스트
배포 완료 후 제공된 URL로 접속하여 테스트:
- 홈페이지: `https://your-app-name.railway.app/`
- AURA 시스템: `https://your-app-name.railway.app/aura_system`
- 채팅: `https://your-app-name.railway.app/chat`

### 3. 로그 확인
Railway 대시보드에서 실시간 로그 확인:
- 애플리케이션 시작 로그
- 오류 메시지
- 요청/응답 로그

## 🔄 업데이트 배포

### 자동 배포
- GitHub 저장소에 푸시하면 자동으로 재배포
- `railway_requirements.txt` 변경 시 자동으로 의존성 재설치

### 수동 재배포
Railway 대시보드에서:
1. "Deployments" 탭 클릭
2. "Redeploy" 버튼 클릭

## 📊 모니터링

### 성능 모니터링
- Railway 대시보드에서 CPU, 메모리 사용량 확인
- 응답 시간 모니터링

### 오류 모니터링
- 실시간 로그 스트림 확인
- 오류 알림 설정

## 🛠️ 추가 설정

### 커스텀 도메인
1. Railway 프로젝트 설정에서 "Custom Domains" 클릭
2. 도메인 추가 및 DNS 설정

### SSL 인증서
- Railway에서 자동으로 SSL 인증서 제공
- HTTPS 리다이렉션 자동 설정

## 📞 지원

문제가 발생하면:
1. Railway 로그 확인
2. 의존성 파일 검증
3. 환경변수 설정 확인
4. GitHub 저장소 상태 확인

---

**참고:** Railway는 무료 티어에서 월 500시간 제공하며, 추가 사용 시 요금이 발생할 수 있습니다. 