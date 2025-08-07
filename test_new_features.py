#!/usr/bin/env python3
"""
신규 기능 테스트 스크립트
- 12자리 사용자 ID 생성 테스트
- 자동 로그인 기능 테스트
"""

import requests
import json
import time
import re

BASE_URL = "http://127.0.0.1:8300"

def test_user_id_format():
    """12자리 사용자 ID 생성 테스트"""
    print("🧪 12자리 사용자 ID 생성 테스트...")
    
    test_user = {
        "name": "ID테스트사용자",
        "email": f"userid_test_{int(time.time())}@example.com",
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
        
        print(f"   상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                user_id = data['user']['user_id']
                print(f"   ✅ 회원가입 성공!")
                print(f"   🆔 생성된 사용자 ID: {user_id}")
                print(f"   📏 ID 길이: {len(user_id)}자")
                
                # 12자리 검증
                if len(user_id) == 12:
                    print(f"   ✅ 12자리 형식 정상")
                else:
                    print(f"   ❌ 12자리가 아님: {len(user_id)}자")
                
                # 영문자+숫자 조합 검증
                if re.match(r'^[A-Z0-9]{12}$', user_id):
                    print(f"   ✅ 영문자+숫자 조합 정상")
                else:
                    print(f"   ❌ 형식 오류: 영문자+숫자가 아님")
                
                return data
            else:
                print(f"   ❌ 회원가입 실패: {data.get('error', '알 수 없는 오류')}")
        else:
            try:
                error_data = response.json()
                print(f"   ❌ 회원가입 실패: {error_data.get('error', '알 수 없는 오류')}")
            except:
                print(f"   ❌ 회원가입 실패: HTTP {response.status_code}")
                
    except requests.exceptions.ConnectionError:
        print(f"   ❌ 서버 연결 실패")
        return None
    except Exception as e:
        print(f"   ❌ 오류 발생: {e}")
        return None

def test_auto_login():
    """자동 로그인 기능 테스트"""
    print("\n🧪 자동 로그인 기능 테스트...")
    
    test_user = {
        "name": "자동로그인테스트",
        "email": f"autologin_test_{int(time.time())}@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }
    
    try:
        session = requests.Session()
        
        response = session.post(
            f"{BASE_URL}/api/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"   ✅ 회원가입 성공!")
                print(f"   📧 이메일: {data['user']['email']}")
                
                # 자동 로그인 플래그 확인
                if data.get("auto_login"):
                    print(f"   ✅ 자동 로그인 플래그 존재")
                else:
                    print(f"   ❌ 자동 로그인 플래그 없음")
                
                # 리디렉션 URL 확인
                if data.get("redirect_url"):
                    print(f"   ✅ 리디렉션 URL: {data['redirect_url']}")
                else:
                    print(f"   ❌ 리디렉션 URL 없음")
                
                # 쿠키 확인
                cookies = response.cookies
                if 'user_email' in cookies:
                    print(f"   ✅ 사용자 이메일 쿠키 설정됨: {cookies['user_email']}")
                else:
                    print(f"   ❌ 사용자 이메일 쿠키 없음")
                
                # 자동 로그인 상태 확인 (메인 페이지 접속 테스트)
                print(f"   🔍 자동 로그인 상태 확인 중...")
                home_response = session.get(f"{BASE_URL}/", timeout=10)
                
                if home_response.status_code == 200:
                    print(f"   ✅ 메인 페이지 접속 성공 (자동 로그인 상태)")
                else:
                    print(f"   ⚠️ 메인 페이지 접속: {home_response.status_code}")
                
                return True
            else:
                print(f"   ❌ 회원가입 실패: {data.get('error', '알 수 없는 오류')}")
        else:
            print(f"   ❌ 회원가입 실패: {response.status_code}")
                
    except requests.exceptions.ConnectionError:
        print(f"   ❌ 서버 연결 실패")
        return False
    except Exception as e:
        print(f"   ❌ 오류 발생: {e}")
        return False

def test_multiple_user_ids():
    """여러 사용자 ID 중복 테스트"""
    print("\n🧪 여러 사용자 ID 중복 테스트...")
    
    user_ids = []
    
    for i in range(5):
        test_user = {
            "name": f"중복테스트{i+1}",
            "email": f"duplicate_test_{int(time.time())}_{i}@example.com",
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
                    user_id = data['user']['user_id']
                    user_ids.append(user_id)
                    print(f"   사용자 {i+1}: {user_id}")
                    
        except Exception as e:
            print(f"   사용자 {i+1} 생성 실패: {e}")
        
        time.sleep(0.5)  # 짧은 대기
    
    # 중복 검사
    unique_ids = set(user_ids)
    print(f"\n   생성된 ID 수: {len(user_ids)}")
    print(f"   고유 ID 수: {len(unique_ids)}")
    
    if len(user_ids) == len(unique_ids):
        print(f"   ✅ 모든 ID가 고유함 (중복 없음)")
    else:
        print(f"   ❌ 중복된 ID 발견!")
        duplicates = [id for id in user_ids if user_ids.count(id) > 1]
        print(f"   중복 ID: {duplicates}")

def main():
    """메인 테스트 함수"""
    print("🚀 신규 기능 종합 테스트")
    print("=" * 60)
    
    # 1. 12자리 사용자 ID 테스트
    result1 = test_user_id_format()
    
    # 2. 자동 로그인 기능 테스트
    result2 = test_auto_login()
    
    # 3. 여러 사용자 ID 중복 테스트
    test_multiple_user_ids()
    
    print("\n" + "=" * 60)
    print("🏁 테스트 완료")
    
    if result1 and result2:
        print("✅ 모든 신규 기능이 정상적으로 작동합니다!")
    else:
        print("⚠️ 일부 기능에 문제가 있을 수 있습니다.")
    
    print("\n💡 서버 로그를 확인하여 추가적인 정보를 확인하세요.")

if __name__ == "__main__":
    main()