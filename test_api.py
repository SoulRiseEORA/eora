import requests
import json

def test_api():
    base_url = "http://127.0.0.1:8001"
    
    print("=== EORA AI 시스템 API 테스트 ===")
    
    # 1. Health Check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health Check: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Health Check 실패: {e}")
    
    print("\n" + "="*50)
    
    # 2. API Status
    try:
        response = requests.get(f"{base_url}/api/status")
        print(f"✅ API Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ API Status 실패: {e}")
    
    print("\n" + "="*50)
    
    # 3. Chat API Test
    try:
        chat_data = {
            "message": "안녕하세요! 테스트입니다.",
            "session_id": "test_session",
            "user_id": "test_user"
        }
        response = requests.post(f"{base_url}/api/chat", json=chat_data)
        print(f"✅ Chat API: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Chat API 실패: {e}")
    
    print("\n" + "="*50)
    
    # 4. Login API Test (이메일)
    try:
        login_data = {
            "email": "admin@eora.ai",
            "password": "admin123"
        }
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"✅ Login API (이메일): {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Login API (이메일) 실패: {e}")
    print("\n" + "="*50)
    
    # 5. Sessions API Test
    try:
        response = requests.get(f"{base_url}/api/sessions")
        print(f"✅ Sessions API: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Sessions API 실패: {e}")
    
    print("\n" + "="*50)
    
    # 6. Admin Users API Test
    try:
        response = requests.get(f"{base_url}/api/admin/users")
        print(f"✅ Admin Users API: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Admin Users API 실패: {e}")

if __name__ == "__main__":
    test_api() 