#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 관리자 API 테스트
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8300"
ADMIN_EMAIL = "admin@eora.ai"
ADMIN_PASSWORD = "admin123"

def simple_test():
    # 관리자 로그인
    admin_session = requests.Session()
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    
    response = admin_session.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"관리자 로그인: {response.status_code}")
    
    # 관리자 포인트 사용자 목록 조회
    response = admin_session.get(f"{BASE_URL}/api/admin/points/users")
    print(f"API 응답: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        users = data.get('users', [])
        print(f"사용자 수: {len(users)}")
        
        # 최근 5명의 사용자 정보 상세 출력
        print("\n최근 사용자들:")
        for i, user in enumerate(users[-5:]):
            print(f"{i+1}. {json.dumps(user, indent=2, ensure_ascii=False)}")
    else:
        print(f"오류: {response.text}")

if __name__ == "__main__":
    simple_test() 