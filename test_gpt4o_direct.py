#!/usr/bin/env python3
"""
GPT-4o API 직접 호출 테스트
"""

import requests
import json
import time

def test_gpt4o_direct():
    """GPT-4o API 직접 호출 테스트"""
    base_url = "http://localhost:8016"
    
    print("🚀 GPT-4o API 직접 호출 테스트 시작")
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
    
    # 2. 다양한 메시지로 GPT-4o 테스트
    test_messages = [
        "안녕하세요!",
        "오늘 날씨는 어때요?",
        "인공지능에 대해 설명해주세요",
        "파이썬 프로그래밍을 배우고 싶어요",
        "테스트 메시지입니다"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"2️⃣ 테스트 {i}: {message}")
        
        chat_data = {
            "message": message,
            "session_id": f"test_session_{i}"
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/api/chat",
                headers=headers,
                json=chat_data,
                timeout=30
            )
            end_time = time.time()
            response_time = end_time - start_time
            
            print(f"📥 응답 상태: {response.status_code}")
            print(f"⏱️ 응답 시간: {response_time:.2f}초")
            
            if response.status_code == 200:
                response_data = response.json()
                ai_response = response_data.get('response', '응답 없음')
                print(f"✅ GPT-4o 응답: {ai_response[:100]}...")
                
                # 응답이 다양하고 의미있는지 확인
                if len(ai_response) > 20 and "💭 흥미로운 이야기네요" not in ai_response:
                    print("🎉 GPT-4o API가 정상적으로 작동하고 있습니다!")
                else:
                    print("⚠️ 폴백 응답이 사용되고 있습니다.")
            else:
                print(f"❌ 응답 실패: {response.text}")
                
        except Exception as e:
            print(f"💥 테스트 {i} 실패: {e}")
        
        print("-" * 30)
    
    print("\n" + "=" * 50)
    print("🏁 테스트 완료")

if __name__ == "__main__":
    test_gpt4o_direct() 