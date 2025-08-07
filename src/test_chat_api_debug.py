#!/usr/bin/env python3
"""
채팅 API 디버깅 테스트 스크립트
"""

import requests
import json
import time

def test_chat_api():
    """채팅 API 테스트"""
    base_url = "http://localhost:8013"
    
    print("🔍 채팅 API 디버깅 테스트 시작")
    print(f"🌐 서버 URL: {base_url}")
    print("=" * 50)
    
    # 1. 서버 상태 확인
    print("1️⃣ 서버 상태 확인")
    try:
        response = requests.get(f"{base_url}/api/status")
        print(f"📊 상태 코드: {response.status_code}")
        print(f"📊 응답: {response.json()}")
    except Exception as e:
        print(f"❌ 서버 상태 확인 실패: {e}")
        return
    
    print("\n" + "=" * 50)
    
    # 2. 채팅 API 테스트 (익명 사용자)
    print("2️⃣ 채팅 API 테스트 (익명 사용자)")
    
    chat_data = {
        "message": "안녕하세요! 테스트 메시지입니다.",
        "session_id": "test_session_001"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"📤 요청 데이터: {chat_data}")
        print(f"📤 요청 헤더: {headers}")
        
        response = requests.post(
            f"{base_url}/api/chat",
            headers=headers,
            json=chat_data
        )
        
        print(f"📥 응답 상태: {response.status_code}")
        print(f"📥 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ 응답 성공: {response_data}")
        else:
            print(f"❌ 응답 실패: {response.text}")
            
    except Exception as e:
        print(f"💥 채팅 API 테스트 실패: {e}")
    
    print("\n" + "=" * 50)
    
    # 3. 채팅 API 테스트 (토큰 없음)
    print("3️⃣ 채팅 API 테스트 (토큰 없음)")
    
    chat_data2 = {
        "message": "두 번째 테스트 메시지입니다.",
        "session_id": "test_session_002"
    }
    
    try:
        print(f"📤 요청 데이터: {chat_data2}")
        
        response = requests.post(
            f"{base_url}/api/chat",
            headers=headers,
            json=chat_data2
        )
        
        print(f"📥 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ 응답 성공: {response_data}")
        else:
            print(f"❌ 응답 실패: {response.text}")
            
    except Exception as e:
        print(f"💥 채팅 API 테스트 실패: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 테스트 완료")

if __name__ == "__main__":
    test_chat_api() 