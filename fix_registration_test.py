#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
회원가입 문제 해결 및 테스트
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8300"

def wait_for_server(max_attempts=10):
    """서버가 시작될 때까지 대기"""
    print("🔄 서버 시작 대기 중...")
    for i in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=2)
            if response.status_code == 200:
                print("✅ 서버가 시작되었습니다!")
                return True
        except:
            time.sleep(2)
            print(f"   대기 중... ({i+1}/{max_attempts})")
    
    print("❌ 서버 시작 확인 실패")
    return False

def test_registration():
    """회원가입 테스트"""
    print("\n🧪 회원가입 테스트 시작...")
    
    # 고유한 테스트 사용자 생성
    timestamp = int(time.time())
    test_email = f"testuser{timestamp}@eora.ai"
    
    # 회원가입 데이터
    registration_data = {
        "email": test_email,
        "password": "test123456",
        "name": "테스트 사용자"
    }
    
    print(f"📧 테스트 이메일: {test_email}")
    
    try:
        # 회원가입 요청
        print("📤 회원가입 요청 전송...")
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=registration_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 회원가입 성공!")
            print(f"👤 사용자 ID: {result.get('user', {}).get('user_id', 'N/A')}")
            print(f"💰 초기 포인트: {result.get('user', {}).get('initial_points', 0):,}")
            print(f"💾 저장소: {result.get('user', {}).get('storage_quota_mb', 0)}MB")
            
            # 로그인 테스트
            print("\n🔐 로그인 테스트...")
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": test_email, "password": "test123456"},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                print("✅ 로그인 성공!")
                print(f"💰 현재 포인트: {login_result.get('user', {}).get('points', 0):,}")
                return True
            else:
                print(f"❌ 로그인 실패: {login_response.status_code}")
                print(f"   응답: {login_response.text}")
                return False
        else:
            print(f"❌ 회원가입 실패: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   오류: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   원시 응답: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버 연결 실패")
        return False
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 EORA 회원가입 문제 해결 테스트")
    print("=" * 60)
    
    # 서버 대기
    if not wait_for_server():
        print("\n❌ 서버가 시작되지 않았습니다.")
        print("💡 다음 명령으로 서버를 시작해주세요: python src/app.py")
        exit(1)
    
    # 회원가입 테스트
    success = test_registration()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 회원가입이 정상적으로 작동합니다!")
        print("✅ 문제가 해결되었습니다.")
    else:
        print("❌ 회원가입에 여전히 문제가 있습니다.")
        print("🔧 추가 디버깅이 필요합니다.")
    print("=" * 60)