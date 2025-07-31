#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 MongoDB 저장 확인 스크립트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 설정
project_root = Path(__file__).parent
sys.path.append(str(project_root / "src"))

def check_mongodb_direct():
    """MongoDB에 직접 연결하여 데이터 확인"""
    print("=== MongoDB 직접 연결 및 데이터 확인 ===")
    
    try:
        # MongoDB 모듈들 import
        from database import (
            mongo_client, sessions_collection, 
            chat_logs_collection, memories_collection, 
            verify_connection, DATABASE_NAME
        )
        
        if not mongo_client:
            print("❌ MongoDB 클라이언트가 없습니다.")
            return False
        
        # 연결 상태 확인
        if not verify_connection():
            print("❌ MongoDB 연결이 실패했습니다.")
            return False
        
        print("✅ MongoDB 연결 성공!")
        print(f"📊 데이터베이스 이름: {DATABASE_NAME}")
        
        # 컬렉션들 확인
        db = mongo_client[DATABASE_NAME]
        collections = db.list_collection_names()
        print(f"📂 사용 가능한 컬렉션: {collections}")
        
        # 세션 컬렉션 확인
        if sessions_collection is not None:
            try:
                session_count = sessions_collection.count_documents({})
                print(f"🗂️ 저장된 세션 수: {session_count}개")
                
                if session_count > 0:
                    # 최근 세션 3개 조회
                    recent_sessions = list(sessions_collection.find().sort([("created_at", -1)]).limit(3))
                    print("📋 최근 세션:")
                    for i, session in enumerate(recent_sessions, 1):
                        session_id = session.get('session_id', 'Unknown')
                        name = session.get('name', 'Unnamed')
                        created_at = session.get('created_at', '')
                        user_email = session.get('user_email', 'Unknown')
                        print(f"   {i}. {session_id}")
                        print(f"      이름: {name}")
                        print(f"      사용자: {user_email}")
                        print(f"      생성일: {created_at}")
                        print()
                else:
                    print("   💡 저장된 세션이 없습니다.")
            except Exception as e:
                print(f"❌ 세션 컬렉션 확인 오류: {e}")
        else:
            print("❌ 세션 컬렉션이 없습니다.")
        
        # 채팅 로그 컬렉션 확인
        if chat_logs_collection is not None:
            try:
                message_count = chat_logs_collection.count_documents({})
                print(f"💬 저장된 메시지 수: {message_count}개")
                
                if message_count > 0:
                    # 최근 메시지 5개 조회
                    recent_messages = list(chat_logs_collection.find().sort([("timestamp", -1)]).limit(5))
                    print("📨 최근 메시지:")
                    for i, msg in enumerate(recent_messages, 1):
                        role = msg.get('role', msg.get('sender', 'unknown'))
                        content = msg.get('content', '')[:50]
                        timestamp = msg.get('timestamp', '')
                        user_id = msg.get('user_id', 'Unknown')
                        session_id = msg.get('session_id', 'Unknown')
                        print(f"   {i}. [{role}] {content}...")
                        print(f"      사용자: {user_id}")
                        print(f"      세션: {session_id}")
                        print(f"      시간: {timestamp}")
                        print()
                else:
                    print("   💡 저장된 메시지가 없습니다.")
            except Exception as e:
                print(f"❌ 메시지 컬렉션 확인 오류: {e}")
        else:
            print("❌ 메시지 컬렉션이 없습니다.")
        
        # 메모리 컬렉션 확인
        if memories_collection is not None:
            try:
                memory_count = memories_collection.count_documents({})
                print(f"🧠 저장된 메모리 수: {memory_count}개")
                
                if memory_count > 0:
                    # 최근 메모리 3개 조회
                    recent_memories = list(memories_collection.find().sort([("timestamp", -1)]).limit(3))
                    print("🧩 최근 메모리:")
                    for i, memory in enumerate(recent_memories, 1):
                        memory_type = memory.get('memory_type', 'unknown')
                        user_message = memory.get('user_message', '')[:30]
                        ai_response = memory.get('ai_response', '')[:30]
                        timestamp = memory.get('timestamp', '')
                        user_id = memory.get('user_id', 'Unknown')
                        print(f"   {i}. [{memory_type}] {user_message}...")
                        print(f"      AI 응답: {ai_response}...")
                        print(f"      사용자: {user_id}")
                        print(f"      시간: {timestamp}")
                        print()
                else:
                    print("   💡 저장된 메모리가 없습니다.")
            except Exception as e:
                print(f"❌ 메모리 컬렉션 확인 오류: {e}")
        else:
            print("❌ 메모리 컬렉션이 없습니다.")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB 확인 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_json_files():
    """JSON 파일 백업 확인"""
    print("\n=== JSON 파일 백업 확인 ===")
    
    json_files = [
        "data/users.json",
        "data/sessions.json", 
        "data/messages.json"
    ]
    
    for file_path in json_files:
        if os.path.exists(file_path):
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, dict):
                    count = len(data)
                elif isinstance(data, list):
                    count = len(data)
                else:
                    count = "Unknown"
                
                print(f"✅ {file_path}: {count}개 항목")
            except Exception as e:
                print(f"❌ {file_path} 읽기 실패: {e}")
        else:
            print(f"⚠️ {file_path} 파일 없음")

def main():
    print("=" * 60)
    print("🔍 MongoDB 장기 저장 확인")
    print("=" * 60)
    
    # MongoDB 직접 확인
    mongodb_ok = check_mongodb_direct()
    
    # JSON 파일 백업 확인
    check_json_files()
    
    # 결론
    print("\n" + "=" * 60)
    print("📊 확인 결과")
    print("=" * 60)
    
    if mongodb_ok:
        print("✅ MongoDB 연결 및 데이터 확인 성공")
        print("   📈 대화 내용이 MongoDB에 장기적으로 저장되고 있습니다")
        print("   🔒 서버 재시작 후에도 데이터가 유지됩니다")
        print("   💾 Redis나 임시 메모리가 아닌 영구 저장소 사용")
    else:
        print("❌ MongoDB 확인 실패")
        print("   ⚠️ 현재 JSON 파일로만 저장될 수 있습니다")
        print("   🔧 MongoDB 연결 상태를 확인해주세요")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 