#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
포인트 시스템 테스트 스크립트
수정된 포인트 시스템의 동작을 확인합니다.
"""

import sys
import os
import requests
import json
import time
from datetime import datetime

# 프로젝트 경로 추가
sys.path.append('src')

def test_point_system(server_url="http://localhost:8000"):
    """포인트 시스템 테스트 실행"""
    
    print("🧪 포인트 시스템 테스트 시작")
    print(f"🌐 서버 URL: {server_url}")
    print("=" * 50)
    
    # 테스트 계정 정보
    test_user = {
        "email": "test@eora.ai",
        "password": "test123",
        "name": "테스트사용자"
    }
    
    session = requests.Session()
    
    try:
        # 1. 회원가입 테스트
        print("1️⃣ 회원가입 테스트...")
        register_data = {
            "email": test_user["email"],
            "password": test_user["password"],
            "password_confirm": test_user["password"],
            "name": test_user["name"]
        }
        
        register_response = session.post(
            f"{server_url}/api/register",
            data=register_data
        )
        
        if register_response.status_code == 200:
            print("✅ 회원가입 성공")
        elif register_response.status_code == 409:
            print("ℹ️ 이미 존재하는 계정 (정상)")
        else:
            print(f"⚠️ 회원가입 응답: {register_response.status_code}")
        
        # 2. 로그인 테스트
        print("\n2️⃣ 로그인 테스트...")
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        login_response = session.post(
            f"{server_url}/api/login",
            data=login_data
        )
        
        if login_response.status_code == 200:
            print("✅ 로그인 성공")
            login_result = login_response.json()
            print(f"📧 사용자: {login_result.get('user', {}).get('email', 'Unknown')}")
        else:
            print(f"❌ 로그인 실패: {login_response.status_code}")
            print(f"❌ 응답: {login_response.text}")
            return
        
        # 3. 포인트 조회 테스트
        print("\n3️⃣ 포인트 조회 테스트...")
        points_response = session.get(f"{server_url}/api/user/points")
        
        if points_response.status_code == 200:
            points_data = points_response.json()
            current_points = points_data.get("points", 0)
            print(f"✅ 포인트 조회 성공")
            print(f"💰 현재 포인트: {current_points:,}포인트")
            
            # 10만 포인트인지 확인
            if current_points >= 100000:
                print("✅ 신규 사용자 10만 포인트 지급 확인됨")
            else:
                print(f"⚠️ 예상보다 적은 포인트: {current_points:,} (예상: 100,000)")
        else:
            print(f"❌ 포인트 조회 실패: {points_response.status_code}")
            return
        
        # 4. 채팅 테스트 (토큰 50% 추가 소비 확인)
        print("\n4️⃣ 채팅 테스트 (토큰 50% 추가 소비 확인)...")
        
        test_messages = [
            "안녕하세요!",
            "오늘 날씨가 어떤가요?",
            "파이썬 프로그래밍에 대해 간단히 설명해주세요."
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n📝 테스트 메시지 {i}: {message}")
            
            # 채팅 전 포인트 확인
            before_response = session.get(f"{server_url}/api/user/points")
            before_points = before_response.json().get("points", 0) if before_response.status_code == 200 else 0
            
            # 채팅 요청
            chat_data = {
                "message": message,
                "session_id": "test_session_" + str(int(time.time()))
            }
            
            chat_response = session.post(
                f"{server_url}/api/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"}
            )
            
            if chat_response.status_code == 200:
                chat_result = chat_response.json()
                print("✅ 채팅 성공")
                
                # 포인트 차감 정보 확인
                points_deducted = chat_result.get("points_deducted", 0)
                remaining_points = chat_result.get("remaining_points", 0)
                token_info = chat_result.get("token_info", {})
                
                print(f"💰 차감된 포인트: {points_deducted}포인트")
                print(f"💰 남은 포인트: {remaining_points:,}포인트")
                print(f"🔢 사용자 토큰: {token_info.get('user_tokens', 0)}")
                print(f"🔢 AI 응답 토큰: {token_info.get('ai_tokens', 0)}")
                print(f"🔢 총 토큰: {token_info.get('total_tokens', 0)}")
                
                # 50% 추가 소비 확인
                total_tokens = token_info.get('total_tokens', 0)
                expected_points = int(total_tokens * 1.5)  # 50% 추가
                actual_points = points_deducted
                
                if abs(expected_points - actual_points) <= 1:  # 반올림 오차 허용
                    print(f"✅ 토큰 50% 추가 소비 확인됨 (예상: {expected_points}, 실제: {actual_points})")
                else:
                    print(f"⚠️ 토큰 추가 소비 비율 확인 필요 (예상: {expected_points}, 실제: {actual_points})")
                
                # 채팅 후 포인트 확인
                after_response = session.get(f"{server_url}/api/user/points")
                after_points = after_response.json().get("points", 0) if after_response.status_code == 200 else 0
                
                actual_deduction = before_points - after_points
                print(f"💰 실제 차감: {before_points:,} → {after_points:,} (-{actual_deduction})")
                
            else:
                print(f"❌ 채팅 실패: {chat_response.status_code}")
                if chat_response.status_code == 402:
                    error_data = chat_response.json()
                    print(f"💰 포인트 부족: {error_data}")
                elif chat_response.status_code == 503:
                    error_data = chat_response.json()
                    print(f"🔧 서비스 장애: {error_data}")
                else:
                    print(f"❌ 오류 내용: {chat_response.text}")
            
            time.sleep(1)  # 요청 간격
        
        print("\n" + "=" * 50)
        print("🎉 포인트 시스템 테스트 완료!")
        
        # 최종 포인트 확인
        final_response = session.get(f"{server_url}/api/user/points")
        if final_response.status_code == 200:
            final_points = final_response.json().get("points", 0)
            print(f"💰 최종 포인트: {final_points:,}포인트")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

def test_token_calculator():
    """토큰 계산기 테스트"""
    
    print("\n🧮 토큰 계산기 테스트")
    print("=" * 30)
    
    try:
        from token_calculator import TokenCalculator
        
        calculator = TokenCalculator()
        
        # 테스트 메시지들
        test_cases = [
            "안녕하세요!",
            "오늘 날씨가 어떤가요?",
            "파이썬 프로그래밍에 대해 자세히 설명해주세요. 특히 객체지향 프로그래밍의 장점과 단점을 포함해서 설명해주시면 감사하겠습니다."
        ]
        
        for i, message in enumerate(test_cases, 1):
            print(f"\n📝 테스트 케이스 {i}: {message}")
            
            # 토큰 수 계산
            tokens = calculator.count_tokens(message)
            print(f"🔢 토큰 수: {tokens}")
            
            # 메시지 비용 계산
            cost_info = calculator.calculate_message_cost(message)
            print(f"💰 예상 포인트: {cost_info['points_to_deduct']}")
            print(f"🔢 총 예상 토큰: {cost_info['total_estimated_tokens']}")
            
            # 50% 추가 확인
            expected_with_50_percent = int(cost_info['total_estimated_tokens'] * 1.5)
            print(f"✅ 50% 추가 계산: {cost_info['total_estimated_tokens']} × 1.5 = {expected_with_50_percent}")
        
        print("\n✅ 토큰 계산기 테스트 완료!")
        
    except ImportError as e:
        print(f"❌ 토큰 계산기 import 실패: {e}")
    except Exception as e:
        print(f"❌ 토큰 계산기 테스트 오류: {e}")

if __name__ == "__main__":
    print("🚀 EORA AI 포인트 시스템 종합 테스트")
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 토큰 계산기 테스트
    test_token_calculator()
    
    # 서버 연결 테스트
    server_url = "http://localhost:8000"
    
    try:
        # 서버 상태 확인
        response = requests.get(f"{server_url}/", timeout=5)
        if response.status_code == 200:
            print(f"✅ 서버 연결 확인: {server_url}")
            test_point_system(server_url)
        else:
            print(f"⚠️ 서버 응답 이상: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ 서버 연결 실패: {server_url}")
        print("💡 서버를 먼저 시작해주세요: python src/app.py")
    except Exception as e:
        print(f"❌ 서버 확인 중 오류: {e}")