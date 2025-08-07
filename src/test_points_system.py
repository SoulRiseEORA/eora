#!/usr/bin/env python3
"""
포인트 시스템 전용 테스트 스크립트
"""

import requests
import json
import time

def test_points_system():
    """포인트 시스템 테스트"""
    print("=== 포인트 시스템 전용 테스트 ===")
    
    # 서버 URL
    base_url = "http://127.0.0.1:8001"
    
    # 1. 초기 포인트 확인
    print("\n--- 1. 초기 포인트 확인 ---")
    try:
        response = requests.get(f"{base_url}/api/user/points")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 초기 포인트: {data}")
            initial_points = data.get("points", 0)
        else:
            print(f"❌ 포인트 조회 실패: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 포인트 조회 오류: {e}")
        return
    
    # 2. 첫 번째 메시지 전송 (포인트 차감 테스트)
    print(f"\n--- 2. 첫 번째 메시지 전송 ---")
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json={
                "message": "안녕하세요! 포인트 시스템 테스트입니다.",
                "user_id": "test_user",
                "recall_type": "normal"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 첫 번째 메시지 성공")
            print(f"   응답: {data.get('response', 'N/A')[:50]}...")
            print(f"   토큰 정보: {data.get('token_info', 'N/A')}")
            
            # 토큰 정보 확인
            token_info = data.get('token_info', {})
            if isinstance(token_info, dict):
                print(f"   사용자 토큰: {token_info.get('user_tokens', 0)}")
                print(f"   프롬프트 토큰: {token_info.get('prompt_tokens', 0)}")
                print(f"   회상 토큰: {token_info.get('recall_tokens', 0)}")
                print(f"   총 토큰: {token_info.get('total_tokens', 0)}")
                print(f"   차감 포인트: {token_info.get('points_deducted', 0)}")
                print(f"   남은 포인트: {token_info.get('remaining_points', 0)}")
        else:
            print(f"❌ 첫 번째 메시지 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 첫 번째 메시지 오류: {e}")
    
    # 3. 잠시 대기
    time.sleep(1)
    
    # 4. 두 번째 메시지 전송 (추가 차감 테스트)
    print(f"\n--- 3. 두 번째 메시지 전송 ---")
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json={
                "message": "두 번째 메시지입니다. 포인트가 계속 차감되는지 확인해보겠습니다.",
                "user_id": "test_user",
                "recall_type": "wisdom"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 두 번째 메시지 성공")
            print(f"   응답: {data.get('response', 'N/A')[:50]}...")
            print(f"   토큰 정보: {data.get('token_info', 'N/A')}")
            
            # 토큰 정보 확인
            token_info = data.get('token_info', {})
            if isinstance(token_info, dict):
                print(f"   사용자 토큰: {token_info.get('user_tokens', 0)}")
                print(f"   프롬프트 토큰: {token_info.get('prompt_tokens', 0)}")
                print(f"   회상 토큰: {token_info.get('recall_tokens', 0)}")
                print(f"   총 토큰: {token_info.get('total_tokens', 0)}")
                print(f"   차감 포인트: {token_info.get('points_deducted', 0)}")
                print(f"   남은 포인트: {token_info.get('remaining_points', 0)}")
        else:
            print(f"❌ 두 번째 메시지 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 두 번째 메시지 오류: {e}")
    
    # 5. 최종 포인트 확인
    print(f"\n--- 4. 최종 포인트 확인 ---")
    try:
        response = requests.get(f"{base_url}/api/user/points")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 최종 포인트: {data}")
            final_points = data.get("points", 0)
            
            # 포인트 변화 확인
            points_change = initial_points - final_points
            print(f"📊 포인트 변화: {initial_points} → {final_points} (차감: {points_change})")
            
            if points_change > 0:
                print(f"✅ 포인트 차감이 정상적으로 작동했습니다!")
            else:
                print(f"⚠️ 포인트 차감이 작동하지 않았습니다.")
        else:
            print(f"❌ 최종 포인트 조회 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 최종 포인트 조회 오류: {e}")
    
    print("\n=== 포인트 시스템 테스트 완료 ===")

if __name__ == "__main__":
    test_points_system() 