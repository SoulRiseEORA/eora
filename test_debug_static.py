#!/usr/bin/env python3
"""
정적 파일 디버깅 테스트 스크립트
"""

import requests
import json

def test_debug_static():
    """정적 파일 디버깅 정보 확인"""
    base_url = "http://localhost:8017"
    
    print("🔍 정적 파일 디버깅 테스트")
    print(f"🌐 서버 URL: {base_url}")
    print("=" * 50)
    
    # 1. 디버깅 정보 확인
    print("1️⃣ 디버깅 정보 확인")
    try:
        response = requests.get(f"{base_url}/debug/static")
        print(f"📊 상태 코드: {response.status_code}")
        print(f"📊 응답: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"❌ 디버깅 정보 확인 실패: {e}")
        return
    
    print("\n" + "=" * 50)
    
    # 2. 정적 파일 직접 접근 테스트
    print("2️⃣ 정적 파일 직접 접근 테스트")
    
    test_urls = [
        f"{base_url}/static/test_chat_simple.html",
        f"{base_url}/static/style.css",
        f"{base_url}/test_chat_simple.html"  # 잘못된 경로
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url)
            print(f"📊 {url}")
            print(f"   상태 코드: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ 성공 - 파일 크기: {len(response.content)} bytes")
            else:
                print(f"   ❌ 실패")
        except Exception as e:
            print(f"   ❌ 오류: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_debug_static() 