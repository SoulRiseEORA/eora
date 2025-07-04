#!/usr/bin/env python3
"""
Railway MongoDB 연결 테스트
"""

try:
    from pymongo import MongoClient
    print("✅ PyMongo 라이브러리 로드 성공")
except ImportError:
    print("❌ PyMongo 라이브러리가 설치되지 않았습니다.")
    print("설치 방법: pip install pymongo")
    exit(1)

def test_railway_mongo():
    """Railway MongoDB 연결 테스트"""
    
    # Railway MongoDB 연결 정보
    mongo_url = "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594"
    
    print("🔗 Railway MongoDB 연결 테스트 시작...")
    print(f"📝 연결 URL: {mongo_url.replace('HYxotmUHxMxbYAejsOxEnHwrgKpAochC', '***')}")
    
    try:
        # MongoDB 클라이언트 생성
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=15000)
        
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
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")
        print(f"🔍 상세 오류: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("🚀 Railway MongoDB 연결 테스트")
    print("=" * 40)
    
    success = test_railway_mongo()
    
    if success:
        print("\n🎉 Railway MongoDB 연결이 성공했습니다!")
        print("이제 final_server.py를 실행하면 MongoDB를 사용할 수 있습니다.")
    else:
        print("\n❌ Railway MongoDB 연결에 실패했습니다.")
        print("다음을 확인해주세요:")
        print("1. Railway 프로젝트에서 MongoDB 서비스가 실행 중인지 확인")
        print("2. 연결 정보가 올바른지 확인")
        print("3. 네트워크 연결 상태 확인") 