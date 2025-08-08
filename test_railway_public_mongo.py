#!/usr/bin/env python3
"""
Railway MongoDB 공개 URL 연결 테스트 (로컬에서 실행)
"""

import os

try:
    from pymongo import MongoClient
    print("✅ PyMongo 라이브러리 로드 성공")
except ImportError:
    print("❌ PyMongo 라이브러리가 설치되지 않았습니다.")
    print("설치 방법: pip install pymongo")
    exit(1)

def test_railway_public_mongo():
    """Railway MongoDB 공개 URL 연결 테스트"""
    
    print("🔗 Railway MongoDB 공개 URL 연결 테스트")
    print("=" * 50)
    
    # Railway MongoDB 공개 URL (로컬에서 접근 가능)
    mongo_public_url = "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594"
    
    print(f"📝 연결 URL: {mongo_public_url.replace('HYxotmUHxMxbYAejsOxEnHwrgKpAochC', '***')}")
    print(f"🔍 도메인: trolley.proxy.rlwy.net")
    print(f"🔍 포트: 26594")
    print(f"📍 목적: 로컬에서 Railway MongoDB 연결 테스트")
    
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
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")
        print(f"🔍 상세 오류: {type(e).__name__}")
        
        # 오류별 해결 방법 제시
        if "Authentication failed" in str(e):
            print("\n🔧 해결 방법:")
            print("1. Railway 대시보드에서 MongoDB 인증 정보 확인")
            print("2. MongoDB 서비스가 실행 중인지 확인")
        elif "getaddrinfo failed" in str(e):
            print("\n🔧 해결 방법:")
            print("1. Railway 대시보드에서 공개 URL 확인")
            print("2. 네트워크 연결 상태 확인")
        elif "timeout" in str(e).lower():
            print("\n🔧 해결 방법:")
            print("1. Railway MongoDB 서비스가 실행 중인지 확인")
            print("2. 공개 URL이 올바른지 확인")
        
        return False

def main():
    """메인 함수"""
    print("🚀 Railway MongoDB 공개 URL 연결 테스트")
    print("=" * 50)
    print("📍 목적: 로컬에서 Railway MongoDB 연결 확인")
    print("💡 참고: 이 테스트가 성공하면 로컬에서 Railway MongoDB 사용 가능")
    print()
    
    success = test_railway_public_mongo()
    
    if success:
        print("\n🎉 Railway MongoDB 공개 URL 연결이 성공했습니다!")
        print("이제 로컬에서 Railway MongoDB를 사용할 수 있습니다.")
        print("\n다음 단계:")
        print("1. run_server_with_railway_mongo.bat 실행")
        print("2. 또는 python final_server.py 실행")
        print("3. 서버가 Railway MongoDB를 사용하는지 확인")
    else:
        print("\n❌ Railway MongoDB 공개 URL 연결에 실패했습니다.")
        print("\n📋 다음 단계:")
        print("1. Railway 대시보드에서 MongoDB 서비스 상태 확인")
        print("2. 공개 URL이 올바른지 확인")
        print("3. GitHub 배포 후 Railway에서 실행하는 것을 권장")

if __name__ == "__main__":
    main() 