#!/bin/bash

echo "🚀 Railway 환경 변수 설정 스크립트"
echo "=================================="

# Railway CLI 설치 확인
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI가 설치되지 않았습니다."
    echo "설치 방법: npm install -g @railway/cli"
    exit 1
fi

echo "✅ Railway CLI 확인됨"

# 환경 변수 설정
echo "📝 환경 변수 설정 중..."

# MongoDB 연결 정보
railway variables set MONGODB_URL="mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594"

# 개별 MongoDB 변수
railway variables set MONGO_HOST="trolley.proxy.rlwy.net"
railway variables set MONGO_PORT="26594"
railway variables set MONGO_INITDB_ROOT_PASSWORD="HYxotmUHxMxbYAejsOxEnHwrgKpAochC"

# 포트 설정
railway variables set PORT="8080"

echo "✅ 환경 변수 설정 완료!"
echo ""
echo "📋 설정된 환경 변수:"
railway variables list

echo ""
echo "🔄 배포를 위해 다음 명령을 실행하세요:"
echo "railway up" 