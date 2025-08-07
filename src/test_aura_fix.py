import requests
import time

def test_aura_page():
    """AURA 시스템 페이지 연결 테스트"""
    base_url = "http://127.0.0.1:8001"
    
    # 서버가 시작될 때까지 잠시 대기
    print("서버 시작 대기 중...")
    time.sleep(3)
    
    try:
        # 홈페이지 테스트
        print("홈페이지 테스트...")
        response = requests.get(f"{base_url}/")
        print(f"홈페이지 상태: {response.status_code}")
        
        # AURA 시스템 페이지 테스트
        print("AURA 시스템 페이지 테스트...")
        response = requests.get(f"{base_url}/aura_system")
        print(f"AURA 페이지 상태: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ AURA 시스템 페이지가 정상적으로 로드됩니다!")
            print(f"페이지 크기: {len(response.text)} 문자")
        else:
            print(f"❌ AURA 페이지 오류: {response.status_code}")
            print(f"응답 내용: {response.text}")
            
        # 헬스 체크 테스트
        print("헬스 체크 테스트...")
        response = requests.get(f"{base_url}/health")
        print(f"헬스 체크 상태: {response.status_code}")
        if response.status_code == 200:
            print(f"서버 정보: {response.json()}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    test_aura_page() 