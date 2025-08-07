#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
회원가입 기능 테스트 - points_db 오류 수정 후 테스트
"""

import requests
import json
import time
import random

# 서버 URL
BASE_URL = "http://127.0.0.1:8300"

def test_registration():
    """회원가입 기능 테스트"""
    print("=" * 50)
    print("🧪 회원가입 기능 테스트 시작")
    print("=" * 50)
    
    # 테스트용 사용자 정보
    timestamp = int(time.time())
    test_users = [
        {
            "name": "테스트사용자1",
            "email": f"test_user_{timestamp}@example.com",
            "password": "password123",
            "confirm_password": "password123"
        },
        {
            "name": "테스트사용자2", 
            "email": f"test_user_{timestamp + 1}@example.com",
            "password": "test12345",
            "confirm_password": "test12345"
        }
    ]
    
    success_count = 0
    
    for i, user_data in enumerate(test_users, 1):
        print(f"\n📝 테스트 {i}: {user_data['email']}")
        
        try:
            # 회원가입 요청
            response = requests.post(
                f"{BASE_URL}/api/auth/register",
                headers={"Content-Type": "application/json"},
                json=user_data,
                timeout=10
            )
            
            print(f"   📡 HTTP 상태: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 회원가입 성공!")
                print(f"   🆔 사용자 ID: {data['user']['user_id']}")
                print(f"   📧 이메일: {data['user']['email']}")
                print(f"   👤 이름: {data['user']['name']}")
                print(f"   💰 초기 포인트: {data['user']['initial_points']:,}포인트")
                print(f"   🔐 자동 로그인: {data.get('auto_login', False)}")
                print(f"   🔄 리디렉션 URL: {data.get('redirect_url', 'N/A')}")
                
                # 사용자 ID 길이 확인
                user_id_length = len(data['user']['user_id'])
                if user_id_length == 12:
                    print(f"   ✅ 사용자 ID 길이 검증 통과: {user_id_length}자리")
                else:
                    print(f"   ❌ 사용자 ID 길이 오류: {user_id_length}자리 (12자리 필요)")
                
                success_count += 1
                
            else:
                data = response.json()
                print(f"   ❌ 회원가입 실패: {data.get('error', '알 수 없는 오류')}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ 서버 연결 실패: {BASE_URL}")
            print("   💡 서버가 실행 중인지 확인하세요.")
            break
        except requests.exceptions.Timeout:
            print(f"   ❌ 요청 시간 초과")
        except Exception as e:
            print(f"   ❌ 예외 발생: {e}")
    
    print("\n" + "=" * 50)
    print(f"🏁 테스트 완료: {success_count}/{len(test_users)} 성공")
    print("=" * 50)
    
    return success_count == len(test_users)

def test_duplicate_email():
    """중복 이메일 테스트"""
    print("\n📧 중복 이메일 테스트")
    
    timestamp = int(time.time())
    duplicate_email = f"duplicate_{timestamp}@example.com"
    
    user_data = {
        "name": "중복테스트",
        "email": duplicate_email,
        "password": "test123456",
        "confirm_password": "test123456"
    }
    
    try:
        # 첫 번째 회원가입
        print(f"   1️⃣ 첫 번째 가입: {duplicate_email}")
        response1 = requests.post(
            f"{BASE_URL}/api/auth/register",
            headers={"Content-Type": "application/json"},
            json=user_data,
            timeout=10
        )
        
        if response1.status_code == 200:
            print(f"   ✅ 첫 번째 가입 성공")
            
            # 두 번째 회원가입 (중복)
            print(f"   2️⃣ 중복 가입 시도: {duplicate_email}")
            response2 = requests.post(
                f"{BASE_URL}/api/auth/register",
                headers={"Content-Type": "application/json"},
                json=user_data,
                timeout=10
            )
            
            if response2.status_code == 400:
                data = response2.json()
                print(f"   ✅ 중복 검사 통과: {data.get('error', '이미 존재하는 이메일')}")
                return True
            else:
                print(f"   ❌ 중복 검사 실패: HTTP {response2.status_code}")
                return False
        else:
            print(f"   ❌ 첫 번째 가입 실패: HTTP {response1.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ 중복 테스트 오류: {e}")
        return False

if __name__ == "__main__":
    # 서버 대기
    print("⏳ 서버 시작 대기 중...")
    time.sleep(3)
    
    # 기본 회원가입 테스트
    basic_test_passed = test_registration()
    
    # 중복 이메일 테스트
    duplicate_test_passed = test_duplicate_email()
    
    # 최종 결과
    print("\n" + "=" * 60)
    print("🎯 최종 테스트 결과")
    print("=" * 60)
    print(f"✅ 기본 회원가입: {'통과' if basic_test_passed else '실패'}")
    print(f"✅ 중복 이메일 검사: {'통과' if duplicate_test_passed else '실패'}")
    
    if basic_test_passed and duplicate_test_passed:
        print("\n🎉 모든 테스트 통과! 회원가입 시스템이 정상적으로 작동합니다.")
    else:
        print("\n❌ 일부 테스트 실패. 시스템을 확인해주세요.")