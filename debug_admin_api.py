#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
관리자 API 디버깅 스크립트
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8300"
ADMIN_EMAIL = "admin@eora.ai"
ADMIN_PASSWORD = "admin123"

def test_admin_api():
    """관리자 API 테스트"""
    print("🔍 관리자 API 디버깅 시작")
    
    # 1. 신규 사용자 생성
    timestamp = int(time.time())
    test_email = f"debuguser{timestamp}@test.eora.ai"
    test_name = f"디버그사용자{timestamp}"
    test_password = "testpass123"
    
    print(f"📝 신규 사용자 생성: {test_email}")
    
    session = requests.Session()
    register_data = {
        "email": test_email,
        "password": test_password,
        "name": test_name
    }
    
    response = session.post(f"{BASE_URL}/api/auth/register", json=register_data)
    print(f"회원가입 응답: {response.status_code}")
    if response.status_code == 200:
        print(f"회원가입 성공: {response.json()}")
    else:
        print(f"회원가입 실패: {response.text}")
        return
    
    # 2. 관리자 로그인
    print("\n🔑 관리자 로그인 중...")
    admin_session = requests.Session()
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    
    response = admin_session.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"관리자 로그인 응답: {response.status_code}")
    if response.status_code == 200:
        print(f"관리자 로그인 성공")
    else:
        print(f"관리자 로그인 실패: {response.text}")
        return
    
    # 3. 관리자 포인트 사용자 목록 조회
    print("\n📊 관리자 포인트 사용자 목록 조회...")
    response = admin_session.get(f"{BASE_URL}/api/admin/points/users")
    print(f"API 응답 코드: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"API 응답 성공")
        print(f"응답 키들: {list(data.keys())}")
        
        if 'users' in data:
            users = data['users']
            print(f"총 사용자 수: {len(users)}")
            
            # 신규 사용자 찾기
            found_user = None
            for user in users:
                print(f"  사용자: {user.get('email', 'N/A')} | 포인트: {user.get('current_points', 0):,}")
                if user.get('email') == test_email:
                    found_user = user
                    print(f"  ✅ 신규 사용자 발견!")
            
            if found_user:
                print(f"\n🎉 신규 사용자 정보:")
                for key, value in found_user.items():
                    print(f"  {key}: {value}")
            else:
                print(f"\n❌ 신규 사용자 {test_email}를 찾을 수 없음")
                
        if 'stats' in data:
            stats = data['stats']
            print(f"\n📈 통계:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
    else:
        print(f"API 응답 실패: {response.text}")

if __name__ == "__main__":
    test_admin_api() 