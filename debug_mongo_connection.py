#!/usr/bin/env python3
"""
MongoDB 연결 상태 및 사용자 데이터 디버깅
"""

import os

try:
    from pymongo import MongoClient
    print("✅ PyMongo 라이브러리 로드 성공")
except ImportError:
    print("❌ PyMongo 라이브러리가 설치되지 않았습니다.")
    exit(1)

def debug_mongo_connection():
    """MongoDB 연결 상태 및 사용자 데이터 확인"""
    
    print("🔍 MongoDB 연결 상태 및 사용자 데이터 디버깅")
    print("=" * 60)
    
    # Railway MongoDB 연결 정보
    mongo_public_url = "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594"
    
    try:
        # MongoDB 클라이언트 생성
        client = MongoClient(mongo_public_url, serverSelectionTimeoutMS=15000)
        
        # 연결 테스트
        client.admin.command('ping')
        print("✅ MongoDB 연결 성공!")
        
        # 데이터베이스 및 컬렉션 확인
        db = client.eora_ai
        users_collection = db.users
        
        # 컬렉션 목록 확인
        collections = db.list_collection_names()
        print(f"📋 데이터베이스 컬렉션 목록: {collections}")
        
        # 사용자 컬렉션 문서 수 확인
        user_count = users_collection.count_documents({})
        print(f"👥 사용자 컬렉션 문서 수: {user_count}")
        
        # 모든 사용자 조회
        all_users = list(users_collection.find({}))
        print(f"📋 모든 사용자 목록:")
        for i, user in enumerate(all_users, 1):
            print(f"  {i}. ID: {user.get('user_id', 'N/A')}")
            print(f"     이메일: {user.get('email', 'N/A')}")
            print(f"     이름: {user.get('name', 'N/A')}")
            print(f"     관리자: {user.get('is_admin', False)}")
            print(f"     생성일: {user.get('created_at', 'N/A')}")
            print()
        
        # 관리자 계정 특별 확인
        admin_users = list(users_collection.find({
            "$or": [
                {"email": "admin@eora.ai"},
                {"user_id_login": "admin"}
            ]
        }))
        
        print(f"🔐 관리자 계정 검색 결과:")
        if admin_users:
            for admin in admin_users:
                print(f"  ✅ 관리자 계정 발견:")
                print(f"     ID: {admin.get('user_id', 'N/A')}")
                print(f"     이메일: {admin.get('email', 'N/A')}")
                print(f"     로그인 ID: {admin.get('user_id_login', 'N/A')}")
                print(f"     관리자 권한: {admin.get('is_admin', False)}")
        else:
            print("  ❌ 관리자 계정을 찾을 수 없습니다.")
        
        # 데이터베이스 통계
        print(f"\n📊 데이터베이스 통계:")
        print(f"  데이터베이스 이름: {db.name}")
        print(f"  컬렉션 수: {len(collections)}")
        print(f"  사용자 수: {user_count}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")
        print(f"🔍 상세 오류: {type(e).__name__}")
        return False

def main():
    """메인 함수"""
    print("🚀 MongoDB 연결 상태 및 사용자 데이터 디버깅")
    print("=" * 60)
    
    success = debug_mongo_connection()
    
    if success:
        print("\n✅ 디버깅 완료!")
        print("💡 만약 관리자 계정이 없다면 서버를 재시작하세요.")
    else:
        print("\n❌ 디버깅 실패!")
        print("💡 MongoDB 연결을 확인하세요.")

if __name__ == "__main__":
    main() 