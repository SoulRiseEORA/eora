#!/bin/bash

# Railway 배포용 시작 스크립트
echo "🚀 Railway 배포 시작 스크립트 실행 중..."

# 환경변수 확인
echo "🔍 환경변수 확인:"
echo "  PORT: ${PORT:-8080}"
echo "  OPENAI_API_KEY: ${OPENAI_API_KEY:+설정됨}"
echo "  MONGODB_URI: ${MONGODB_URI:+설정됨}"

# app.py 파일 존재 확인
if [ ! -f "app.py" ]; then
    echo "❌ app.py 파일이 존재하지 않습니다!"
    exit 1
fi

echo "✅ app.py 파일 확인 완료"

# 포트 설정 (기본값 8080)
PORT=${PORT:-8080}
HOST="0.0.0.0"

echo "📍 호스트: $HOST"
echo "🔌 포트: $PORT"

# uvicorn 서버 시작
echo "🚀 uvicorn 서버 시작..."
exec python -m uvicorn app:app --host $HOST --port $PORT --workers 1 