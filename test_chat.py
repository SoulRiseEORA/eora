import requests
import json

def test_chat():
    url = "http://127.0.0.1:8001/api/chat"
    data = {
        "message": "안녕하세요! 테스트 메시지입니다.",
        "session_id": "test_session_001",
        "user_id": "test_user_001"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        response_data = response.json()
        print(f"Response Keys: {list(response_data.keys())}")
        print(f"Response: {response_data.get('response', 'No response')}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=== 채팅 API 테스트 ===")
    success = test_chat()
    if success:
        print("✅ 채팅 테스트 성공!")
    else:
        print("❌ 채팅 테스트 실패!") 