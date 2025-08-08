#!/usr/bin/env python3
"""
종합 테스트 스크립트 - 포인트 시스템, 회상 시스템, 토큰 계산
"""

import requests
import json
import time

def test_comprehensive():
    """종합 테스트"""
    print("=== EORA AI System 종합 테스트 ===")
    
    # 서버 URL
    base_url = "http://127.0.0.1:8001"
    
    # 1. 사용자 포인트 확인
    print("\n--- 1. 사용자 포인트 확인 ---")
    try:
        response = requests.get(f"{base_url}/api/user/points")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 포인트 조회 성공: {data}")
        else:
            print(f"❌ 포인트 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 포인트 조회 오류: {e}")
    
    # 2. 회상 시스템 테스트
    print("\n--- 2. 회상 시스템 테스트 ---")
    recall_types = ["normal", "window", "wisdom", "intuition"]
    
    for recall_type in recall_types:
        try:
            response = requests.post(
                f"{base_url}/api/chat",
                json={
                    "message": f"테스트 메시지 - {recall_type} 회상",
                    "user_id": "test_user",
                    "recall_type": recall_type
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {recall_type} 회상 성공")
                print(f"   응답: {data.get('response', 'N/A')[:50]}...")
                print(f"   토큰 정보: {data.get('token_info', 'N/A')}")
            else:
                print(f"❌ {recall_type} 회상 실패: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {recall_type} 회상 오류: {e}")
    
    # 3. 포인트 차감 테스트
    print("\n--- 3. 포인트 차감 테스트 ---")
    try:
        # 첫 번째 메시지 전송
        response1 = requests.post(
            f"{base_url}/api/chat",
            json={
                "message": "첫 번째 테스트 메시지",
                "user_id": "test_user",
                "recall_type": "normal"
            }
        )
        
        if response1.status_code == 200:
            data1 = response1.json()
            print(f"✅ 첫 번째 메시지 성공")
            print(f"   토큰 정보: {data1.get('token_info', 'N/A')}")
        
        # 잠시 대기
        time.sleep(1)
        
        # 두 번째 메시지 전송
        response2 = requests.post(
            f"{base_url}/api/chat",
            json={
                "message": "두 번째 테스트 메시지",
                "user_id": "test_user",
                "recall_type": "wisdom"
            }
        )
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"✅ 두 번째 메시지 성공")
            print(f"   토큰 정보: {data2.get('token_info', 'N/A')}")
        
        # 최종 포인트 확인
        response_points = requests.get(f"{base_url}/api/user/points")
        if response_points.status_code == 200:
            final_points = response_points.json()
            print(f"✅ 최종 포인트: {final_points}")
            
    except Exception as e:
        print(f"❌ 포인트 차감 테스트 오류: {e}")
    
    # 4. 아우라 메모리 시스템 테스트
    print("\n--- 4. 아우라 메모리 시스템 테스트 ---")
    try:
        response = requests.get(f"{base_url}/api/aura/memory")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 아우라 메모리 조회 성공")
            print(f"   메모리 수: {len(data.get('memories', []))}")
        else:
            print(f"❌ 아우라 메모리 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 아우라 메모리 테스트 오류: {e}")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    test_comprehensive() 