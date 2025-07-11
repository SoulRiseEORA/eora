import requests
import json

def test_admin_apis():
    base_url = "http://127.0.0.1:8001"
    
    # 1. 관리자 사용자 목록 조회
    print("=== 관리자 사용자 목록 조회 테스트 ===")
    try:
        response = requests.get(f"{base_url}/api/admin/users")
        print(f"Admin Users Status: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            print(f"Found {len(users)} users")
            for user in users:
                print(f"  - {user.get('username', 'Unknown')} (Admin: {user.get('is_admin', False)})")
        else:
            print(f"Admin Users Error: {response.text}")
            return False
    except Exception as e:
        print(f"Admin Users Error: {e}")
        return False
    
    # 2. 시스템 상태 조회
    print("\n=== 시스템 상태 조회 테스트 ===")
    try:
        response = requests.get(f"{base_url}/api/status")
        print(f"System Status: {response.status_code}")
        if response.status_code == 200:
            status = response.json()
            print(f"Database Available: {status.get('database_available', False)}")
            print(f"OpenAI Available: {status.get('openai_available', False)}")
            print(f"EORA Systems: {status.get('eora_systems', {})}")
        else:
            print(f"System Status Error: {response.text}")
    except Exception as e:
        print(f"System Status Error: {e}")
    
    return True

if __name__ == "__main__":
    print("=== 관리자 API 테스트 ===")
    success = test_admin_apis()
    if success:
        print("\n✅ 관리자 API 테스트 성공!")
    else:
        print("\n❌ 관리자 API 테스트 실패!") 