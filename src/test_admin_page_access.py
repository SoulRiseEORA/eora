#!/usr/bin/env python3
"""
관리자 페이지 접속 테스트 스크립트
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_admin_page_access():
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
        print(f"로그인 오류: {e}")
        return False
    
    # 2. 관리자 페이지 접속
    print("\n2️⃣ /admin 페이지 접속 시도...")
    try:
        response = session.get(f"{BASE_URL}/admin", allow_redirects=False)
        print(f"/admin 응답 상태: {response.status_code}")
        if response.status_code in [302, 307]:
            print(f"❌ 리다이렉트 발생: {response.headers.get('location')}")
            return False
        if response.status_code == 403:
            print("❌ 403 Forbidden: 관리자 권한 없음")
            return False
        if response.status_code == 200:
            print("✅ /admin 페이지 정상 접속!")
            return True
        print(f"❌ 기타 응답: {response.status_code}")
        return False
    except Exception as e:
        print(f"/admin 접속 오류: {e}")
        return False

test_admin_page_access() 