# EORA AI System - 빠른 시작 가이드

## 🚀 로컬 서버 실행 방법

### 방법 1: PowerShell 사용 (권장)
```powershell
# PowerShell을 관리자 권한으로 실행 후
.\start_app.ps1
```

### 방법 2: Windows 배치 파일 사용
```cmd
start_app.bat
```

### 방법 3: 직접 명령어 실행
```bash
# 프로젝트 루트 디렉토리(E:\eora_new)에서 실행
python -m uvicorn src.app:app --host 127.0.0.1 --port 8001 --reload
```

### 방법 4: src 디렉토리에서 실행
```bash
cd src
python -m uvicorn app:app --host 127.0.0.1 --port 8001 --reload
```

## ⚠️ 주의사항

1. **PowerShell에서 `&&` 오류가 발생하는 경우**
   - PowerShell에서는 `&&` 대신 `;` 또는 별도 명령어로 실행
   ```powershell
   cd src; python -m uvicorn app:app --host 127.0.0.1 --port 8001 --reload
   ```

2. **"Could not import module app" 오류가 발생하는 경우**
   - 프로젝트 루트에서: `python -m uvicorn src.app:app`
   - src 디렉토리에서: `python -m uvicorn app:app`

3. **포트가 이미 사용 중인 경우**
   - 다른 포트 사용: `--port 8002`
   - 스크립트는 자동으로 8002, 8003, 8004, 8005 시도

## 🔧 환경 설정

1. **필수 패키지 설치**
   ```bash
   cd src
   pip install -r requirements.txt
   ```

2. **환경변수 설정**
   - `src/.env` 파일 생성
   ```env
   OPENAI_API_KEY=your_api_key_here
   MONGODB_URI=mongodb://localhost:27017
   ```

## ✅ 서버 확인

서버가 정상적으로 실행되면:
- 브라우저에서 http://127.0.0.1:8001 접속
- Health Check: http://127.0.0.1:8001/health

## 🐛 문제 해결

### MongoDB Boolean Check 오류
- ✅ 이미 수정됨 (`if not db:` → `if db is None:`)

### Import 오류
- ✅ requirements.txt에 FastAPI, Uvicorn 추가됨

### PowerShell 실행 정책 오류
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📝 로그 확인

정상 실행 시 다음과 같은 로그가 표시됩니다:
```
🚀 EORA AI System 시작 중...
✅ MongoDB 연결 성공
✅ OpenAI API 키 설정 성공
INFO:     Uvicorn running on http://127.0.0.1:8001
INFO:     Application startup complete.
``` 