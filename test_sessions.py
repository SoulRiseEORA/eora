import requests
import json

def test_sessions():
    base_url = "http://127.0.0.1:8001"
    
    # 1. 세션 생성
    print("=== 세션 생성 테스트 ===")
    create_data = {
        "user_id": "test_user_001",
        "session_name": "테스트 세션"
    }
    
    try:
        response = requests.post(f"{base_url}/api/sessions", json=create_data)
        print(f"Create Session Status: {response.status_code}")
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data.get("session_id")
            print(f"Created Session ID: {session_id}")
        else:
            print(f"Create Session Error: {response.text}")
            return False
    except Exception as e:
        print(f"Create Session Error: {e}")
        return False
    
    # 2. 세션 목록 조회
    print("\n=== 세션 목록 조회 테스트 ===")
    try:
        response = requests.get(f"{base_url}/api/sessions")
        print(f"Get Sessions Status: {response.status_code}")
        if response.status_code == 200:
            sessions = response.json()
            print(f"Found {len(sessions)} sessions")
        else:
            print(f"Get Sessions Error: {response.text}")
    except Exception as e:
        print(f"Get Sessions Error: {e}")
    
    # 3. 세션 메시지 조회
    if session_id:
        print(f"\n=== 세션 메시지 조회 테스트 (Session ID: {session_id}) ===")
        try:
            response = requests.get(f"{base_url}/api/sessions/{session_id}/messages")
            print(f"Get Messages Status: {response.status_code}")
            if response.status_code == 200:
                messages = response.json()
                print(f"Found {len(messages)} messages")
            else:
                print(f"Get Messages Error: {response.text}")
        except Exception as e:
            print(f"Get Messages Error: {e}")
    
    return True

if __name__ == "__main__":
    print("=== 세션 API 테스트 ===")
    success = test_sessions()
    if success:
        print("\n✅ 세션 테스트 성공!")
    else:
        print("\n❌ 세션 테스트 실패!") 