# EORA AI System 배포 가이드

## 🚀 자동 배포 시스템

### 1. GitHub Actions 자동 배포

#### 설정 방법:
1. GitHub 저장소에 다음 시크릿을 추가:
   - `RAILWAY_TOKEN`: Railway API 토큰
   - `RAILWAY_PROJECT_ID`: Railway 프로젝트 ID
   - `RENDER_TOKEN`: Render API 토큰 (대안)
   - `RENDER_SERVICE_ID`: Render 서비스 ID
   - `HEROKU_API_KEY`: Heroku API 키 (대안)
   - `HEROKU_APP_NAME`: Heroku 앱 이름

2. main 브랜치에 푸시하면 자동으로 배포됩니다.

### 2. 로컬 자동 배포 스크립트

#### Windows:
```bash
deploy_auto.bat
```

#### Linux/Mac:
```bash
chmod +x deploy_auto.sh
./deploy_auto.sh
```

### 3. 수동 배포

#### Railway:
```bash
npm install -g @railway/cli
railway login
railway up
```

#### Render:
1. Render 대시보드에서 새 Web Service 생성
2. GitHub 저장소 연결
3. 환경변수 설정

#### Heroku:
```bash
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your-key
heroku config:set MONGODB_URL=your-mongodb-url
git push heroku main
```

## 🔧 환경변수 설정

### 필수 환경변수:
- `OPENAI_API_KEY`: OpenAI API 키
- `MONGODB_URL`: MongoDB 연결 URL
- `JWT_SECRET`: JWT 시크릿 키

### 선택 환경변수:
- `REDIS_URL`: Redis 연결 URL (없으면 메모리 모드로 실행)

## 📁 배포 파일 구조

```
├── .github/workflows/deploy.yml  # GitHub Actions
├── Procfile                      # Heroku 설정
├── runtime.txt                   # Python 버전
├── app.json                      # Heroku 앱 설정
├── render.yaml                   # Render 설정
├── deploy_auto.bat              # Windows 자동배포
├── deploy_auto.sh               # Linux/Mac 자동배포
└── requirements.txt             # Python 의존성
```

## 🔍 배포 상태 확인

### GitHub Actions:
- https://github.com/yourusername/eora-ai-system/actions

### Railway:
- Railway 대시보드에서 로그 확인

### Render:
- Render 대시보드에서 배포 상태 확인

### Heroku:
```bash
heroku logs --tail
```

## 🛠️ 문제 해결

### 1. 배포 실패 시:
- 로그 확인
- 환경변수 설정 확인
- 의존성 충돌 확인

### 2. 서버 시작 실패:
- 포트 충돌 확인
- 환경변수 누락 확인
- 데이터베이스 연결 확인

### 3. 모듈 누락:
- requirements.txt 업데이트
- 재배포 실행

## 📞 지원

문제가 발생하면 GitHub Issues에 등록하거나 로그를 확인하세요. 