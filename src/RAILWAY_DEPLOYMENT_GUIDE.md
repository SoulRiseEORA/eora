# 🚀 Railway 배포 가이드

## 📋 최신 업데이트 (2025-07-22)

### 🔧 해결된 문제
- **JWT 모듈 누락**: `PyJWT==2.8.0` 추가
- **numpy 모듈 누락**: `numpy==1.24.3` 추가
- **sentence-transformers 누락**: `sentence-transformers==2.2.2` 추가
- **faiss-cpu 누락**: `faiss-cpu==1.7.4` 추가
- **기타 의존성**: MongoDB, Redis, WebSocket 등 추가

## 🚀 배포 방법

### 1. 자동 배포 (권장)
```bash
# Windows
deploy_to_railway_fixed.bat

# PowerShell
.\deploy_to_railway_fixed.ps1

# 빠른 배포
quick_deploy_railway.bat
```

### 2. 수동 배포
```bash
git add .
git commit -m "🔧 JWT/numpy 의존성 문제 해결"
git push railway main
```

## 📦 의존성 패키지

### 핵심 패키지
- `PyJWT==2.8.0` - JWT 토큰 인증
- `numpy==1.24.3` - 수치 계산
- `sentence-transformers==2.2.2` - 텍스트 임베딩
- `faiss-cpu==1.7.4` - 벡터 검색

### 데이터베이스 & 캐싱
- `pymongo==4.6.0` - MongoDB 연결
- `redis==5.0.1` - 캐싱

### 웹 프레임워크
- `fastapi==0.104.1` - API 프레임워크
- `uvicorn[standard]==0.24.0` - ASGI 서버
- `jinja2==3.1.2` - 템플릿 엔진

### 실시간 통신
- `websockets==12.0` - WebSocket 지원

### 시스템 모니터링
- `psutil==5.9.6` - 시스템 리소스 모니터링

## 🔍 배포 후 테스트

1. **메인 페이지**: https://web-production-40c0.up.railway.app/
2. **관리자 페이지**: https://web-production-40c0.up.railway.app/admin
3. **프롬프트 관리**: https://web-production-40c0.up.railway.app/admin/prompt-management
4. **채팅 기능**: https://web-production-40c0.up.railway.app/chat

## ⚠️ 주의사항

- 레일웨이에서 Python 3.12 사용
- 모든 의존성은 `railway_requirements.txt`에 명시
- 환경변수는 Railway 대시보드에서 설정
- MongoDB 연결은 Railway MongoDB 플러그인 사용

## 🐛 문제 해결

### JWT 모듈 오류
```bash
ModuleNotFoundError: No module named 'jwt'
```
**해결**: `PyJWT==2.8.0` 패키지 추가

### numpy 모듈 오류
```bash
ModuleNotFoundError: No module named 'numpy'
```
**해결**: `numpy==1.24.3` 패키지 추가

### 기타 의존성 오류
모든 필요한 패키지가 `railway_requirements.txt`에 포함되어 있습니다.

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. `railway_requirements.txt` 파일이 최신인지 확인
2. Railway 대시보드에서 로그 확인
3. 환경변수 설정 확인 