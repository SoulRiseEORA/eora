#!/usr/bin/env python3
"""
회상 시스템 테스트 스크립트 - API 키 없이도 작동
"""

import requests
import json

def test_recall_system():
    """회상 시스템 테스트"""
    print("=== 회상 시스템 테스트 ===")
    
    # 서버 URL
    base_url = "http://127.0.0.1:8001"
    
    # 테스트할 회상 타입들
    recall_types = ["normal", "window", "wisdom", "intuition"]
    
    for recall_type in recall_types:
        print(f"\n--- {recall_type} 회상 테스트 ---")
        
        try:
            # 회상 API 호출
            response = requests.get(
                f"{base_url}/api/aura/recall",
                params={"query": "테스트 질문", "recall_type": recall_type}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {recall_type} 회상 성공")
                print(f"응답: {data}")
            else:
                print(f"❌ {recall_type} 회상 실패: {response.status_code}")
                print(f"응답: {response.text}")
                
        except Exception as e:
            print(f"❌ {recall_type} 회상 오류: {e}")
    
    # 채팅 API 테스트 (API 키 없이도 기본 응답)
    print(f"\n--- 채팅 API 테스트 ---")
    
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json={
                "message": "안녕하세요",
                "user_id": "test_user",
                "recall_type": "normal"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 채팅 API 성공")
            print(f"응답: {data}")
        else:
            print(f"❌ 채팅 API 실패: {response.status_code}")
            print(f"응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 채팅 API 오류: {e}")

if __name__ == "__main__":
    test_recall_system() 