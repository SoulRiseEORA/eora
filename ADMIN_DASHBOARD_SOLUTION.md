# 관리자 대시보드 문제 해결

## 문제 요약
- 관리자 로그인 후 관리자 페이지(/admin)에 접근할 수 없는 문제
- 관리자 권한 확인 로직이 제대로 작동하지 않음
- 홈페이지에서 관리자 대시보드 링크가 표시되지 않음
- "로그인 중 오류가 발생했습니다" 메시지 표시

## 해결 방법

### 1. 관리자 계정 직접 처리 추가
`app_modular.py` 파일의 로그인 처리 함수에 관리자 계정을 직접 처리하는 코드를 추가했습니다.

```python
@app.post("/api/auth/login")
async def login_user(request: Request):
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        
        # 관리자 계정 하드코딩 처리 (보안을 위해 실제 서비스에서는 환경 변수로 관리 권장)
        if email == "admin@eora.ai" and password == "admin":
            # 관리자 계정 직접 처리
            user_info = {
                "email": email,
                "name": "관리자",
                "role": "admin",
                "is_admin": True,
                "user_id": email
            }
            access_token = str(uuid.uuid4())
            response = JSONResponse({
                "success": True,
                "user": user_info,
                "access_token": access_token
            })
            response.set_cookie("user", json.dumps(user_info))
            response.set_cookie("user_email", email)
            response.set_cookie("is_admin", "true")
            response.set_cookie("role", "admin")
            response.set_cookie("access_token", access_token)
            return response
```

### 2. 사용자 정보 조회 함수 개선
`get_current_user` 함수를 수정하여 여러 방법으로 관리자 여부를 확인하도록 했습니다.

```python
def get_current_user(request: Request):
    user = None
    session_user = None
    
    # 1. 세션에서 user 정보 시도 (세션 미들웨어가 있을 때만)
    if SESSION_MIDDLEWARE_AVAILABLE:
        try:
            if hasattr(request, 'session'):
                try:
                    session_user = request.session.get('user')
                    if session_user:
                        logger.info(f"✅ 세션에서 user 조회 성공: {session_user.get('email', 'unknown')}")
                except Exception as e:
                    logger.warning(f"⚠️ 세션 읽기 오류: {e}")
                    session_user = None
        except Exception as e:
            logger.warning(f"⚠️ 세션 접근 오류: {e}")
            session_user = None
    
    if session_user:
        user = session_user
    else:
        # 2. 쿠키에서 user 정보 시도
        try:
            user_cookie = request.cookies.get('user')
            if user_cookie:
                user = json.loads(user_cookie)
                logger.info(f"✅ 쿠키에서 user 조회 성공: {user.get('email', 'unknown')}")
        except Exception as e:
            logger.warning(f"⚠️ 쿠키 파싱 오류: {e}")
            user = None
        
        # 3. 개별 쿠키에서 정보 조합
        if not user:
            user_email = request.cookies.get('user_email')
            if user_email:
                user = {"email": user_email}
                logger.info(f"✅ 개별 쿠키에서 user 조회 성공: {user_email}")
    
    # 4. user 정보 보정 (관리자 판별 포함)
    if user:
        user['email'] = user.get('email', '')
        user['user_id'] = user.get('user_id') or user.get('email') or 'anonymous'
        
        # 관리자 여부 확인 (여러 방법으로 확인)
        is_admin = (
            user.get('email') == 'admin@eora.ai' or
            user.get('is_admin') == True or
            user.get('is_admin') == 'true' or
            user.get('role') == 'admin'
        )
        
        user['role'] = 'admin' if is_admin else user.get('role', 'user')
        user['is_admin'] = is_admin
        
        # 필수 필드 보정
        if 'name' not in user:
            user['name'] = user['email'].split('@')[0] if '@' in user['email'] else 'User'
    else:
        logger.warning("⚠️ 모든 방법으로 user 정보 조회 실패")
    
    return user
```

### 3. 관리자 페이지 라우트 수정
관리자 페이지 라우트에 `admin_required` 데코레이터를 적용하여 관리자만 접근할 수 있도록 했습니다.

```python
@app.get("/admin", response_class=HTMLResponse)
@admin_required
async def admin_page(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("admin.html", {"request": request, "user": user})
```

### 4. 홈페이지 로그인 처리 개선
`home.html` 파일의 로그인 처리 함수를 수정하여 API 경로를 `/api/auth/login`으로 변경하고 관리자 여부 확인 로직을 개선했습니다.

```javascript
fetch('/api/auth/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        email: email,
        password: password
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        // 로그인 성공 시 사용자 정보 저장
        localStorage.setItem('user_email', email);
        
        // 관리자 여부 확인 및 저장
        const isAdmin = (email === 'admin@eora.ai' || 
                       (data.user && (data.user.is_admin === true || data.user.role === 'admin')));
        
        localStorage.setItem('is_admin', isAdmin);
        
        // 관리자인 경우 관리자 페이지로, 아니면 채팅 페이지로 이동
        if (isAdmin) {
            window.location.href = '/admin';
        } else {
            window.location.href = '/chat';
        }
    }
})
```

### 5. 홈페이지 관리자 대시보드 링크 조건 수정
`home.html` 파일의 관리자 대시보드 링크 표시 조건을 단순화했습니다.

```html
{% if user and user.is_admin %}
<a href="/admin" class="admin-btn" id="adminBtn"
    style="margin-left:12px;display:inline-flex;align-items:center;gap:6px;text-decoration:none;">
    <span>⚙️</span> 관리자 대시보드
</a>
{% endif %}
```

### 6. 환경 변수 설정
서버 시작 스크립트에 필요한 환경 변수를 설정했습니다.

```batch
REM 환경 변수 설정 (배치 파일)
set OPENAI_API_KEY=your_openai_api_key_here
set DATABASE_NAME=eora_ai
set PORT=8010
```

```powershell
# 환경 변수 설정 (PowerShell)
$env:OPENAI_API_KEY = "your_openai_api_key_here"
$env:DATABASE_NAME = "eora_ai"
$env:PORT = 8010
```

## 테스트 방법
1. 서버 시작: `start_app_modular.bat` 또는 `powershell -ExecutionPolicy Bypass -File start_app_modular.ps1`
2. 브라우저에서 `http://127.0.0.1:8010/login` 접속
3. 관리자 계정으로 로그인 (이메일: admin@eora.ai, 비밀번호: admin)
4. 로그인 성공 후 관리자 대시보드로 자동 이동
5. 홈페이지에서도 관리자 대시보드 링크가 표시되는지 확인

## 관리자 계정 정보
- 이메일: admin@eora.ai
- 비밀번호: admin

## 추가 개선 사항
1. 관리자 계정 정보를 환경 변수로 관리하여 보안 강화
2. 비밀번호 해싱 적용하여 보안 강화
3. JWT 기반 인증 시스템 도입 고려
4. 관리자 권한 레벨 세분화 (슈퍼 관리자, 일반 관리자 등) 