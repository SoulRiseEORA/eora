import requests
import time
import json

def check_railway_status():
    """Railway 애플리케이션 상태를 빠르게 확인하는 함수"""
    
    # Railway에서 제공하는 URL (실제 배포 후 URL로 변경 필요)
    # 예: https://your-app-name.railway.app
    base_url = "https://www.eora.life"  # 실제 URL로 변경하세요
    
    endpoints = [
        ("/", "메인 페이지"),
        ("/health", "헬스 체크"),
        ("/docs", "API 문서")
    ]
    
    print("🚂 Railway 상태 확인 중...")
    print("=" * 50)
    
    for endpoint, description in endpoints:
        try:
            url = base_url + endpoint
            start_time = time.time()
            response = requests.get(url, timeout=10)
            end_time = time.time()
            
            status = "✅" if response.status_code == 200 else "❌"
            response_time = round((end_time - start_time) * 1000, 2)
            
            print(f"{status} {description}: {response.status_code} ({response_time}ms)")
            
            if endpoint == "/health" and response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   📊 상태: {data.get('status', 'unknown')}")
                except:
                    pass
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ {description}: 연결 실패 - {str(e)}")
        except Exception as e:
            print(f"❌ {description}: 오류 - {str(e)}")
    
    print("=" * 50)
    print("💡 팁: 실제 Railway URL로 base_url을 변경하세요!")

if __name__ == "__main__":
    check_railway_status() 