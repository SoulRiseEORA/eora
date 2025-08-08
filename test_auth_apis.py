#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
인증 API 테스트 스크립트
"""

import requests
import json
import sys

def test_auth_apis():
    """인증 API들을 테스트합니다."""
    base_url = "http://127.0.0.1:8002"
    
    try:
        # 1. 회원가입 테스트
        print("🔍 회원가입 API 테스트 중...")
        register_data = {
            "name": "테스트사용자",
            "email": "test@example.com",
            "password": "test123"
        }
        
        response = requests.post(f"{base_url}/api/auth/register", 
                               json=register_data, timeout=10)
        print(f"✅ 회원가입: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"📝 회원가입 성공: {data.get('message', '')}")
        else:
            print(f"❌ 회원가입 실패: {response.text}")
        
        # 2. 로그인 테스트
        print("\n🔍 로그인 API 테스트 중...")
        login_data = {
            "email": "test@example.com",
            "password": "test123"
        }
        
        response = requests.post(f"{base_url}/api/auth/login", 
                               json=login_data, timeout=10)
        print(f"✅ 로그인: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"🔐 로그인 성공: {data.get('user', {}).get('name', '')}")
        else:
            print(f"❌ 로그인 실패: {response.text}")
        
        # 3. 관리자 로그인 테스트
        print("\n🔍 관리자 로그인 테스트 중...")
        admin_login_data = {
            "email": "admin@eora.ai",
            "password": "admin123"
        }
        
        response = requests.post(f"{base_url}/api/auth/login", 
                               json=admin_login_data, timeout=10)
        print(f"✅ 관리자 로그인: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"👑 관리자 로그인 성공: {data.get('user', {}).get('name', '')}")
        else:
            print(f"❌ 관리자 로그인 실패: {response.text}")
        
        # 4. 세션 생성 테스트
        print("\n🔍 세션 생성 API 테스트 중...")
        session_data = {
            "user_id": "test_user"
        }
        
        response = requests.post(f"{base_url}/api/sessions", 
                               json=session_data, timeout=10)
        print(f"✅ 세션 생성: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"📋 세션 생성 성공: {data.get('session_id', '')}")
        else:
            print(f"❌ 세션 생성 실패: {response.text}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        return False
    except requests.exceptions.Timeout:
        print("❌ 서버 응답 시간 초과")
        return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    success = test_auth_apis()
    sys.exit(0 if success else 1) 