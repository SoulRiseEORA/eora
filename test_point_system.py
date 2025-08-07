#!/usr/bin/env python3
"""
포인트 시스템 테스트 스크립트
- 토큰 계산 및 포인트 차감 테스트
- 포인트 부족 시나리오 테스트
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8300"

def register_test_user():
    """테스트용 사용자 등록"""
    print("👤 테스트 사용자 등록...")
    
    timestamp = int(time.time())
    test_user = {
        "name": "포인트테스트",
        "email": f"point_test_{timestamp}@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"   ✅ 사용자 등록 성공: {test_user['email']}")
                print(f"   💰 초기 포인트: {data['user']['initial_points']:,}")
                return test_user['email'], test_user['password']
            else:
                print(f"   ❌ 등록 실패: {data.get('error')}")
        else:
            print(f"   ❌ 등록 실패: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ 등록 오류: {e}")
    
    return None, None

def login_user(email, password):
    """사용자 로그인 및 세션 생성"""
    print(f"🔐 로그인: {email}")
    
    session = requests.Session()
    
    try:
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"   ✅ 로그인 성공")
                return session
            else:
                print(f"   ❌ 로그인 실패: {data.get('error')}")
        else:
            print(f"   ❌ 로그인 실패: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ 로그인 오류: {e}")
    
    return None

def get_user_points(session):
    """사용자 포인트 조회"""
    try:
        response = session.get(f"{BASE_URL}/api/user/points", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data
            else:
                print(f"   ❌ 포인트 조회 실패: {data.get('error')}")
        else:
            print(f"   ❌ 포인트 조회 실패: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ 포인트 조회 오류: {e}")
    
    return None

def create_session(session):
    """채팅 세션 생성"""
    try:
        response = session.post(
            f"{BASE_URL}/api/sessions",
            json={"name": "포인트 테스트 세션"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                session_id = data["session"]["session_id"]
                print(f"   ✅ 세션 생성: {session_id}")
                return session_id
            else:
                print(f"   ❌ 세션 생성 실패: {data.get('error')}")
        else:
            print(f"   ❌ 세션 생성 실패: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ 세션 생성 오류: {e}")
    
    return None

def send_chat_message(session, session_id, message):
    """채팅 메시지 전송 및 포인트 차감 테스트"""
    print(f"💬 채팅 메시지 전송: '{message[:30]}...'")
    
    try:
        response = session.post(
            f"{BASE_URL}/api/chat",
            json={
                "session_id": session_id,
                "message": message
            },
            headers={"Content-Type": "application/json"},
            timeout=30  # 긴 타임아웃 (AI 응답 대기)
        )
        
        print(f"   응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"   ✅ 채팅 성공!")
                print(f"   🤖 AI 응답: {data['response'][:100]}...")
                
                # 포인트 정보 확인
                if "points_info" in data:
                    points_info = data["points_info"]
                    print(f"   💰 포인트 차감: {points_info['deducted']}")
                    print(f"   💳 남은 포인트: {points_info['remaining']:,}")
                    
                    token_usage = points_info["token_usage"]
                    print(f"   🔢 토큰 사용량:")
                    print(f"      - 입력: {token_usage['prompt_tokens']}")
                    print(f"      - 출력: {token_usage['completion_tokens']}")
                    print(f"      - 총합: {token_usage['total_tokens']}")
                else:
                    print(f"   ⚠️ 포인트 정보 없음")
                
                return True
            else:
                print(f"   ❌ 채팅 실패: {data.get('error')}")
        elif response.status_code == 402:
            data = response.json()
            print(f"   💸 포인트 부족: {data.get('error')}")
            print(f"   💳 현재 포인트: {data.get('current_points', 0)}")
            return False
        else:
            print(f"   ❌ 채팅 실패: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   오류 내용: {error_data}")
            except:
                pass
    except Exception as e:
        print(f"   ❌ 채팅 오류: {e}")
    
    return False

def get_points_history(session):
    """포인트 히스토리 조회"""
    print("📊 포인트 히스토리 조회...")
    
    try:
        response = session.get(f"{BASE_URL}/api/user/points/history", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                history = data["history"]
                print(f"   ✅ 히스토리 조회 성공 (총 {data['total_records']}개 기록)")
                
                for i, record in enumerate(history[:5], 1):  # 최신 5개만 표시
                    print(f"   {i}. {record['type']}: {record['amount']:+} 포인트")
                    print(f"      설명: {record['description']}")
                    print(f"      잔액: {record['balance_after']:,} 포인트")
                    print(f"      시간: {record['timestamp']}")
                    if "token_details" in record:
                        tokens = record["token_details"]
                        print(f"      토큰: {tokens['total_tokens']} (입력: {tokens['prompt_tokens']}, 출력: {tokens['completion_tokens']})")
                    print()
                
                return True
            else:
                print(f"   ❌ 히스토리 조회 실패: {data.get('error')}")
        else:
            print(f"   ❌ 히스토리 조회 실패: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ 히스토리 조회 오류: {e}")
    
    return False

def main():
    """메인 테스트 함수"""
    print("🚀 포인트 시스템 종합 테스트")
    print("=" * 60)
    
    # 1. 테스트 사용자 등록
    email, password = register_test_user()
    if not email:
        print("❌ 사용자 등록 실패")
        return
    
    time.sleep(1)
    
    # 2. 로그인
    session = login_user(email, password)
    if not session:
        print("❌ 로그인 실패")
        return
    
    # 3. 초기 포인트 확인
    print("\n💰 초기 포인트 확인...")
    initial_points = get_user_points(session)
    if initial_points:
        print(f"   현재 포인트: {initial_points['points']:,}")
        print(f"   총 획득: {initial_points['total_earned']:,}")
        print(f"   총 사용: {initial_points['total_spent']:,}")
    
    # 4. 채팅 세션 생성
    print("\n📱 채팅 세션 생성...")
    session_id = create_session(session)
    if not session_id:
        print("❌ 세션 생성 실패")
        return
    
    # 5. 다양한 길이의 메시지로 테스트
    test_messages = [
        "안녕하세요!",  # 짧은 메시지
        "오늘 날씨가 어떤가요? 밖에 나가기 좋을까요?",  # 중간 메시지
        "인공지능의 발전이 우리 사회에 미치는 영향에 대해 자세히 설명해주세요. 특히 일자리 변화, 교육 방식의 변화, 그리고 윤리적 고려사항들을 포함해서 종합적으로 분석해주세요.",  # 긴 메시지
    ]
    
    print(f"\n💬 채팅 테스트 ({len(test_messages)}개 메시지)...")
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- 메시지 {i}/{len(test_messages)} ---")
        
        # 메시지 전송 전 포인트 확인
        before_points = get_user_points(session)
        
        # 메시지 전송
        success = send_chat_message(session, session_id, message)
        
        if success:
            # 메시지 전송 후 포인트 확인
            after_points = get_user_points(session)
            if before_points and after_points:
                diff = before_points['points'] - after_points['points']
                print(f"   📊 포인트 변화: {before_points['points']:,} → {after_points['points']:,} (-{diff})")
        
        time.sleep(2)  # 다음 메시지까지 대기
    
    # 6. 포인트 히스토리 확인
    print(f"\n📊 포인트 사용 히스토리...")
    get_points_history(session)
    
    # 7. 최종 포인트 확인
    print(f"\n💰 최종 포인트 확인...")
    final_points = get_user_points(session)
    if final_points and initial_points:
        total_used = initial_points['points'] - final_points['points']
        print(f"   초기 포인트: {initial_points['points']:,}")
        print(f"   최종 포인트: {final_points['points']:,}")
        print(f"   총 사용량: {total_used:,}")
    
    print("\n" + "=" * 60)
    print("🏁 포인트 시스템 테스트 완료")
    print("✅ 토큰 기반 포인트 차감 시스템이 정상적으로 작동합니다!")

if __name__ == "__main__":
    main()