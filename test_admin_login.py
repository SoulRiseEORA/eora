#!/usr/bin/env python3
"""
관리자 로그인 및 대시보드 기능 테스트 스크립트
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_admin_login():
    """관리자 로그인 테스트"""
    print("🔐 관리자 로그인 테스트 시작...")
    
    # 로그인
    login_data = {
        "email": "admin@eora.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"로그인 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"로그인 성공: {data}")
            print(f"관리자 권한: {data.get('data', {}).get('is_admin', False)}")
            return True
        else:
            print(f"로그인 실패: {response.text}")
            return False
            
    except Exception as e:
        print(f"로그인 오류: {e}")
        return False

def test_user_info():
    """사용자 정보 조회 테스트"""
    print("\n👤 사용자 정보 조회 테스트...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/user/info")
        print(f"사용자 정보 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"사용자 정보: {data}")
            print(f"관리자 권한: {data.get('is_admin', False)}")
            return True
        else:
            print(f"사용자 정보 조회 실패: {response.text}")
            return False
            
    except Exception as e:
        print(f"사용자 정보 조회 오류: {e}")
        return False

def test_logout():
    """로그아웃 테스트"""
    print("\n🚪 로그아웃 테스트...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/logout")
        print(f"로그아웃 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            print("로그아웃 성공")
            return True
        else:
            print(f"로그아웃 실패: {response.text}")
            return False
            
    except Exception as e:
        print(f"로그아웃 오류: {e}")
        return False

def test_dashboard_access():
    """대시보드 접근 테스트"""
    print("\n📊 대시보드 접근 테스트...")
    
    try:
        response = requests.get(f"{BASE_URL}/dashboard")
        print(f"대시보드 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            print("대시보드 접근 성공")
            return True
        else:
            print(f"대시보드 접근 실패: {response.text}")
            return False
            
    except Exception as e:
        print(f"대시보드 접근 오류: {e}")
        return False

def test_admin_page_access():
    """관리자 페이지 접근 테스트"""
    print("\n🔧 관리자 페이지 접근 테스트...")
    
    try:
        response = requests.get(f"{BASE_URL}/admin")
        print(f"관리자 페이지 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            print("관리자 페이지 접근 성공")
            return True
        else:
            print(f"관리자 페이지 접근 실패: {response.text}")
            return False
            
    except Exception as e:
        print(f"관리자 페이지 접근 오류: {e}")
        return False

if __name__ == "__main__":
    print("🚀 EORA AI 시스템 테스트 시작")
    print("=" * 50)
    
    # 테스트 실행
    login_success = test_admin_login()
    
    if login_success:
        test_user_info()
        test_dashboard_access()
        test_admin_page_access()
        test_logout()
    
    print("\n" + "=" * 50)
    print("✅ 테스트 완료") 