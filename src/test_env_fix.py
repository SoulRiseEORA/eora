import requests
import json
import time

def test_environment_fix():
    base_url = "http://127.0.0.1:8001"
    
    print("=== 환경변수 수정 후 API 테스트 ===")
    
    # 1. 서버 상태 확인
    print("\n1. 서버 상태 확인...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ 서버 정상 실행")
        else:
            print("   ❌ 서버 오류")
            return False
    except Exception as e:
        print(f"   ❌ 서버 연결 실패: {e}")
        return False
    
    # 2. 시스템 상태 확인
    print("\n2. 시스템 상태 확인...")
    try:
        response = requests.get(f"{base_url}/api/status")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 시스템 상태: {data.get('status', 'Unknown')}")
            print(f"   ✅ DB 연결: {data.get('database_connected', False)}")
            print(f"   ✅ OpenAI API: {data.get('openai_available', False)}")
        else:
            print("   ❌ 시스템 상태 조회 실패")
    except Exception as e:
        print(f"   ❌ 시스템 상태 조회 오류: {e}")
    
    # 3. 로그인 테스트
    print("\n3. 관리자 로그인 테스트...")
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("   ✅ 로그인 성공")
            print(f"   ✅ 사용자: {data.get('username', 'Unknown')}")
            print(f"   ✅ 관리자 권한: {data.get('is_admin', False)}")
        else:
            print("   ❌ 로그인 실패")
            print(f"   오류: {response.text}")
    except Exception as e:
        print(f"   ❌ 로그인 테스트 오류: {e}")
    
    # 4. 채팅 API 테스트
    print("\n4. 채팅 API 테스트...")
    try:
        chat_data = {
            "message": "안녕하세요! 테스트 메시지입니다.",
            "session_id": "test_session_001",
            "user_id": "test_user_001"
        }
        response = requests.post(f"{base_url}/api/chat", json=chat_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("   ✅ 채팅 API 정상")
            print(f"   ✅ 응답: {data.get('response', 'No response')[:100]}...")
            print(f"   ✅ GPT 응답 여부: {'GPT' in str(data.get('response', ''))}")
        else:
            print("   ❌ 채팅 API 실패")
            print(f"   오류: {response.text}")
    except Exception as e:
        print(f"   ❌ 채팅 API 테스트 오류: {e}")
    
    # 5. 세션 API 테스트
    print("\n5. 세션 API 테스트...")
    try:
        # 세션 생성
        session_data = {
            "user_id": "test_user_001",
            "session_name": "테스트 세션"
        }
        response = requests.post(f"{base_url}/api/sessions", json=session_data)
        print(f"   세션 생성 Status: {response.status_code}")
        
        # 세션 목록 조회
        response = requests.get(f"{base_url}/api/sessions")
        print(f"   세션 목록 Status: {response.status_code}")
        if response.status_code == 200:
            sessions = response.json()
            print(f"   ✅ 세션 개수: {len(sessions)}")
        else:
            print("   ❌ 세션 목록 조회 실패")
    except Exception as e:
        print(f"   ❌ 세션 API 테스트 오류: {e}")
    
    print("\n=== 테스트 완료 ===")
    return True

if __name__ == "__main__":
    # 서버 시작 대기
    print("서버 시작 대기 중... (5초)")
    time.sleep(5)
    test_environment_fix() 