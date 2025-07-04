#!/usr/bin/env python3
"""
MongoDB 연결 테스트 스크립트
"""

import os
import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import json

def test_mongodb_connection():
    """MongoDB 연결을 테스트합니다."""
    
    print("🔍 MongoDB 연결 테스트 시작")
    print("=" * 50)
    
    # Railway MongoDB 환경변수 설정
    os.environ['MONGODB_URI'] = 'mongodb://mongo:admin1234@trolley.proxy.rlwy.net:26594'
    os.environ['MONGODB_DB'] = 'eora_ai'
    
    mongodb_uri = os.getenv('MONGODB_URI')
    mongodb_db = os.getenv('MONGODB_DB', 'eora_ai')
    
    print(f"📝 연결 URL: {mongodb_uri}")
    print(f"📁 데이터베이스: {mongodb_db}")
    
    try:
        # MongoDB 클라이언트 생성
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # 연결 테스트
        client.admin.command('ping')
        print("✅ MongoDB 연결 성공!")
        
        # 데이터베이스 선택
        db = client[mongodb_db]
        
        # 컬렉션 목록 확인
        collections = db.list_collection_names()
        print(f"📋 컬렉션 목록: {collections}")
        
        # 채팅 컬렉션 확인
        if 'chats' in collections:
            chat_count = db.chats.count_documents({})
            print(f"💬 채팅 메시지 수: {chat_count}")
            
            # 최근 채팅 메시지 확인
            recent_chats = list(db.chats.find().sort('timestamp', -1).limit(5))
            print(f"📝 최근 채팅 메시지:")
            for chat in recent_chats:
                print(f"  - {chat.get('timestamp', 'N/A')}: {chat.get('user_id', 'N/A')} - {chat.get('message', 'N/A')[:50]}...")
        
        # 사용자 컬렉션 확인
        if 'users' in collections:
            user_count = db.users.count_documents({})
            print(f"👥 사용자 수: {user_count}")
        
        client.close()
        return True
        
    except ConnectionFailure as e:
        print(f"❌ MongoDB 연결 실패: {e}")
        return False
    except ServerSelectionTimeoutError as e:
        print(f"❌ MongoDB 서버 선택 타임아웃: {e}")
        return False
    except Exception as e:
        print(f"❌ MongoDB 연결 오류: {e}")
        return False

def test_chat_save():
    """채팅 저장 테스트를 수행합니다."""
    
    print("\n🔍 채팅 저장 테스트")
    print("=" * 50)
    
    try:
        mongodb_uri = os.getenv('MONGODB_URI')
        mongodb_db = os.getenv('MONGODB_DB', 'eora_ai')
        
        client = MongoClient(mongodb_uri)
        db = client[mongodb_db]
        
        # 테스트 채팅 메시지 저장
        test_chat = {
            'user_id': 'test_user_001',
            'session_id': 'test_session_001',
            'message': 'MongoDB 연결 테스트 메시지',
            'response': '테스트 응답입니다.',
            'timestamp': '2025-07-04T15:30:00.000000'
        }
        
        result = db.chats.insert_one(test_chat)
        print(f"✅ 테스트 채팅 저장 성공: {result.inserted_id}")
        
        # 저장된 메시지 확인
        saved_chat = db.chats.find_one({'_id': result.inserted_id})
        print(f"📝 저장된 메시지: {saved_chat}")
        
        # 테스트 메시지 삭제
        db.chats.delete_one({'_id': result.inserted_id})
        print("🗑️ 테스트 메시지 삭제 완료")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ 채팅 저장 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    print("🚀 MongoDB 연결 테스트 시작")
    print("=" * 50)
    
    # MongoDB 연결 테스트
    connection_success = test_mongodb_connection()
    
    if connection_success:
        # 채팅 저장 테스트
        save_success = test_chat_save()
        
        if save_success:
            print("\n🎉 모든 테스트 통과!")
            print("✅ MongoDB 연결 및 저장 기능이 정상 작동합니다.")
        else:
            print("\n⚠️ 채팅 저장 테스트 실패")
    else:
        print("\n❌ MongoDB 연결 실패")
    
    print("\n" + "=" * 50)
    print("테스트 완료")
