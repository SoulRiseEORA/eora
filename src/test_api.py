#!/usr/bin/env python3
"""
API 상태 테스트 스크립트
"""

import requests
import json

def test_api():
    """API 상태를 테스트합니다."""
    base_url = "http://127.0.0.1:8081"
    
    try:
        # 상태 API 테스트
        print("🔍 API 상태 확인 중...")
        response = requests.get(f"{base_url}/api/status", timeout=5)
        
        if response.status_code == 200:
            print("✅ API 상태 정상")
            print(f"📊 응답: {response.json()}")
        else:
            print(f"❌ API 오류: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")

if __name__ == "__main__":
    test_api() 