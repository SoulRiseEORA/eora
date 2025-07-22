import requests
import json

def test_api():
    base_url = "http://127.0.0.1:8001"
    
    # 1. 헬스 체크
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health Check: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 2. API 상태 확인
    try:
        response = requests.get(f"{base_url}/api/status")
        print(f"✅ API Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ API Status Failed: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 3. 환경변수 확인
    try:
        response = requests.get(f"{base_url}/api/env-check")
        print(f"✅ Environment Check: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Environment Check Failed: {e}")

if __name__ == "__main__":
    test_api() 