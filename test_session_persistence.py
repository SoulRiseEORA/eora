#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
세션 저장 및 불러오기 시스템 테스트 스크립트
"""

import requests
import json
import time
import uuid

BASE_URL = "http://localhost:8001"

def test_sessions_api():
    """세션 목록 API 테스트"""
    print("\n=== 세션 목록 API 테스트 ===")
    
    try:
        # 세션 목록 가져오기
        response = requests.get(f"{BASE_URL}/api/sessions")
        if response.status_code == 200:
            data = response.json()
            sessions = data.get("sessions", [])
            print(f"✅ 세션 목록 조회 성공: {len(sessions)}개 세션")
            
            if sessions:
                print("\n📋 세션 목록:")
                for i, session in enumerate(sessions[:5]):  # 최대 5개만 표시
                    print(f"  {i+1}. {session.get('name', 'Unknown')} (ID: {session.get('id', '')[:20]}...)")
                    print(f"     - 생성일: {session.get('created_at', 'Unknown')}")
                    print(f"     - 메시지 수: {session.get('message_count', 0)}")
            else:
                print("⚠️ 저장된 세션이 없습니다.")
                
            return sessions
        else:
            print(f"❌ 세션 목록 조회 실패: {response.status_code}")
            return []
            
    except requests.ConnectionError:
        print("❌ 서버 연결 실패. 서버가 실행 중인지 확인하세요.")
        return []
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return []

def test_session_messages(session_id):
    """특정 세션의 메시지 조회 테스트"""
    print(f"\n=== 세션 메시지 조회 테스트 (ID: {session_id[:20]}...) ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/sessions/{session_id}/messages")
        if response.status_code == 200:
            data = response.json()
            messages = data.get("messages", [])
            print(f"✅ 메시지 조회 성공: {len(messages)}개 메시지")
            
            if messages:
                print("\n📝 메시지 내용:")
                for i, msg in enumerate(messages[:6]):  # 최대 6개만 표시
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")[:100]  # 최대 100자
                    timestamp = msg.get("timestamp", "")
                    
                    role_emoji = "👤" if role == "user" else "🤖"
                    print(f"  {role_emoji} {role}: {content}...")
                    
            return True
        else:
            print(f"❌ 메시지 조회 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def test_chat_and_reload():
    """채팅 후 새로고침 시뮬레이션 테스트"""
    print("\n=== 채팅 및 새로고침 테스트 ===")
    
    try:
        # 1. 새 세션으로 채팅 전송
        session_id = f"session_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        print(f"📝 새 세션 ID 생성: {session_id}")
        
        chat_data = {
            "message": "안녕하세요! 세션 저장 테스트입니다.",
            "session_id": session_id
        }
        
        response = requests.post(f"{BASE_URL}/api/chat", json=chat_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ 채팅 전송 성공")
            print(f"   AI 응답: {data.get('response', '')[:100]}...")
            
            # 2. 잠시 대기 (저장 시간 확보)
            time.sleep(1)
            
            # 3. 세션 목록에서 확인
            sessions = test_sessions_api()
            found = any(s.get("id") == session_id for s in sessions)
            
            if found:
                print(f"\n✅ 새로고침 후에도 세션이 유지됩니다!")
                
                # 4. 메시지 조회
                test_session_messages(session_id)
            else:
                print(f"\n❌ 세션이 저장되지 않았습니다.")
                
        else:
            print(f"❌ 채팅 전송 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def test_mongodb_connection():
    """MongoDB 연결 상태 확인"""
    print("\n=== MongoDB 연결 테스트 ===")
    
    try:
        # admin API를 통해 리소스 상태 확인
        response = requests.get(f"{BASE_URL}/api/admin/resources")
        if response.status_code == 200:
            data = response.json()
            db_status = data.get("database", {})
            
            if db_status.get("status") == "connected":
                print("✅ MongoDB 연결 상태: 정상")
                print(f"   - 컬렉션 수: {db_status.get('collections', 0)}")
            else:
                print("⚠️ MongoDB 연결 없음 - 메모리 캐시 사용 중")
                print("   (서버 재시작 시 데이터가 사라집니다)")
        else:
            print("⚠️ 데이터베이스 상태를 확인할 수 없습니다")
            
    except Exception as e:
        print(f"⚠️ 상태 확인 실패: {e}")

if __name__ == "__main__":
    print("🔧 세션 저장 및 불러오기 시스템 테스트 시작")
    print(f"📍 테스트 서버: {BASE_URL}")
    print("=" * 50)
    
    # MongoDB 연결 상태 확인
    test_mongodb_connection()
    
    # 기존 세션 목록 조회
    existing_sessions = test_sessions_api()
    
    # 첫 번째 세션의 메시지 조회 (있다면)
    if existing_sessions:
        first_session_id = existing_sessions[0]["id"]
        test_session_messages(first_session_id)
    
    # 새 채팅 생성 및 새로고침 테스트
    test_chat_and_reload()
    
    print("\n✅ 테스트 완료!")
    print("\n💡 팁: 브라우저에서 채팅 페이지를 열고 실제로 테스트해보세요.")
    print(f"   주소: {BASE_URL}/chat") 