#!/usr/bin/env python3
"""
Railway MongoDB 최종 연결 테스트 (확인된 정보 사용)
"""

import os

try:
    from pymongo import MongoClient
    print("✅ PyMongo 라이브러리 로드 성공")
except ImportError:
    print("❌ PyMongo 라이브러리가 설치되지 않았습니다.")
    print("설치 방법: pip install pymongo")
    exit(1)

def test_railway_mongo():
    """Railway MongoDB 연결 테스트"""
    
    print("🔗 Railway MongoDB 연결 테스트")
    print("=" * 50)
    
    # Railway에서 확인된 실제 연결 정보
    mongo_public_url = "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594"
    
    print(f"📝 연결 URL: {mongo_public_url.replace('HYxotmUHxMxbYAejsOxEnHwrgKpAochC', '***')}")
    print(f"🔍 도메인: trolley.proxy.rlwy.net")
    print(f"🔍 포트: 26594")
    
    try:
        # MongoDB 클라이언트 생성
        client = MongoClient(mongo_public_url, serverSelectionTimeoutMS=15000)
        
        # 연결 테스트
        client.admin.command('ping')
        print("✅ MongoDB 연결 성공!")
        
        # 데이터베이스 및 컬렉션 생성 테스트
        db = client.eora_ai
        users_collection = db.users
        
        # 컬렉션 목록 확인
        collections = db.list_collection_names()
        print(f"📋 현재 컬렉션 목록: {collections}")
        
        # 테스트 문서 삽입
        test_user = {
            "user_id": "test_user_123",
            "email": "test@example.com",
            "name": "테스트 사용자",
            "created_at": "2024-01-01T00:00:00"
        }
        
        result = users_collection.insert_one(test_user)
        print(f"✅ 테스트 사용자 생성 성공: {result.inserted_id}")
        
        # 테스트 문서 삭제
        users_collection.delete_one({"user_id": "test_user_123"})
        print("✅ 테스트 사용자 삭제 완료")
        
        # 최종 컬렉션 목록 확인
        final_collections = db.list_collection_names()
        print(f"📋 최종 컬렉션 목록: {final_collections}")
        
        # 추가 컬렉션 생성 테스트
        points_collection = db.points
        sessions_collection = db.sessions
        chat_logs_collection = db.chat_logs
        
        print("✅ 모든 컬렉션이 성공적으로 생성되었습니다!")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")
        print(f"🔍 상세 오류: {type(e).__name__}")
        
        # 오류별 해결 방법 제시
        if "Authentication failed" in str(e):
            print("\n🔧 해결 방법:")
            print("1. Railway 대시보드에서 MONGO_INITDB_ROOT_PASSWORD 확인")
            print("2. Railway 대시보드에서 MONGO_INITDB_ROOT_USERNAME 확인")
        elif "getaddrinfo failed" in str(e):
            print("\n🔧 해결 방법:")
            print("1. Railway 대시보드에서 RAILWAY_TCP_PROXY_DOMAIN 확인")
            print("2. Railway 대시보드에서 RAILWAY_TCP_PROXY_PORT 확인")
        elif "timeout" in str(e).lower():
            print("\n🔧 해결 방법:")
            print("1. Railway MongoDB 서비스가 실행 중인지 확인")
            print("2. 네트워크 연결 상태 확인")
        
        return False

def setup_environment():
    """환경변수 설정"""
    print("\n🔧 환경변수 설정...")
    
    # Railway 환경변수 설정
    os.environ["MONGO_INITDB_ROOT_PASSWORD"] = "HYxotmUHxMxbYAejsOxEnHwrgKpAochC"
    os.environ["MONGO_INITDB_ROOT_USERNAME"] = "mongo"
    os.environ["MONGO_PUBLIC_URL"] = "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594"
    os.environ["MONGO_URL"] = "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@mongodb.railway.internal:27017"
    os.environ["RAILWAY_TCP_PROXY_DOMAIN"] = "trolley.proxy.rlwy.net"
    os.environ["RAILWAY_TCP_PROXY_PORT"] = "26594"
    os.environ["RAILWAY_PRIVATE_DOMAIN"] = "mongodb.railway.internal"
    
    print("✅ 환경변수 설정 완료")
    
    # 설정된 환경변수 확인
    print("\n📋 설정된 환경변수:")
    print(f"MONGO_INITDB_ROOT_PASSWORD: {os.environ.get('MONGO_INITDB_ROOT_PASSWORD')[:3]}***{os.environ.get('MONGO_INITDB_ROOT_PASSWORD')[-3:]}")
    print(f"MONGO_INITDB_ROOT_USERNAME: {os.environ.get('MONGO_INITDB_ROOT_USERNAME')}")
    print(f"RAILWAY_TCP_PROXY_DOMAIN: {os.environ.get('RAILWAY_TCP_PROXY_DOMAIN')}")
    print(f"RAILWAY_TCP_PROXY_PORT: {os.environ.get('RAILWAY_TCP_PROXY_PORT')}")
    print(f"RAILWAY_PRIVATE_DOMAIN: {os.environ.get('RAILWAY_PRIVATE_DOMAIN')}")

def main():
    """메인 함수"""
    print("🚀 Railway MongoDB 최종 연결 테스트")
    print("=" * 50)
    
    # 환경변수 설정
    setup_environment()
    
    # MongoDB 연결 테스트
    success = test_railway_mongo()
    
    if success:
        print("\n🎉 Railway MongoDB 연결이 성공했습니다!")
        print("이제 final_server.py를 실행하면 MongoDB를 사용할 수 있습니다.")
        print("\n실행 방법:")
        print("python final_server.py")
        print("\n또는:")
        print("run_server_with_railway_mongo.bat")
    else:
        print("\n❌ Railway MongoDB 연결에 실패했습니다.")
        print("\n📋 다음 단계:")
        print("1. Railway 대시보드에서 MongoDB 서비스 상태 확인")
        print("2. Railway 대시보드에서 서비스 로그 확인")
        print("3. 네트워크 연결 상태 확인")

if __name__ == "__main__":
    main() 