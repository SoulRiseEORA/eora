# 🔧 OpenAI API 키 401 오류 해결 방법

## 🚨 현재 문제
```
Error code: 401 - 'Incorrect API key provided: sk-proj-...ZKYA'
```

## 🔍 원인 분석
1. **만료된 API 키**: 현재 사용 중인 키가 만료되었거나 삭제됨
2. **잘못된 키**: 키가 손상되었거나 부분적으로 복사됨
3. **권한 부족**: API 키의 사용 권한이 제한됨

## ✅ 해결 방법

### 🔑 1. 새로운 API 키 발급 (권장)

**OpenAI 플랫폼에서:**
1. https://platform.openai.com/api-keys 접속
2. 로그인 후 "Create new secret key" 클릭
3. 키 이름 입력 (예: "EORA-AI-KEY")
4. 새로 생성된 키 복사 (sk-proj-로 시작)

### 🛠️ 2. 로컬 환경에 API 키 설정

**방법 A: .env 파일 생성 (권장)**
```bash
# src/.env 파일 생성
OPENAI_API_KEY=sk-proj-새로운-유효한-키-여기에-입력
```

**방법 B: 시스템 환경변수 설정**
```cmd
# Windows CMD
set OPENAI_API_KEY=sk-proj-새로운-유효한-키-여기에-입력

# PowerShell  
$env:OPENAI_API_KEY="sk-proj-새로운-유효한-키-여기에-입력"
```

### 🚂 3. 레일웨이 환경에 API 키 설정

1. Railway Dashboard 접속
2. 프로젝트 선택 → Variables 탭
3. 다음 변수들 추가/수정:
```
OPENAI_API_KEY=sk-proj-새로운-유효한-키
OPENAI_API_KEY_1=sk-proj-백업-키-1
OPENAI_API_KEY_2=sk-proj-백업-키-2
```

## 🔄 4. 서버 재시작 및 확인

**서버 재시작:**
```bash
# 현재 서버 중지 (Ctrl+C)
# 새로 시작
cd src
python app.py
```

**성공 확인 메시지:**
```
✅ 유효한 API 키 발견: OPENAI_API_KEY = sk-proj-...
🔧 환경변수에 API 키 강제 설정 완료
```

## 🧪 5. 테스트 방법

**관리자 계정 테스트:**
1. http://127.0.0.1:8300 접속
2. admin@eora.ai / admin123 로그인
3. 채팅에서 "안녕하세요" 메시지 전송
4. AI 응답 확인

**일반 회원 테스트:**
1. 새 계정 가입
2. 채팅 테스트
3. 포인트 차감 확인

## ⚠️ 주의사항

1. **API 키 보안**: 
   - 절대 Git에 커밋하지 마세요
   - 사용하지 않는 키는 즉시 삭제하세요

2. **사용량 관리**:
   - OpenAI 대시보드에서 사용량 모니터링
   - 예상치 못한 요금 방지를 위해 사용 한도 설정

3. **백업 키 준비**:
   - 여러 개의 API 키 준비 권장
   - 메인 키 문제 시 자동 전환

## 🎯 예상 결과

API 키를 올바르게 설정하면:
- ✅ 관리자: 무제한 GPT 대화 가능
- ✅ 일반 회원: 포인트 차감으로 GPT 대화 가능  
- ✅ 레일웨이 환경변수 정상 인식
- ✅ 모든 사용자 유형에서 정상 작동