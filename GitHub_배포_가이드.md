# 🚀 EORA AI GitHub 전체 배포 가이드

## 📋 개요

모든 Python 파일과 프로젝트 파일들을 GitHub에 한번에 배포하는 완전 자동화된 스크립트입니다.

## 🎯 제공되는 배포 스크립트

### 1. Windows 배치 파일 (권장)
```bash
deploy_all_to_github.bat
```
- Windows 명령 프롬프트(CMD)에서 실행
- 한글 지원 완벽
- 단계별 안내 제공

### 2. PowerShell 스크립트
```powershell
deploy_all_to_github.ps1
```
- PowerShell에서 실행
- 고급 기능 및 매개변수 지원
- 컬러 출력 지원

## 🚀 빠른 시작

### 방법 1: 배치 파일 사용 (추천)

1. **파일 실행**
   ```bash
   deploy_all_to_github.bat
   ```

2. **안내에 따라 진행**
   - Git 사용자 설정 (필요시)
   - GitHub 저장소 URL 입력
   - 커밋 메시지 입력 (선택사항)
   - 푸시 확인

### 방법 2: PowerShell 사용

1. **PowerShell 관리자 권한으로 실행**

2. **실행 정책 설정** (최초 1회)
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **스크립트 실행**
   ```powershell
   .\deploy_all_to_github.ps1
   ```

4. **매개변수와 함께 실행** (고급)
   ```powershell
   .\deploy_all_to_github.ps1 -CommitMessage "새로운 기능 추가" -GitHubUrl "https://github.com/username/repo.git" -Force
   ```

### 방법 3: 수동 배포

PowerShell이나 Git Bash에서:

```bash
# 1. Git 초기화
git init

# 2. 모든 파일 추가
git add .

# 3. 커밋 생성
git commit -m "회원가입 시스템 수정 완료 - Railway 환경 최적화"

# 4. 원격 저장소 추가
git remote add origin https://github.com/username/repository-name.git

# 5. 푸시
git push -u origin main --force
```

## 📁 배포되는 파일들

### Python 파일
- ✅ `src/app.py` (메인 서버 파일)
- ✅ `app.py` (루트 서버 파일)
- ✅ 모든 모듈 파일들 (`src/` 하위)
- ✅ 테스트 파일들

### 설정 파일
- ✅ `Dockerfile` (Railway 배포용)
- ✅ `requirements.txt` (Python 의존성)
- ✅ `Procfile` (Railway 실행 설정)
- ✅ `nixpacks.toml` (Nixpacks 설정)

### 데이터 파일
- ✅ `data/` 폴더 (사용자, 세션, 메시지 데이터)
- ✅ 설정 JSON 파일들

### 웹 파일
- ✅ `src/templates/` (HTML 템플릿)
- ✅ `src/static/` (CSS, JS, 이미지)

### 제외되는 파일
- ❌ `.env` (환경변수 파일)
- ❌ `__pycache__/` (Python 캐시)
- ❌ `*.log` (로그 파일)
- ❌ 임시 파일들

## 🔧 사전 준비사항

### 1. Git 설치
- **Windows**: https://git-scm.com/download/win
- **macOS**: `brew install git`
- **Linux**: `sudo apt install git`

### 2. GitHub 계정
- GitHub 계정 생성: https://github.com
- 저장소 생성 (Public 또는 Private)

### 3. Git 사용자 설정 (최초 1회)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## 🎯 Railway 연동

### 자동 배포 설정

1. **Railway 계정 생성**
   - https://railway.app 방문
   - GitHub으로 로그인

2. **프로젝트 생성**
   - "New Project" 클릭
   - "Deploy from GitHub repo" 선택
   - 배포한 저장소 선택

3. **환경변수 설정**
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   OPENAI_API_KEY_1=sk-backup-key-1
   OPENAI_API_KEY_2=sk-backup-key-2
   # ... 기타 필요한 환경변수
   ```

4. **자동 배포 확인**
   - GitHub에 푸시할 때마다 자동 배포
   - Railway 대시보드에서 배포 로그 확인

## 📊 배포 후 확인사항

### 1. GitHub 저장소 확인
- [ ] 모든 파일이 정상 업로드되었는지 확인
- [ ] 커밋 히스토리 확인
- [ ] README.md 파일 확인

### 2. Railway 배포 확인
- [ ] 자동 배포가 트리거되었는지 확인
- [ ] 배포 로그에서 오류가 없는지 확인
- [ ] 서비스 URL 접속 테스트

### 3. 기능 테스트
- [ ] 회원가입 시스템 테스트
- [ ] AI 채팅 기능 테스트
- [ ] 세션 저장 기능 테스트
- [ ] 포인트 시스템 테스트

## 🆘 문제 해결

### Git 오류
```bash
# 원격 저장소 변경
git remote set-url origin https://github.com/new-username/new-repo.git

# 강제 푸시
git push origin main --force

# 브랜치 이름 변경
git branch -M main
```

### GitHub 인증 오류
```bash
# Personal Access Token 사용
git config credential.helper store
# GitHub에서 PAT 생성 후 비밀번호 대신 사용
```

### PowerShell 실행 정책 오류
```powershell
# 실행 정책 변경
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# 또는 일회성 실행
powershell -ExecutionPolicy Bypass -File .\deploy_all_to_github.ps1
```

## 💡 팁과 권장사항

### 배포 전 체크리스트
- [ ] 중요한 변경사항이 모두 포함되었는지 확인
- [ ] 환경변수 파일(.env)이 제외되었는지 확인
- [ ] 테스트가 모두 통과했는지 확인
- [ ] 커밋 메시지가 명확한지 확인

### 정기 배포 권장
- 새로운 기능 추가 시
- 버그 수정 시
- 설정 변경 시
- 주기적인 백업 목적

### 버전 관리
```bash
# 태그를 사용한 버전 관리
git tag -a v1.0.0 -m "회원가입 시스템 완료"
git push origin v1.0.0
```

---

## 🚀 지금 바로 시작하기

```bash
# 간단하게 시작하려면:
deploy_all_to_github.bat

# 고급 사용자라면:
.\deploy_all_to_github.ps1 -Force
```

모든 과정이 자동화되어 있으므로 안내에 따라 진행하시면 됩니다! 🎉