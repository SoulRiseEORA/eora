#!/usr/bin/env python3
"""
초고속 응답 테스트 스크립트
"""

import requests
import json
import time
import statistics

def test_speed_optimized():
    """초고속 응답 테스트"""
    base_url = "http://localhost:8016"
    
    print("🚀 초고속 응답 테스트 시작")
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
    
    # 2. 빠른 응답 테스트 (프리로드 응답)
    fast_messages = ["hi", "hello", "안녕", "반가워", "테스트", "test"]
    
    fast_times = []
    for message in fast_messages:
        print(f"📝 테스트: {message}")
        
        chat_data = {
            "message": message,
            "session_id": f"speed_test_{message}"
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
                timeout=10
            )
            end_time = time.time()
            response_time = end_time - start_time
            fast_times.append(response_time)
            
            print(f"📥 응답 상태: {response.status_code}")
            print(f"⏱️ 응답 시간: {response_time:.3f}초")
            
            if response.status_code == 200:
                response_data = response.json()
                ai_response = response_data.get('response', '응답 없음')
                print(f"✅ 응답: {ai_response[:50]}...")
                
                if response_time < 0.1:
                    print("⚡ 초고속 응답! (0.1초 미만)")
                elif response_time < 0.5:
                    print("🚀 고속 응답! (0.5초 미만)")
                else:
                    print("⚠️ 일반 응답")
            else:
                print(f"❌ 응답 실패: {response.text}")
                
        except Exception as e:
            print(f"💥 테스트 실패: {e}")
        
        print("-" * 30)
    
    print("\n" + "=" * 50)
    
    # 3. 일반 응답 테스트
    print("3️⃣ 일반 응답 테스트 (GPT-4o API)")
    normal_messages = [
        "오늘 날씨는 어때요?",
        "파이썬 프로그래밍을 배우고 싶어요",
        "인공지능에 대해 설명해주세요"
    ]
    
    normal_times = []
    for message in normal_messages:
        print(f"📝 테스트: {message}")
        
        chat_data = {
            "message": message,
            "session_id": f"normal_test_{len(normal_times)}"
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
                timeout=15
            )
            end_time = time.time()
            response_time = end_time - start_time
            normal_times.append(response_time)
            
            print(f"📥 응답 상태: {response.status_code}")
            print(f"⏱️ 응답 시간: {response_time:.3f}초")
            
            if response.status_code == 200:
                response_data = response.json()
                ai_response = response_data.get('response', '응답 없음')
                print(f"✅ 응답: {ai_response[:50]}...")
                
                if response_time < 1.0:
                    print("🚀 빠른 응답! (1초 미만)")
                elif response_time < 3.0:
                    print("✅ 일반 응답! (3초 미만)")
                else:
                    print("⚠️ 느린 응답")
            else:
                print(f"❌ 응답 실패: {response.text}")
                
        except Exception as e:
            print(f"💥 테스트 실패: {e}")
        
        print("-" * 30)
    
    print("\n" + "=" * 50)
    
    # 4. 통계 결과
    print("4️⃣ 성능 통계")
    if fast_times:
        print(f"⚡ 프리로드 응답:")
        print(f"  - 평균: {statistics.mean(fast_times):.3f}초")
        print(f"  - 최소: {min(fast_times):.3f}초")
        print(f"  - 최대: {max(fast_times):.3f}초")
    
    if normal_times:
        print(f"🤖 GPT-4o API 응답:")
        print(f"  - 평균: {statistics.mean(normal_times):.3f}초")
        print(f"  - 최소: {min(normal_times):.3f}초")
        print(f"  - 최대: {max(normal_times):.3f}초")
    
    # 5. 성능 평가
    print("\n5️⃣ 성능 평가")
    if fast_times and statistics.mean(fast_times) < 0.1:
        print("🎉 프리로드 응답: 초고속 성능 달성!")
    elif fast_times and statistics.mean(fast_times) < 0.5:
        print("✅ 프리로드 응답: 고속 성능 달성!")
    
    if normal_times and statistics.mean(normal_times) < 1.0:
        print("🚀 GPT-4o API: 초고속 성능 달성!")
    elif normal_times and statistics.mean(normal_times) < 3.0:
        print("✅ GPT-4o API: 고속 성능 달성!")
    else:
        print("⚠️ 추가 최적화 필요")
    
    print("\n" + "=" * 50)
    print("🏁 테스트 완료")

if __name__ == "__main__":
    test_speed_optimized() 