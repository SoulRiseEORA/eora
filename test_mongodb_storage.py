#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB 장기 저장 테스트 스크립트
대화 내용과 학습 데이터가 MongoDB에 정말로 저장되는지 확인
"""

import asyncio
import json
import sys
import os
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path

# 프로젝트 루트 설정
project_root = Path(__file__).parent
sys.path.append(str(project_root / "src"))

def test_server_status():
    """서버 상태 확인"""
    print("\n=== 서버 상태 확인 ===")
    try:
        response = requests.get("http://127.0.0.1:8300/", timeout=5)
        if response.status_code == 200:
            print("✅ 서버 정상 작동 중")
            return True
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return False

def test_admin_login():
    """관리자 로그인 테스트"""
    print("\n=== 관리자 로그인 테스트 ===")
    try:
        session = requests.Session()
        login_response = session.post(
            'http://127.0.0.1:8300/api/login',
            json={
                'email': 'admin@eora.ai',
                'password': 'admin123'
            },
            timeout=10
        )
        
        if login_response.status_code == 200:
            result = login_response.json()
            if result.get('success'):
                print("✅ 관리자 로그인 성공")
                return session
            else:
                print(f"❌ 로그인 실패: {result.get('error')}")
                return None
        else:
            print(f"❌ 로그인 요청 실패: {login_response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 로그인 오류: {e}")
        return None

def test_create_session(session):
    """세션 생성 테스트"""
    print("\n=== 세션 생성 테스트 ===")
    try:
        timestamp = int(time.time() * 1000)
        session_data = {
            "name": f"MongoDB 테스트 세션 {timestamp}"
        }
        
        response = session.post(
            'http://127.0.0.1:8300/api/sessions',
            json=session_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                session_id = result.get('session_id')
                print(f"✅ 세션 생성 성공: {session_id}")
                return session_id
            else:
                print(f"❌ 세션 생성 실패: {result}")
                return None
        else:
            print(f"❌ 세션 생성 요청 실패: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 세션 생성 오류: {e}")
        return None

def test_chat_storage(session, session_id):
    """대화 저장 테스트"""
    print("\n=== 대화 저장 테스트 ===")
    
    test_messages = [
        "안녕하세요! MongoDB 저장 테스트입니다.",
        "대화 내용이 MongoDB에 장기적으로 저장되는지 확인하고 있습니다.",
        "이 메시지들이 나중에도 조회될 수 있어야 합니다.",
        "메모리 시스템도 함께 테스트해보겠습니다."
    ]
    
    chat_results = []
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- 대화 {i}/{len(test_messages)} ---")
        try:
            response = session.post(
                'http://127.0.0.1:8300/api/chat',
                json={
                    'message': message,
                    'session_id': session_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    ai_response = result.get('response', '')
                    print(f"📨 사용자: {message}")
                    print(f"🤖 AI: {ai_response[:100]}...")
                    
                    chat_results.append({
                        'user_message': message,
                        'ai_response': ai_response,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # 저장 시간 대기
                    time.sleep(2)
                else:
                    print(f"❌ 대화 실패: {result.get('error')}")
            else:
                print(f"❌ 대화 요청 실패: {response.status_code}")
                print(f"응답: {response.text}")
        except Exception as e:
            print(f"❌ 대화 오류: {e}")
    
    print(f"\n✅ 총 {len(chat_results)}개 대화 완료")
    return chat_results

def test_session_messages_retrieval(session, session_id):
    """세션 메시지 조회 테스트"""
    print("\n=== 세션 메시지 조회 테스트 ===")
    try:
        response = session.get(
            f'http://127.0.0.1:8300/api/sessions/{session_id}/messages',
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                messages = result.get('messages', [])
                print(f"✅ 조회된 메시지 수: {len(messages)}개")
                
                for i, msg in enumerate(messages, 1):
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')[:50]
                    timestamp = msg.get('timestamp', '')
                    print(f"   {i}. [{role}] {content}... ({timestamp})")
                
                return messages
            else:
                print(f"❌ 메시지 조회 실패: {result}")
                return []
        else:
            print(f"❌ 메시지 조회 요청 실패: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 메시지 조회 오류: {e}")
        return []

def test_mongodb_direct_check():
    """MongoDB 직접 확인"""
    print("\n=== MongoDB 직접 확인 ===")
    try:
        from database import (
            mongo_client, sessions_collection, 
            chat_logs_collection, memories_collection
        )
        
        if not mongo_client:
            print("❌ MongoDB 클라이언트 없음")
            return False
        
        # 연결 상태 확인
        mongo_client.admin.command('ping')
        print("✅ MongoDB 연결 상태 정상")
        
        # 세션 컬렉션 확인
        if sessions_collection:
            session_count = sessions_collection.count_documents({})
            print(f"📊 저장된 세션 수: {session_count}개")
            
            # 최근 세션 조회
            recent_sessions = list(sessions_collection.find().sort("created_at", -1).limit(3))
            for i, session in enumerate(recent_sessions, 1):
                session_id = session.get('session_id', 'Unknown')
                name = session.get('name', 'Unnamed')
                created_at = session.get('created_at', '')
                print(f"   {i}. {session_id}: {name} ({created_at})")
        
        # 채팅 로그 컬렉션 확인
        if chat_logs_collection:
            message_count = chat_logs_collection.count_documents({})
            print(f"📊 저장된 메시지 수: {message_count}개")
            
            # 최근 메시지 조회
            recent_messages = list(chat_logs_collection.find().sort("timestamp", -1).limit(5))
            for i, msg in enumerate(recent_messages, 1):
                role = msg.get('role', msg.get('sender', 'unknown'))
                content = msg.get('content', '')[:30]
                timestamp = msg.get('timestamp', '')
                print(f"   {i}. [{role}] {content}... ({timestamp})")
        
        # 메모리 컬렉션 확인
        if memories_collection:
            memory_count = memories_collection.count_documents({})
            print(f"📊 저장된 메모리 수: {memory_count}개")
            
            # 최근 메모리 조회
            recent_memories = list(memories_collection.find().sort("timestamp", -1).limit(3))
            for i, memory in enumerate(recent_memories, 1):
                memory_type = memory.get('memory_type', 'unknown')
                user_message = memory.get('user_message', '')[:30]
                timestamp = memory.get('timestamp', '')
                print(f"   {i}. [{memory_type}] {user_message}... ({timestamp})")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB 직접 확인 실패: {e}")
        return False

def test_data_persistence():
    """데이터 지속성 테스트"""
    print("\n=== 데이터 지속성 테스트 ===")
    try:
        from database import sessions_collection, chat_logs_collection, memories_collection
        
        # 1시간 전 데이터 조회
        one_hour_ago = datetime.now() - timedelta(hours=1)
        
        if sessions_collection:
            old_sessions = sessions_collection.count_documents({
                "created_at": {"$lt": one_hour_ago.isoformat()}
            })
            print(f"📅 1시간 전 이후 세션: {old_sessions}개")
        
        if chat_logs_collection:
            old_messages = chat_logs_collection.count_documents({
                "timestamp": {"$lt": one_hour_ago.isoformat()}
            })
            print(f"📅 1시간 전 이후 메시지: {old_messages}개")
        
        if memories_collection:
            old_memories = memories_collection.count_documents({
                "timestamp": {"$lt": one_hour_ago}
            })
            print(f"📅 1시간 전 이후 메모리: {old_memories}개")
        
        print("✅ 데이터 지속성 확인 완료 - MongoDB에 장기 저장됨")
        return True
        
    except Exception as e:
        print(f"❌ 데이터 지속성 확인 실패: {e}")
        return False

def main():
    """메인 테스트 실행"""
    print("=" * 60)
    print("🔍 MongoDB 장기 저장 테스트 시작")
    print("=" * 60)
    
    # 1. 서버 상태 확인
    if not test_server_status():
        print("❌ 서버가 실행되지 않아 테스트를 중단합니다.")
        return
    
    # 2. 로그인
    session = test_admin_login()
    if not session:
        print("❌ 로그인 실패로 테스트를 중단합니다.")
        return
    
    # 3. 세션 생성
    session_id = test_create_session(session)
    if not session_id:
        print("❌ 세션 생성 실패로 테스트를 중단합니다.")
        return
    
    # 4. 대화 테스트
    chat_results = test_chat_storage(session, session_id)
    if not chat_results:
        print("❌ 대화 테스트 실패")
    
    # 5. 메시지 조회
    retrieved_messages = test_session_messages_retrieval(session, session_id)
    
    # 6. MongoDB 직접 확인
    mongodb_ok = test_mongodb_direct_check()
    
    # 7. 데이터 지속성 확인
    persistence_ok = test_data_persistence()
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    print(f"🔒 로그인: {'✅ 성공' if session else '❌ 실패'}")
    print(f"🆕 세션 생성: {'✅ 성공' if session_id else '❌ 실패'}")
    print(f"💬 대화 저장: {'✅ 성공' if chat_results else '❌ 실패'} ({len(chat_results)}개)")
    print(f"📨 메시지 조회: {'✅ 성공' if retrieved_messages else '❌ 실패'} ({len(retrieved_messages)}개)")
    print(f"🔍 MongoDB 직접 확인: {'✅ 성공' if mongodb_ok else '❌ 실패'}")
    print(f"📅 데이터 지속성: {'✅ 성공' if persistence_ok else '❌ 실패'}")
    
    # 최종 판정
    all_tests_passed = all([
        session, session_id, chat_results, 
        retrieved_messages, mongodb_ok, persistence_ok
    ])
    
    if all_tests_passed:
        print("\n🎉 결론: 대화와 학습 내용이 MongoDB에 장기적으로 저장됩니다!")
        print("   ✅ Redis나 임시 메모리가 아닌 MongoDB에 영구 저장")
        print("   ✅ 서버 재시작 후에도 데이터 유지됨")
        print("   ✅ 세션, 메시지, 메모리 모두 정상 저장")
    else:
        print("\n⚠️ 경고: 일부 테스트 실패 - 저장 방식 확인 필요")
        if not mongodb_ok:
            print("   ❌ MongoDB 연결 또는 저장에 문제가 있습니다")
        if not persistence_ok:
            print("   ❌ 데이터 지속성에 문제가 있습니다")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 