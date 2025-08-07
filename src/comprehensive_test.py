import requests
import json
import time
import asyncio
from datetime import datetime

def test_all_apis():
    base_url = "http://127.0.0.1:8001"
    
    print("🚀 EORA AI 시스템 종합 테스트 시작")
    print("=" * 60)
    
    # 1. 헬스 체크
    print("\n1️⃣ 헬스 체크 테스트")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health Check: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
    
    # 2. API 상태 확인
    print("\n2️⃣ API 상태 확인")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        print(f"✅ API Status: {response.status_code}")
        data = response.json()
        print(f"Database Available: {data.get('database_available', 'N/A')}")
        print(f"OpenAI Available: {data.get('openai_available', 'N/A')}")
    except Exception as e:
        print(f"❌ API Status Failed: {e}")
    
    # 3. 관리자 로그인 테스트
    print("\n3️⃣ 관리자 로그인 테스트")
    try:
        login_data = {
            "email": "admin@eora.ai",
            "password": "admin123"
        }
        response = requests.post(f"{base_url}/api/auth/login", 
                               json=login_data, timeout=10)
        print(f"✅ Admin Login: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Login Success: {data.get('success', False)}")
            print(f"User ID: {data.get('user_id', 'N/A')}")
            print(f"Is Admin: {data.get('is_admin', False)}")
        else:
            print(f"Login Failed: {response.text}")
    except Exception as e:
        print(f"❌ Admin Login Failed: {e}")
    
    # 4. 세션 생성 테스트
    print("\n4️⃣ 세션 생성 테스트")
    try:
        session_data = {
            "user_id": "test_user_123",
            "session_name": "테스트 세션"
        }
        response = requests.post(f"{base_url}/api/sessions", 
                               json=session_data, timeout=10)
        print(f"✅ Session Create: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            session_id = data.get('session_id')
            print(f"Session ID: {session_id}")
            print(f"Session Name: {data.get('session_name', 'N/A')}")
        else:
            print(f"Session Create Failed: {response.text}")
            session_id = None
    except Exception as e:
        print(f"❌ Session Create Failed: {e}")
        session_id = None
    
    # 5. 메시지 저장 테스트
    if session_id:
        print("\n5️⃣ 메시지 저장 테스트")
        try:
            message_data = {
                "session_id": session_id,
                "sender": "user",
                "content": "안녕하세요! 테스트 메시지입니다."
            }
            response = requests.post(f"{base_url}/api/messages", 
                                   json=message_data, timeout=10)
            print(f"✅ Message Save: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Message ID: {data.get('message_id', 'N/A')}")
            else:
                print(f"Message Save Failed: {response.text}")
        except Exception as e:
            print(f"❌ Message Save Failed: {e}")
    
    # 6. 세션 메시지 조회 테스트
    if session_id:
        print("\n6️⃣ 세션 메시지 조회 테스트")
        try:
            response = requests.get(f"{base_url}/api/sessions/{session_id}/messages", 
                                  timeout=10)
            print(f"✅ Session Messages: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                messages = data.get('messages', [])
                print(f"Message Count: {len(messages)}")
                for i, msg in enumerate(messages[:3]):  # 처음 3개만 출력
                    print(f"  {i+1}. {msg.get('sender', 'N/A')}: {msg.get('content', 'N/A')[:50]}...")
            else:
                print(f"Session Messages Failed: {response.text}")
        except Exception as e:
            print(f"❌ Session Messages Failed: {e}")
    
    # 7. 세션 목록 조회 테스트
    print("\n7️⃣ 세션 목록 조회 테스트")
    try:
        response = requests.get(f"{base_url}/api/sessions?user_id=test_user_123", 
                              timeout=10)
        print(f"✅ Session List: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            sessions = data.get('sessions', [])
            print(f"Session Count: {len(sessions)}")
            for i, session in enumerate(sessions[:3]):  # 처음 3개만 출력
                print(f"  {i+1}. {session.get('session_name', 'N/A')} (ID: {session.get('session_id', 'N/A')})")
        else:
            print(f"Session List Failed: {response.text}")
    except Exception as e:
        print(f"❌ Session List Failed: {e}")
    
    # 8. GPT 채팅 테스트
    print("\n8️⃣ GPT 채팅 테스트")
    try:
        chat_data = {
            "message": "안녕하세요! 간단한 테스트입니다.",
            "user_id": "test_user_123",
            "session_id": session_id or "test_session"
        }
        start_time = time.time()
        response = requests.post(f"{base_url}/api/chat", 
                               json=chat_data, timeout=30)
        end_time = time.time()
        print(f"✅ GPT Chat: {response.status_code}")
        print(f"Response Time: {end_time - start_time:.2f}초")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data.get('response', 'N/A')[:100]}...")
            print(f"Consciousness Level: {data.get('consciousness_level', 'N/A')}")
        else:
            print(f"GPT Chat Failed: {response.text}")
    except Exception as e:
        print(f"❌ GPT Chat Failed: {e}")
    
    # 9. 관리자 사용자 목록 테스트
    print("\n9️⃣ 관리자 사용자 목록 테스트")
    try:
        response = requests.get(f"{base_url}/api/admin/users", timeout=10)
        print(f"✅ Admin Users: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            users = data.get('users', [])
            print(f"User Count: {len(users)}")
            for i, user in enumerate(users[:3]):  # 처음 3개만 출력
                print(f"  {i+1}. {user.get('name', 'N/A')} ({user.get('email', 'N/A')})")
        else:
            print(f"Admin Users Failed: {response.text}")
    except Exception as e:
        print(f"❌ Admin Users Failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 종합 테스트 완료!")
    print(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    # 서버 시작 대기
    print("서버 시작 대기 중... (5초)")
    time.sleep(5)
    test_all_apis() 