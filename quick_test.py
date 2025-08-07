#!/usr/bin/env python3
"""간단한 회원가입 테스트"""
import requests
import time

def test_registration():
    try:
        # 테스트 사용자 정보
        timestamp = int(time.time())
        email = f"testuser{timestamp}@test.com"
        
        # 회원가입 요청
        response = requests.post("http://127.0.0.1:8300/api/auth/register", json={
            "email": email,
            "password": "testpass123",
            "name": f"테스트사용자{timestamp}"
        })
        
        print(f"회원가입 결과: {response.status_code}")
        if response.status_code == 200:
            print("✅ 회원가입 성공!")
            print(response.json())
        else:
            print("❌ 회원가입 실패")
            print(response.text)
            
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    test_registration() 