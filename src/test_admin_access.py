#!/usr/bin/env python3
"""
관리자 페이지 접속 테스트 스크립트
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_admin_access():
    """관리자 페이지 접속 테스트"""
    print("🔐 관리자 페이지 접속 테스트 시작...")
    
    # 세션 생성
    session = requests.Session()
    
    # 1. 로그인
    print("\n1️⃣ 관리자 로그인 시도...")
    login_data = {
        "email": "admin@eora.com",
        "password": "admin123"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"로그인 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 로그인 성공: {data.get('message', '')}")
            print(f"관리자 권한: {data.get('data', {}).get('is_admin', False)}")
        else:
            print(f"❌ 로그인 실패: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 로그인 오류: {e}")
        return False
    
    # 2. 사용자 정보 확인
    print("\n2️⃣ 사용자 정보 확인...")
    try:
        response = session.get(f"{BASE_URL}/api/user/info")
        print(f"사용자 정보 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ 사용자 정보: {user_data}")
            print(f"관리자 권한: {user_data.get('is_admin', False)}")
        else:
            print(f"❌ 사용자 정보 조회 실패: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 사용자 정보 조회 오류: {e}")
        return False
    
    # 3. 관리자 페이지 접속
    print("\n3️⃣ 관리자 페이지 접속 시도...")
    try:
        response = session.get(f"{BASE_URL}/admin")
        print(f"관리자 페이지 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 관리자 페이지 접속 성공!")
            print(f"페이지 크기: {len(response.text)} bytes")
            if "관리자" in response.text:
                print("✅ 관리자 페이지 내용 확인됨")
            else:
                print("⚠️ 관리자 페이지 내용이 예상과 다름")
        else:
            print(f"❌ 관리자 페이지 접속 실패: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 관리자 페이지 접속 오류: {e}")
        return False
    
    # 4. 대시보드 접속
    print("\n4️⃣ 대시보드 접속 확인...")
    try:
        response = session.get(f"{BASE_URL}/dashboard")
        print(f"대시보드 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 대시보드 접속 성공!")
            if "관리자" in response.text:
                print("✅ 대시보드에 관리자 버튼 포함됨")
            else:
                print("⚠️ 대시보드에 관리자 버튼이 없음")
        else:
            print(f"❌ 대시보드 접속 실패: {response.text}")
            
    except Exception as e:
        print(f"❌ 대시보드 접속 오류: {e}")
    
    # 5. 로그아웃
    print("\n5️⃣ 로그아웃...")
    try:
        response = session.post(f"{BASE_URL}/api/auth/logout")
        print(f"로그아웃 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 로그아웃 성공!")
        else:
            print(f"❌ 로그아웃 실패: {response.text}")
            
    except Exception as e:
        print(f"❌ 로그아웃 오류: {e}")
    
    print("\n🎉 테스트 완료!")
    return True

if __name__ == "__main__":
    test_admin_access() 