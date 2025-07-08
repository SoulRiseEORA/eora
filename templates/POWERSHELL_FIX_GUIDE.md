# PowerShell 환경 문제 해결 가이드

## 🔧 문제 상황
PowerShell 환경에서 다음과 같은 문제들이 발생했습니다:
- 터미널 명령 실행 실패
- 포트 충돌 문제 (8005 포트 사용 중)
- Git 명령 실행 문제

## 🛠️ 해결 방법

### 1. PowerShell 실행 정책 수정
```powershell
# 관리자 권한으로 PowerShell 실행 후
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. 자동 수정 스크립트 실행
```powershell
# fix_powershell.ps1 실행
.\fix_powershell.ps1
```

### 3. 수동 해결 방법

#### 포트 충돌 해결
```powershell
# 포트 8005 사용 중인 프로세스 확인
netstat -ano | findstr :8005

# 프로세스 종료 (PID는 위 명령으로 확인)
taskkill /PID [프로세스ID] /F
```

#### 서버 시작
```powershell
# 포트 8005로 시작
python main.py --port 8005

# 또는 다른 포트로 시작
python main.py --port 8006
```

### 4. Git 배포
```powershell
# 배치 파일 실행
deploy_git.bat

# 또는 수동 실행
cd E:\AI_Dev_Tool\src
git add .
git commit -m "Stable: EORA AI system deployment fixes and improvements"
git push
```

## 📁 생성된 파일들

1. **fix_powershell.ps1** - PowerShell 환경 자동 수정
2. **deploy_git.bat** - Git 배포 자동화
3. **start_server_simple.bat** - 간단한 서버 시작

## ✅ 확인 사항

- [ ] PowerShell 실행 정책이 RemoteSigned로 설정됨
- [ ] 포트 8005가 사용 가능함
- [ ] Python 프로세스가 정상적으로 시작됨
- [ ] Git 명령이 정상 실행됨

## 🚀 다음 단계

1. `fix_powershell.ps1` 실행
2. `start_server_simple.bat` 실행
3. 서버가 정상 시작되면 `deploy_git.bat` 실행

## 📞 문제 지속 시

만약 문제가 지속되면:
1. 관리자 권한으로 PowerShell 실행
2. Windows 방화벽 설정 확인
3. Python 환경 변수 확인
4. Git 설치 상태 확인 