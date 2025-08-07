# 🔑 OpenAI API 로컬 설정 가이드

## 현재 상황
- Railway 환경에서는 OpenAI API가 정상 작동
- 로컬 서버에서 OpenAI API 키 인식 안 됨
- 로그: `Incorrect API key provided`

## 해결 방법

### 1. .env 파일 생성/수정

#### 자동 설정 (권장)
```batch
setup_local_env.bat
```
실행 후 메모장이 열리면 `YOUR_API_KEY`를 실제 API 키로 교체

#### 수동 설정
1. 프로젝트 루트(`E:\eora_new`)에 `.env` 파일 생성
2. 다음 내용 추가:
```env
OPENAI_API_KEY=sk-proj-실제API키입력
```

### 2. API 키 확인 방법
```batch
test_api_key.py
```

### 3. 서버 실행
```batch
run_server_utf8.bat
```

## 문제 해결

### 여전히 API 키 오류가 발생하는 경우

1. **환경 변수 직접 설정**
   ```batch
   set OPENAI_API_KEY=sk-proj-실제API키
   python -m uvicorn src.app:app --host 127.0.0.1 --port 8001
   ```

2. **src 폴더에도 .env 복사**
   ```batch
   copy .env src\.env
   ```

3. **Python에서 직접 확인**
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   print(os.getenv('OPENAI_API_KEY'))
   ```

## OpenAI API 키 얻는 방법

1. https://platform.openai.com/account/api-keys 접속
2. "Create new secret key" 클릭
3. 생성된 키를 복사 (sk-proj-로 시작)
4. `.env` 파일에 붙여넣기

## 주의사항

- `.env` 파일은 절대 Git에 커밋하지 마세요
- API 키는 안전하게 보관하세요
- 키가 노출되면 즉시 재생성하세요

## 확인 사항

✅ `.env` 파일이 프로젝트 루트에 있는지 확인
✅ API 키가 `sk-proj-`로 시작하는지 확인
✅ 따옴표 없이 키만 입력했는지 확인
✅ 파일 인코딩이 UTF-8인지 확인 