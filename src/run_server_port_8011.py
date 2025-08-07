#!/usr/bin/env python3
"""
포트 8011로 EORA AI 서버 실행
"""

import os
import uvicorn

# Railway MongoDB 환경변수 설정
os.environ["MONGO_INITDB_ROOT_PASSWORD"] = "HYxotmUHxMxbYAejsOxEnHwrgKpAochC"
os.environ["MONGO_INITDB_ROOT_USERNAME"] = "mongo"
os.environ["MONGO_PUBLIC_URL"] = "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594"
os.environ["RAILWAY_TCP_PROXY_DOMAIN"] = "trolley.proxy.rlwy.net"
os.environ["RAILWAY_TCP_PROXY_PORT"] = "26594"
os.environ["RAILWAY_PRIVATE_DOMAIN"] = "mongodb.railway.internal"

print("🚀 EORA AI 서버 시작 (포트 8011)")
print("=" * 50)
print("🔧 Railway MongoDB 환경변수 설정 완료")
print("📍 서버 주소: http://localhost:8011")
print("🔐 관리자 계정: admin@eora.ai / admin1234")
print("=" * 50)

if __name__ == "__main__":
    uvicorn.run(
        "final_server:app",
        host="127.0.0.1",
        port=8011,
        reload=False
    ) 