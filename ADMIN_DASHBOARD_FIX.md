# 관리자 대시보드 링크 문제 해결

## 문제
관리자 로그인 후 홈 페이지에서 관리자 대시보드 링크가 표시되지 않음

## 원인
1. 로그인 API 엔드포인트 불일치 (`/api/admin/login` vs `/api/login`)
2. 템플릿에서 관리자 권한 확인 조건 문제
3. 세션 정보가 제대로 전달되지 않음

## 해결 방법

### 1. ✅ 로그인 API 엔드포인트 수정 (완료)
- `/api/admin/login` → `/api/login`으로 변경
- 로그인 성공 후 홈페이지(`/`)로 리다이렉트

### 2. ✅ 템플릿 조건문 수정 (완료)
```jinja2
{% if user and (user.role == 'admin' or user.is_admin == True or user.is_admin or user.email == 'admin@eora.ai') %}
```

### 3. 로그인 테스트 방법
1. 서버 실행: `run_server_utf8.bat`
2. http://127.0.0.1:8001/login 접속
3. 관리자 계정으로 로그인:
   - Email: `admin@eora.ai`
   - Password: `admin123`
4. 로그인 성공 후 홈페이지로 이동
5. 상단에 "⚙️ 관리자 대시보드" 링크 확인

## 확인된 동작
- 로그인 시 세션에 사용자 정보 저장
- `is_admin: true` 속성 설정
- 홈페이지에서 관리자 권한 확인 후 대시보드 링크 표시

## 추가 디버깅 (필요시)
브라우저 개발자 도구 콘솔에서 확인:
```javascript
// localStorage에 저장된 사용자 정보 확인
console.log(JSON.parse(localStorage.getItem('user')));
```

## 주의사항
- 세션 미들웨어가 활성화되어 있어야 함
- MongoDB가 연결되어 있어야 사용자 정보 저장 가능 