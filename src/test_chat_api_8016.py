#!/usr/bin/env python3
"""
포트 8016 채팅 API 테스트 스크립트
"""

import requests
import json
import time

def test_chat_api_8016():
    """포트 8016 채팅 API 테스트"""
    base_url = "http://localhost:8016"
    
    print("🔍 포트 8016 채팅 API 테스트 시작")
    print(f"🌐 서버 URL: {base_url}")
    print("=" * 50)
    
    # 1. 서버 상태 확인
    print("1️⃣ 서버 상태 확인")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        print(f"📊 상태 코드: {response.status_code}")
        print(f"📊 응답: {response.json()}")
    except Exception as e:
        print(f"❌ 서버 상태 확인 실패: {e}")
        return
    
    print("\n" + "=" * 50)
    
    # 2. 채팅 API 테스트
    print("2️⃣ 채팅 API 테스트")
    
    chat_data = {
        "message": "안녕하세요! 테스트 메시지입니다.",
        "session_id": "test_session_8016"
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
            json=chat_data,
            timeout=30
        )
        
        print(f"📥 응답 상태: {response.status_code}")
        print(f"📥 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ 응답 성공: {response_data}")
            print(f"💬 AI 응답: {response_data.get('response', '응답 없음')}")
        else:
            print(f"❌ 응답 실패: {response.text}")
            
    except Exception as e:
        print(f"💥 채팅 API 테스트 실패: {e}")
    
    print("\n" + "=" * 50)
    
    # 3. 채팅 페이지 접근 테스트
    print("3️⃣ 채팅 페이지 접근 테스트")
    try:
        response = requests.get(f"{base_url}/chat", timeout=5)
        print(f"📊 채팅 페이지 상태: {response.status_code}")
        if response.status_code == 200:
            print("✅ 채팅 페이지 접근 성공")
        else:
            print(f"❌ 채팅 페이지 접근 실패: {response.text}")
    except Exception as e:
        print(f"❌ 채팅 페이지 접근 실패: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 테스트 완료")

if __name__ == "__main__":
    test_chat_api_8016() 