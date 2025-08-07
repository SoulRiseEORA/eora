@echo off
chcp 65001 > nul
echo 로컬 개발 환경 설정 스크립트

echo.
echo 기존에 이미 .env 파일이 있다면 백업합니다...
if exist .env (
    echo 기존 .env 파일을 .env.backup으로 백업합니다.
    copy .env .env.backup
)

echo.
echo .env 파일을 생성합니다...

(
echo # 로컬 개발 환경 설정
echo ENVIRONMENT=development
echo.
echo # OpenAI API 설정
echo # 아래 YOUR_API_KEY 부분을 실제 OpenAI API 키로 교체하세요
echo OPENAI_API_KEY=YOUR_API_KEY
echo.
echo # GPT 모델 설정
echo OPENAI_MODEL=gpt-4o
echo GPT_MODEL=gpt-4o
echo MAX_TOKENS=2048
echo TEMPERATURE=0.7
echo.
echo # MongoDB 설정 ^(로컬^)
echo MONGODB_URL=mongodb://localhost:27017
echo DATABASE_NAME=aura_memory
echo.
echo # Redis 설정 ^(로컬^)
echo REDIS_URL=redis://localhost:6379
echo.
echo # JWT 설정
echo JWT_SECRET=your-secret-key-here
echo.
echo # 서버 설정
echo PORT=8001
echo HOST=127.0.0.1
echo.
echo # 세션 설정
echo SESSION_SECRET_KEY=your-session-secret-key-here
echo.
echo # Railway 환경 변수 ^(로컬에서는 사용 안함^)
echo RAILWAY_ENVIRONMENT=
) > .env

echo.
echo ✅ .env 파일이 생성되었습니다!
echo.
echo ⚠️  중요: .env 파일을 열어서 다음을 수정하세요:
echo    1. OPENAI_API_KEY=YOUR_API_KEY 부분에 실제 OpenAI API 키를 입력하세요.
echo    2. 다른 설정값도 필요에 따라 수정하세요.
echo.
echo 📝 .env 파일을 메모장으로 열기:
notepad .env
echo.
pause 