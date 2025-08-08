#!/bin/bash
echo "🚀 Railway 안전 서버 시작"
echo "================================================="

# 환경변수 확인
echo "📍 포트: ${PORT:-8080}"
echo "🌍 환경: ${RAILWAY_ENVIRONMENT:-production}"

# Python 경로 확인
which python3 2>/dev/null && PYTHON_CMD="python3" || PYTHON_CMD="python"
echo "🐍 Python 명령어: $PYTHON_CMD"

# 작업 디렉토리 확인
echo "📁 작업 디렉토리: $(pwd)"
echo "📄 파일 목록:"
ls -la | head -10

echo "================================================="
echo "🚀 Railway 안전 서버 실행 중..."

# 안전한 서버 실행
exec $PYTHON_CMD app.py 