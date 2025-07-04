#!/usr/bin/env python3
"""
Railway 환경변수 확인 스크립트
"""

import os

def check_railway_env():
    """Railway 환경변수 확인"""
    
    print("🔍 Railway 환경변수 확인")
    print("=" * 50)
    
    # Railway MongoDB 관련 환경변수
    env_vars = [
        "MONGO_INITDB_ROOT_PASSWORD",
        "MONGO_INITDB_ROOT_USERNAME", 
        "MONGO_PUBLIC_URL",
        "MONGO_URL",
        "MONGOHOST",
        "MONGOPASSWORD",
        "MONGOPORT",
        "MONGOUSER",
        "RAILWAY_TCP_PROXY_DOMAIN",
        "RAILWAY_TCP_PROXY_PORT",
        "RAILWAY_PRIVATE_DOMAIN"
    ]
    
    print("📋 환경변수 목록:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # 비밀번호는 마스킹 처리
            if "PASSWORD" in var:
                masked_value = value[:3] + "*" * (len(value) - 6) + value[-3:] if len(value) > 6 else "***"
                print(f"  {var}: {masked_value}")
            else:
                print(f"  {var}: {value}")
        else:
            print(f"  {var}: (설정되지 않음)")
    
    print("\n🔗 MongoDB 연결 URL 구성:")
    
    # MONGO_PUBLIC_URL 확인
    mongo_public_url = os.getenv("MONGO_PUBLIC_URL")
    if mongo_public_url:
        print(f"  MONGO_PUBLIC_URL: {mongo_public_url.replace('HYxotmUHxMxbYAejsOxEnHwrgKpAochC', '***')}")
    else:
        print("  MONGO_PUBLIC_URL: (설정되지 않음)")
    
    # MONGO_URL 확인
    mongo_url = os.getenv("MONGO_URL")
    if mongo_url:
        print(f"  MONGO_URL: {mongo_url.replace('HYxotmUHxMxbYAejsOxEnHwrgKpAochC', '***')}")
    else:
        print("  MONGO_URL: (설정되지 않음)")
    
    # 수동 구성 URL
    mongo_user = os.getenv("MONGOUSER", "mongo")
    mongo_password = os.getenv("MONGOPASSWORD", "HYxotmUHxMxbYAejsOxEnHwrgKpAochC")
    mongo_host = os.getenv("MONGOHOST", "localhost")
    mongo_port = os.getenv("MONGOPORT", "27017")
    
    manual_url = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}"
    print(f"  수동 구성 URL: {manual_url.replace(mongo_password, '***')}")
    
    print("\n📊 연결 우선순위:")
    print("  1. MONGO_PUBLIC_URL (로컬에서 접근 가능)")
    print("  2. MONGO_URL (Railway 내부에서만 접근 가능)")
    print("  3. 수동 구성 URL (기본값)")

if __name__ == "__main__":
    check_railway_env() 