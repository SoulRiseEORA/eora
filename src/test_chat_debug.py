#!/usr/bin/env python3
"""
채팅 API 디버그 테스트 스크립트
"""

import requests
import json
import time

def test_chat_api():
    """채팅 API 테스트"""
    print("🧪 채팅 API 디버그 테스트")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8001"
    
    # 테스트 메시지들
    test_messages = [
        "hi",
        "hihi", 
        "안녕하세요",
        "오늘 날씨가 어때요?",
        "인공지능에 대해 어떻게 생각하세요?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 테스트 {i}: '{message}'")
        print("-" * 30)
        
        try:
            # 채팅 API 호출
            response = requests.post(
                f"{base_url}/api/chat",
                json={
                    "message": message,
                    "session_id": "test_session"
                },
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📤 요청 메시지: {message}")
            print(f"📥 응답 상태: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("response", "")
                print(f"🤖 AI 응답: {ai_response}")
                
                # 에코 여부 확인
                if ai_response.lower() == message.lower():
                    print("❌ 에코 감지: AI가 사용자 메시지를 그대로 반복함")
                elif message.lower() in ai_response.lower():
                    print("⚠️ 부분 에코 감지: 사용자 메시지가 AI 응답에 포함됨")
                else:
                    print("✅ 정상 응답: 에코 없음")
            else:
                print(f"❌ API 오류: {response.status_code}")
                print(f"❌ 오류 내용: {response.text}")
                
        except Exception as e:
            print(f"💥 테스트 오류: {e}")
        
        time.sleep(1)  # API 호출 간격
    
    print("\n" + "=" * 50)
    print("🏁 테스트 완료")

if __name__ == "__main__":
    test_chat_api() 