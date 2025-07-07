#!/bin/bash

echo "========================================"
echo "EORA AI System 자동 배포 스크립트"
echo "========================================"

# 환경변수 설정
export OPENAI_API_KEY="sk-your-openai-api-key-here"
export MONGODB_URL="mongodb://your-mongodb-url"
export REDIS_URL="redis://your-redis-url"
export JWT_SECRET="your-jwt-secret-key"

# Git 상태 확인
echo "[1/5] Git 상태 확인 중..."
if ! command -v git &> /dev/null; then
    echo "Git이 설치되지 않았습니다."
    exit 1
fi

git status
if [ $? -ne 0 ]; then
    echo "Git이 초기화되지 않았습니다."
    exit 1
fi

# 변경사항 커밋
echo "[2/5] 변경사항 커밋 중..."
git add .
git commit -m "Auto deploy: $(date)"
if [ $? -ne 0 ]; then
    echo "커밋 실패. 변경사항이 없을 수 있습니다."
fi

# GitHub에 푸시
echo "[3/5] GitHub에 푸시 중..."
git push origin main
if [ $? -ne 0 ]; then
    echo "푸시 실패. GitHub 설정을 확인하세요."
    exit 1
fi

# 로컬 서버 시작 (선택사항)
echo "[4/5] 로컬 서버 시작 중..."
read -p "로컬 서버를 시작하시겠습니까? (y/n): " choice
if [[ $choice == "y" || $choice == "Y" ]]; then
    echo "서버 시작 중..."
    python -m uvicorn main:app --host 0.0.0.0 --port 8016
fi

echo "[5/5] 배포 완료!"
echo "GitHub Actions를 통해 자동 배포가 진행됩니다."
echo "https://github.com/yourusername/eora-ai-system/actions 에서 배포 상태를 확인하세요." 