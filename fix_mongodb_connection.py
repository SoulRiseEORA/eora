#!/usr/bin/env python3
"""
Railway MongoDB 연결 자동 설정 및 테스트
"""

import os
import sys
from pymongo import MongoClient

def setup_railway_mongo_env():
    """Railway MongoDB 환경변수 자동 설정"""
    
    print("🔧 Railway MongoDB 환경변수 자동 설정 중...")
    
    # Railway MongoDB 연결 정보 (확인된 실제 값들)
    mongo_config = {
        "MONGO_INITDB_ROOT_PASSWORD": "HYxotmUHxMxbYAejsOxEnHwrgKpAochC",
        "MONGO_INITDB_ROOT_USERNAME": "mongo",
        "MONGO_PUBLIC_URL": "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594",
        "MONGO_URL": "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@mongodb.railway.internal:27017",
        "RAILWAY_TCP_PROXY_DOMAIN": "trolley.proxy.rlwy.net",
        "RAILWAY_TCP_PROXY_PORT": "26594",
        "RAILWAY_PRIVATE_DOMAIN": "mongodb.railway.internal"
    }
    
    # 환경변수 설정
    for key, value in mongo_config.items():
        os.environ[key] = value
        print(f"✅ {key}: {value[:10]}***" if "PASSWORD" in key else f"✅ {key}: {value}")
    
    print("✅ Railway MongoDB 환경변수 설정 완료")
    return mongo_config

def test_mongo_connection():
    """MongoDB 연결 테스트"""
    
    print("\n🔗 MongoDB 연결 테스트 시작...")
    
    # 연결 URL 우선순위
    connection_urls = [
        ("Railway 공개 URL", os.environ.get("MONGO_PUBLIC_URL")),
        ("Railway 내부 URL", os.environ.get("MONGO_URL")),
        ("기본 공개 URL", "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594")
    ]
    
    for name, url in connection_urls:
        if not url:
            continue
            
        try:
            print(f"🔗 {name} 연결 시도...")
            print(f"📝 URL: {url.replace('HYxotmUHxMxbYAejsOxEnHwrgKpAochC', '***')}")
            
            client = MongoClient(url, serverSelectionTimeoutMS=10000)
            client.admin.command('ping')
            
            # 데이터베이스 및 컬렉션 테스트
            db = client.eora_ai
            users_collection = db.users
            
            # 테스트 문서 삽입
            test_user = {
                "user_id": "test_connection_123",
                "email": "test@connection.com",
                "name": "연결 테스트",
                "created_at": "2024-01-01T00:00:00"
            }
            
            result = users_collection.insert_one(test_user)
            print(f"✅ 테스트 문서 삽입 성공: {result.inserted_id}")
            
            # 테스트 문서 삭제
            users_collection.delete_one({"user_id": "test_connection_123"})
            print("✅ 테스트 문서 삭제 완료")
            
            print(f"🎉 {name} 연결 성공!")
            client.close()
            return True, name, url
            
        except Exception as e:
            print(f"❌ {name} 연결 실패: {e}")
            print(f"🔍 오류 타입: {type(e).__name__}")
            continue
    
    print("❌ 모든 MongoDB 연결 시도 실패")
    return False, None, None

def main():
    """메인 함수"""
    print("🚀 Railway MongoDB 연결 자동 설정 및 테스트")
    print("=" * 60)
    
    # 환경변수 설정
    setup_railway_mongo_env()
    
    # MongoDB 연결 테스트
    success, connection_name, connection_url = test_mongo_connection()
    
    if success:
        print(f"\n🎉 MongoDB 연결 성공!")
        print(f"사용된 연결: {connection_name}")
        print(f"연결 URL: {connection_url.replace('HYxotmUHxMxbYAejsOxEnHwrgKpAochC', '***')}")
        print("\n이제 final_server.py를 실행하면 MongoDB를 사용할 수 있습니다.")
        print("\n실행 방법:")
        print("python final_server.py")
        return True
    else:
        print(f"\n❌ MongoDB 연결에 실패했습니다.")
        print("다음을 확인해주세요:")
        print("1. Railway 프로젝트에서 MongoDB 서비스가 실행 중인지 확인")
        print("2. 네트워크 연결 상태 확인")
        print("3. 방화벽 설정 확인")
        return False

if __name__ == "__main__":
    main() 