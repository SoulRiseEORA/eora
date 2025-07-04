#!/usr/bin/env python3
"""
Railway MongoDB 빠른 연결 테스트
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
    
    # Railway에서 제공한 실제 연결 정보
    mongo_root_user = "mongo"
    mongo_root_password = "HYxotmUHxMxbYAejsOxEnHwrgKpAochC"
    
    # 일반적인 Railway MongoDB 연결 패턴들
    test_urls = [
        # 1. 일반적인 Railway MongoDB 공개 URL 패턴
        f"mongodb://{mongo_root_user}:{mongo_root_password}@trolley.proxy.rlwy.net:26594",
        f"mongodb://{mongo_root_user}:{mongo_root_password}@trolley.proxy.rlwy.net:27017",
        f"mongodb://{mongo_root_user}:{mongo_root_password}@trolley.proxy.rlwy.net:8080",
        
        # 2. 다른 일반적인 도메인 패턴들
        f"mongodb://{mongo_root_user}:{mongo_root_password}@mongo.proxy.rlwy.net:27017",
        f"mongodb://{mongo_root_user}:{mongo_root_password}@db.proxy.rlwy.net:27017",
        
        # 3. 내부 네트워크 URL (Railway 내부에서만 작동)
        f"mongodb://{mongo_root_user}:{mongo_root_password}@mongodb.railway.internal:27017",
        f"mongodb://{mongo_root_user}:{mongo_root_password}@mongo.railway.internal:27017",
        
        # 4. 로컬 테스트
        f"mongodb://{mongo_root_user}:{mongo_root_password}@localhost:27017"
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}. 연결 테스트:")
        print(f"   URL: {url.replace(mongo_root_password, '***')}")
        
        try:
            # MongoDB 클라이언트 생성
            client = MongoClient(url, serverSelectionTimeoutMS=10000)
            
            # 연결 테스트
            client.admin.command('ping')
            print(f"   ✅ 연결 성공!")
            
            # 데이터베이스 및 컬렉션 생성 테스트
            db = client.eora_ai
            users_collection = db.users
            
            # 컬렉션 목록 확인
            collections = db.list_collection_names()
            print(f"   📋 현재 컬렉션 목록: {collections}")
            
            # 테스트 문서 삽입
            test_user = {
                "user_id": "test_user_123",
                "email": "test@example.com",
                "name": "테스트 사용자",
                "created_at": "2024-01-01T00:00:00"
            }
            
            result = users_collection.insert_one(test_user)
            print(f"   ✅ 테스트 사용자 생성 성공: {result.inserted_id}")
            
            # 테스트 문서 삭제
            users_collection.delete_one({"user_id": "test_user_123"})
            print(f"   ✅ 테스트 사용자 삭제 완료")
            
            # 최종 컬렉션 목록 확인
            final_collections = db.list_collection_names()
            print(f"   📋 최종 컬렉션 목록: {final_collections}")
            
            client.close()
            return True, url
            
        except Exception as e:
            print(f"   ❌ 연결 실패: {type(e).__name__}")
            if "Authentication failed" in str(e):
                print(f"   🔍 인증 실패 - 사용자명/비밀번호 확인 필요")
            elif "getaddrinfo failed" in str(e):
                print(f"   🔍 호스트 주소를 찾을 수 없음")
            elif "timeout" in str(e).lower():
                print(f"   🔍 연결 시간 초과")
    
    return False, None

def main():
    """메인 함수"""
    print("🚀 Railway MongoDB 빠른 연결 테스트")
    print("=" * 50)
    
    success, working_url = test_railway_mongo()
    
    if success:
        print(f"\n🎉 Railway MongoDB 연결이 성공했습니다!")
        print(f"작동하는 URL: {working_url.replace('HYxotmUHxMxbYAejsOxEnHwrgKpAochC', '***')}")
        print("\n이제 final_server.py를 실행하면 MongoDB를 사용할 수 있습니다.")
        print("\n실행 방법:")
        print("python final_server.py")
    else:
        print(f"\n❌ 모든 Railway MongoDB 연결 시도가 실패했습니다.")
        print("\n📋 다음 단계:")
        print("1. Railway 대시보드에서 MongoDB 서비스 상태 확인")
        print("2. Railway 대시보드에서 RAILWAY_TCP_PROXY_DOMAIN 확인")
        print("3. Railway 대시보드에서 RAILWAY_TCP_PROXY_PORT 확인")
        print("4. 실제 값들을 알려주시면 정확한 연결을 설정해드리겠습니다")

if __name__ == "__main__":
    main() 