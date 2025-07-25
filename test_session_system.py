#!/usr/bin/env python3
"""세션 시스템 종합 테스트"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8001"
USER_ID = "admin@eora.ai"
HEADERS = {"X-User-Id": USER_ID}

def test_create_session():
    """새 세션 생성 테스트"""
    print("\n🆕 새 세션 생성 테스트")
    
    url = f"{BASE_URL}/api/sessions"
    data = {"name": f"테스트 세션 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
    
    response = requests.post(url, json=data, headers=HEADERS)
    print(f"응답 상태: {response.status_code}")
    
    if response.ok:
        session_data = response.json()
        print(f"✅ 세션 생성 성공: {json.dumps(session_data, indent=2, ensure_ascii=False)}")
        return session_data.get("session_id")
    else:
        print(f"❌ 세션 생성 실패: {response.text}")
        return None

def test_get_sessions():
    """세션 목록 조회 테스트"""
    print("\n📋 세션 목록 조회 테스트")
    
    url = f"{BASE_URL}/api/sessions"
    response = requests.get(url, headers=HEADERS)
    print(f"응답 상태: {response.status_code}")
    
    if response.ok:
        data = response.json()
        sessions = data.get("sessions", [])
        print(f"✅ 세션 개수: {len(sessions)}")
        for session in sessions[:3]:  # 처음 3개만 출력
            print(f"  - ID: {session['id']}, 이름: {session['name']}")
        return sessions
    else:
        print(f"❌ 세션 목록 조회 실패: {response.text}")
        return []

def test_get_messages(session_id):
    """세션 메시지 조회 테스트"""
    print(f"\n💬 세션 메시지 조회 테스트: {session_id}")
    
    url = f"{BASE_URL}/api/sessions/{session_id}/messages"
    response = requests.get(url, headers=HEADERS)
    print(f"응답 상태: {response.status_code}")
    
    if response.ok:
        data = response.json()
        messages = data.get("messages", [])
        print(f"✅ 메시지 개수: {len(messages)}")
        for msg in messages[:2]:  # 처음 2개만 출력
            print(f"  - {msg.get('role', 'unknown')}: {msg.get('content', '')[:50]}...")
    else:
        print(f"❌ 메시지 조회 실패: {response.text}")

def test_delete_session(session_id):
    """세션 삭제 테스트"""
    print(f"\n🗑️ 세션 삭제 테스트: {session_id}")
    
    url = f"{BASE_URL}/api/sessions/{session_id}"
    response = requests.delete(url, headers=HEADERS)
    print(f"응답 상태: {response.status_code}")
    
    if response.ok:
        data = response.json()
        print(f"✅ 세션 삭제 성공: {data}")
    else:
        print(f"❌ 세션 삭제 실패: {response.text}")

def test_chat_message(session_id):
    """채팅 메시지 전송 테스트"""
    print(f"\n💬 채팅 메시지 전송 테스트")
    
    url = f"{BASE_URL}/api/chat"
    data = {
        "message": "안녕하세요, 테스트 메시지입니다.",
        "session_id": session_id,
        "user_id": USER_ID
    }
    
    response = requests.post(url, json=data, headers=HEADERS)
    print(f"응답 상태: {response.status_code}")
    
    if response.ok:
        data = response.json()
        print(f"✅ AI 응답: {data.get('response', '')[:100]}...")
    else:
        print(f"❌ 채팅 실패: {response.text}")

def main():
    print("🧪 세션 시스템 종합 테스트 시작")
    print(f"🌐 서버: {BASE_URL}")
    print(f"👤 사용자: {USER_ID}")
    
    # 1. 세션 목록 조회
    sessions = test_get_sessions()
    
    # 2. 새 세션 생성
    new_session_id = test_create_session()
    
    if new_session_id:
        # 3. 채팅 메시지 전송
        test_chat_message(new_session_id)
        
        # 4. 메시지 조회
        test_get_messages(new_session_id)
        
        # 5. 세션 삭제
        test_delete_session(new_session_id)
    
    # 6. 기존 세션 메시지 조회
    if sessions and len(sessions) > 0:
        test_get_messages(sessions[0]['id'])
    
    print("\n✅ 테스트 완료")

if __name__ == "__main__":
    main() 