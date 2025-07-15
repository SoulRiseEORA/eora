import requests
import json

def test_login():
    url = "http://127.0.0.1:8001/api/auth/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=== 로그인 API 테스트 ===")
    success = test_login()
    if success:
        print("✅ 로그인 테스트 성공!")
    else:
        print("❌ 로그인 테스트 실패!") 