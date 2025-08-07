#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
레일웨이 MongoDB 연결 테스트 스크립트
로컬에서 레일웨이 환경변수를 시뮬레이션하여 테스트
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트 설정
project_root = Path(__file__).parent
sys.path.append(str(project_root / "src"))

def simulate_railway_env():
    """레일웨이 환경변수 시뮬레이션"""
    print("🚂 레일웨이 환경변수 설정 중...")
    
    # 레일웨이 환경변수 설정
    railway_env_vars = {
        "RAILWAY_ENVIRONMENT": "production",
        "RAILWAY_PROJECT_ID": "test_project",
        "RAILWAY_SERVICE_ID": "test_service",
        "DATABASE_NAME": "eora_ai",
        "MONGOUSER": "mongo",
        "MONGOPASSWORD": "HYxotmUHxMxbYAejsOxEnHwrgKpAochC",
        "MONGOHOST": "trolley.proxy.rlwy.net",
        "MONGOPORT": "26594",
        "MONGODB_URL": "mongodb://mongo:HYxotmUHxMxbYAejsOxEnHwrgKpAochC@trolley.proxy.rlwy.net:26594"
    }
    
    for key, value in railway_env_vars.items():
        os.environ[key] = value
        print(f"   ✅ {key}: {value[:50]}...")

def test_mongodb_connection():
    """MongoDB 연결 테스트"""
    print("\n=== MongoDB 연결 테스트 ===")
    
    try:
        # database 모듈 import (환경변수 설정 후)
        from database import (
            init_mongodb_connection, verify_connection, 
            mongo_client, DATABASE_NAME, MONGODB_URL,
            sessions_collection, chat_logs_collection, memories_collection
        )
        
        print(f"📊 데이터베이스 이름: {DATABASE_NAME}")
        print(f"🔗 MongoDB URL: {MONGODB_URL[:50]}...")
        
        # 연결 시도
        if init_mongodb_connection():
            print("✅ MongoDB 초기화 성공")
        else:
            print("❌ MongoDB 초기화 실패")
            return False
        
        # 연결 확인
        if verify_connection():
            print("✅ MongoDB 연결 확인 성공")
        else:
            print("❌ MongoDB 연결 확인 실패")
            return False
        
        # 컬렉션 확인
        if mongo_client:
            db = mongo_client[DATABASE_NAME]
            collections = db.list_collection_names()
            print(f"📂 사용 가능한 컬렉션: {len(collections)}개")
            for collection in collections[:5]:  # 처음 5개만 표시
                print(f"   - {collection}")
            if len(collections) > 5:
                print(f"   ... 총 {len(collections)}개")
        
        # 간단한 읽기/쓰기 테스트
        print("\n=== 읽기/쓰기 테스트 ===")
        
        if sessions_collection is not None:
            # 세션 개수 확인
            session_count = sessions_collection.count_documents({})
            print(f"📊 현재 세션 수: {session_count}개")
            
            # 테스트 세션 생성
            test_session = {
                "session_id": "test_railway_session",
                "user_id": "test@railway.app",
                "name": "Railway 연결 테스트",
                "created_at": "2025-01-01T00:00:00",
                "message_count": 0
            }
            
            try:
                # 기존 테스트 세션 삭제
                sessions_collection.delete_many({"session_id": "test_railway_session"})
                
                # 새 테스트 세션 생성
                result = sessions_collection.insert_one(test_session)
                print(f"✅ 테스트 세션 생성 성공: {result.inserted_id}")
                
                # 생성된 세션 조회
                retrieved = sessions_collection.find_one({"session_id": "test_railway_session"})
                if retrieved:
                    print(f"✅ 테스트 세션 조회 성공: {retrieved['name']}")
                else:
                    print("❌ 테스트 세션 조회 실패")
                
                # 테스트 세션 삭제
                delete_result = sessions_collection.delete_one({"session_id": "test_railway_session"})
                if delete_result.deleted_count > 0:
                    print("✅ 테스트 세션 삭제 성공")
                else:
                    print("❌ 테스트 세션 삭제 실패")
                
            except Exception as e:
                print(f"❌ 읽기/쓰기 테스트 실패: {e}")
                return False
        
        print("\n🎉 모든 테스트 통과 - 레일웨이 MongoDB 연결 준비 완료!")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB 연결 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_detection():
    """환경 감지 테스트"""
    print("\n=== 환경 감지 테스트 ===")
    
    railway_indicators = [
        "RAILWAY_ENVIRONMENT",
        "RAILWAY_PROJECT_ID", 
        "RAILWAY_SERVICE_ID"
    ]
    
    detected_railway = any(os.getenv(var) for var in railway_indicators)
    print(f"🚂 레일웨이 환경 감지: {'✅ Yes' if detected_railway else '❌ No'}")
    
    for var in railway_indicators:
        value = os.getenv(var)
        print(f"   - {var}: {'✅ 설정됨' if value else '❌ 없음'}")
    
    return detected_railway

def main():
    """메인 테스트 실행"""
    print("=" * 60)
    print("🧪 레일웨이 MongoDB 연결 테스트")
    print("=" * 60)
    
    # 1. 레일웨이 환경변수 시뮬레이션
    simulate_railway_env()
    
    # 2. 환경 감지 테스트
    env_detected = test_environment_detection()
    
    # 3. MongoDB 연결 테스트
    connection_success = test_mongodb_connection()
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    print(f"🚂 레일웨이 환경 감지: {'✅' if env_detected else '❌'}")
    print(f"🔗 MongoDB 연결: {'✅' if connection_success else '❌'}")
    
    if env_detected and connection_success:
        print("\n🎉 성공: 레일웨이 환경에서 MongoDB 연결 준비 완료!")
        print("   📈 대화와 메모리가 레일웨이 MongoDB에 저장됩니다")
        print("   🔒 영구 저장소로 데이터 보존됩니다")
        print("   ☁️ 클라우드 환경에서 안정적으로 작동합니다")
    else:
        if not env_detected:
            print("\n⚠️ 환경 감지 실패: 레일웨이 환경변수를 확인하세요")
        if not connection_success:
            print("\n❌ 연결 실패: MongoDB 설정을 확인하세요")
            print("   🔧 MONGODB_URL, MONGOUSER, MONGOPASSWORD 등을 확인")
            print("   🚂 레일웨이 MongoDB 서비스가 실행 중인지 확인")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 