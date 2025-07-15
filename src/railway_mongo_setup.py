#!/usr/bin/env python3
"""
Railway MongoDB 연결 테스트 및 설정 스크립트
"""

import os
import sys
from pymongo import MongoClient

def test_mongo_connection():
    """Railway MongoDB 연결 테스트"""
    
    # Railway MongoDB 연결 정보
    mongo_public_url = "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594"
    
    print("🔗 Railway MongoDB 연결 테스트 시작...")
    print(f"📝 연결 URL: {mongo_public_url.replace('HYxotmUHxMxbYAejsOxEnHwrgKpAochC', '***')}")
    
    try:
        # MongoDB 클라이언트 생성
        client = MongoClient(mongo_public_url, serverSelectionTimeoutMS=10000)
        
        # 연결 테스트
        client.admin.command('ping')
        print("✅ MongoDB 연결 성공!")
        
        # 데이터베이스 및 컬렉션 생성 테스트
        db = client.eora_ai
        users_collection = db.users
        points_collection = db.points
        
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
        
        # 컬렉션 목록 확인
        collections = db.list_collection_names()
        print(f"📋 현재 컬렉션 목록: {collections}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")
        print(f"🔍 상세 오류: {type(e).__name__}")
        return False

def setup_environment():
    """환경변수 설정"""
    print("\n🔧 환경변수 설정...")
    
    # 환경변수 설정
    os.environ["MONGOUSER"] = "mongo"
    os.environ["MONGOPASSWORD"] = "HYxotmUHxMxbYAejsOxEnHwrgKpAochC"
    os.environ["MONGOHOST"] = "trolley.proxy.rlwy.net"
    os.environ["MONGOPORT"] = "26594"
    os.environ["MONGO_PUBLIC_URL"] = "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594"
    os.environ["MONGO_URL"] = "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@mongodb.railway.internal:27017"
    
    print("✅ 환경변수 설정 완료")
    
    # 설정된 환경변수 확인
    print("\n📋 설정된 환경변수:")
    print(f"MONGOUSER: {os.environ.get('MONGOUSER')}")
    print(f"MONGOHOST: {os.environ.get('MONGOHOST')}")
    print(f"MONGOPORT: {os.environ.get('MONGOPORT')}")
    print(f"MONGO_PUBLIC_URL: {os.environ.get('MONGO_PUBLIC_URL').replace('HYxotmUHxMxbYAejsOxEnHwrgKpAochC', '***')}")

def main():
    """메인 함수"""
    print("🚀 Railway MongoDB 연결 테스트 및 설정")
    print("=" * 50)
    
    # 환경변수 설정
    setup_environment()
    
    # MongoDB 연결 테스트
    success = test_mongo_connection()
    
    if success:
        print("\n🎉 Railway MongoDB 연결이 성공했습니다!")
        print("이제 final_server.py를 실행하면 MongoDB를 사용할 수 있습니다.")
        print("\n실행 방법:")
        print("python final_server.py")
    else:
        print("\n❌ Railway MongoDB 연결에 실패했습니다.")
        print("다음을 확인해주세요:")
        print("1. Railway 프로젝트에서 MongoDB 서비스가 실행 중인지 확인")
        print("2. 연결 정보가 올바른지 확인")
        print("3. 네트워크 연결 상태 확인")

if __name__ == "__main__":
    main() 