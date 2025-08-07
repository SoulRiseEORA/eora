#!/usr/bin/env python3
"""
회원가입 기능 테스트 스크립트
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8300"

def test_registration():
    """회원가입 테스트"""
    print("🧪 회원가입 기능 테스트 시작...")
    
    # 테스트 사용자 데이터
    test_users = [
        {
            "name": "테스트 사용자1",
            "email": "test1@example.com",
            "password": "password123",
            "confirm_password": "password123"
        },
        {
            "name": "테스트 사용자2", 
            "email": "test2@example.com",
            "password": "password456",
            "confirm_password": "password456"
        }
    ]
    
    for i, user_data in enumerate(test_users, 1):
        print(f"\n{i}. 회원가입 테스트: {user_data['email']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/register",
                json=user_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"   상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"   ✅ 회원가입 성공!")
                    print(f"   📧 이메일: {data['user']['email']}")
                    print(f"   👤 이름: {data['user']['name']}")
                    print(f"   💰 초기 포인트: {data['user']['initial_points']:,}")
                else:
                    print(f"   ❌ 회원가입 실패: {data.get('error', '알 수 없는 오류')}")
            else:
                try:
                    error_data = response.json()
                    print(f"   ❌ 회원가입 실패: {error_data.get('error', '알 수 없는 오류')}")
                except:
                    print(f"   ❌ 회원가입 실패: HTTP {response.status_code}")
                    
        except requests.exceptions.ConnectionError:
            print(f"   ❌ 서버 연결 실패 - 서버가 실행 중인지 확인하세요")
            return False
        except Exception as e:
            print(f"   ❌ 오류 발생: {e}")
            
        time.sleep(1)  # 각 테스트 간 1초 대기
    
    return True

def test_invalid_registration():
    """잘못된 회원가입 데이터 테스트"""
    print("\n🧪 잘못된 회원가입 데이터 테스트...")
    
    invalid_tests = [
        {
            "name": "빈 이메일",
            "data": {"name": "테스트", "email": "", "password": "password123"},
            "expected_error": "모든 필드를 입력해주세요"
        },
        {
            "name": "잘못된 이메일 형식", 
            "data": {"name": "테스트", "email": "invalid-email", "password": "password123"},
            "expected_error": "올바른 이메일 형식을 입력해주세요"
        },
        {
            "name": "짧은 비밀번호",
            "data": {"name": "테스트", "email": "test@example.com", "password": "123"},
            "expected_error": "비밀번호는 6자 이상이어야 합니다"
        },
        {
            "name": "비밀번호 불일치",
            "data": {"name": "테스트", "email": "test@example.com", "password": "password123", "confirm_password": "different"},
            "expected_error": "비밀번호가 일치하지 않습니다"
        }
    ]
    
    for test_case in invalid_tests:
        print(f"\n  테스트: {test_case['name']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/register",
                json=test_case["data"],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 400:
                data = response.json()
                if test_case["expected_error"] in data.get("error", ""):
                    print(f"    ✅ 예상대로 오류 발생: {data['error']}")
                else:
                    print(f"    ⚠️ 다른 오류 발생: {data.get('error', '알 수 없는 오류')}")
            else:
                print(f"    ❌ 예상과 다른 응답: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"    ❌ 서버 연결 실패")
            return False
        except Exception as e:
            print(f"    ❌ 오류 발생: {e}")

def test_duplicate_registration():
    """중복 이메일 회원가입 테스트"""
    print("\n🧪 중복 이메일 회원가입 테스트...")
    
    user_data = {
        "name": "중복 테스트",
        "email": "duplicate@example.com", 
        "password": "password123",
        "confirm_password": "password123"
    }
    
    # 첫 번째 가입
    print("  1차 가입 시도...")
    try:
        response1 = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response1.status_code == 200:
            print("    ✅ 첫 번째 가입 성공")
        else:
            print(f"    ❌ 첫 번째 가입 실패: {response1.status_code}")
            return False
            
    except Exception as e:
        print(f"    ❌ 첫 번째 가입 오류: {e}")
        return False
    
    # 두 번째 가입 (중복)
    print("  2차 가입 시도 (중복)...")
    try:
        response2 = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response2.status_code == 400:
            data = response2.json()
            if "이미 존재하는 이메일" in data.get("error", ""):
                print(f"    ✅ 중복 이메일 오류 정상 발생: {data['error']}")
            else:
                print(f"    ⚠️ 다른 오류 발생: {data.get('error', '알 수 없는 오류')}")
        else:
            print(f"    ❌ 중복 가입이 허용됨: {response2.status_code}")
            
    except Exception as e:
        print(f"    ❌ 두 번째 가입 오류: {e}")

def main():
    """메인 테스트 함수"""
    print("🚀 회원가입 기능 종합 테스트")
    print("=" * 50)
    
    # 정상 회원가입 테스트
    if not test_registration():
        print("\n❌ 서버가 실행되지 않았습니다. 먼저 서버를 시작하세요.")
        return
    
    # 잘못된 데이터 테스트
    test_invalid_registration()
    
    # 중복 이메일 테스트
    test_duplicate_registration()
    
    print("\n" + "=" * 50)
    print("🏁 테스트 완료")
    print("✅ 모든 테스트가 정상적으로 실행되었습니다.")
    print("\n💡 서버 로그를 확인하여 추가적인 정보를 확인하세요.")

if __name__ == "__main__":
    main()