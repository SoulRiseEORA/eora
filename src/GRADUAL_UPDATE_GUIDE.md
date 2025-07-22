# 점진적 업데이트 가이드

## 🚨 코드 삭제로 인한 오류 방지 가이드

### 📋 현재 상황
- PowerShell `&&` 문법 오류 해결됨
- 포트 충돌 문제 해결됨 (8081로 변경)
- logger 미정의 오류 해결됨
- 백업 파일 생성 완료

### 🔧 안전한 코드 수정 방법

#### 1. 백업 생성 후 수정
```bash
# 수정 전 항상 백업
cp main.py main_backup_$(date +%Y%m%d_%H%M%S).py
```

#### 2. 점진적 테스트
```bash
# 각 단계마다 테스트
python check_server.py
python test_api.py
```

#### 3. 롤백 준비
```bash
# 문제 발생 시 즉시 복원
cp main_backup_*.py main.py
```

### 🚀 서버 실행 방법

#### PowerShell 스크립트 사용 (권장)
```powershell
.\start_server.ps1
```

#### 배치 파일 사용
```cmd
run_server.bat
```

#### 직접 실행
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8081 --reload
```

### 📊 상태 확인

#### 서버 상태 확인
```bash
python check_server.py
```

#### API 테스트
```bash
python test_api.py
```

### 🔄 점진적 업데이트 체크리스트

- [ ] 백업 파일 생성
- [ ] 작은 단위로 수정
- [ ] 각 단계마다 테스트
- [ ] 오류 발생 시 즉시 롤백
- [ ] 성공 시 다음 단계 진행

### ⚠️ 주의사항

1. **한 번에 많은 코드를 삭제하지 마세요**
2. **수정 전 항상 백업을 만드세요**
3. **각 단계마다 테스트하세요**
4. **오류 발생 시 즉시 이전 상태로 복원하세요**

### 🛠️ 문제 해결

#### PowerShell 오류
- `&&` 대신 `;` 사용
- 또는 PowerShell 스크립트 사용

#### 포트 충돌
- `check_server.py`로 사용 가능한 포트 확인
- 다른 포트 사용 (8081, 8082 등)

#### Import 오류
- `main_backup.py`에서 복원
- 의존성 패키지 재설치

### 📞 지원

문제 발생 시:
1. 백업 파일로 복원
2. `check_server.py` 실행
3. 오류 로그 확인
4. 점진적으로 다시 수정 