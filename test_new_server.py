#!/usr/bin/env python3
"""EORA AI System - 서버 테스트 스크립트"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8010"

def test_server_status():
    """서버 상태 확인"""
    print("\n1️⃣ 서버 상태 확인")
    
    url = f"{BASE_URL}/health"
    
    try:
        response = requests.get(url, timeout=5)
        print(f"응답 상태: {response.status_code}")
        
        if response.ok:
            data = response.json()
            print(f"✅ 서버 상태: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ 서버 상태 확인 실패: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 서버 연결 실패: 서버가 실행 중인지 확인하세요.")
        return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def test_admin_page():
    """관리자 페이지 접근 테스트"""
    print("\n2️⃣ 관리자 페이지 접근 테스트")
    
    url = f"{BASE_URL}/admin"
    
    try:
        # 로그인 없이 접근 시도 (리다이렉트 예상)
        response = requests.get(url, timeout=5, allow_redirects=False)
        if response.status_code == 302 or response.status_code == 303:
            print(f"✅ 로그인 없이 접근 시 리다이렉트 확인: {response.status_code}")
            print(f"✅ 리다이렉트 위치: {response.headers.get('Location', '알 수 없음')}")
        else:
            print(f"❌ 예상치 못한 응답: {response.status_code}")
            print(f"응답 내용: {response.text[:100]}...")
        
        # 관리자 쿠키로 접근 시도
        cookies = {
            "user_email": "admin@eora.ai",
            "is_admin": "true",
            "role": "admin"
        }
        
        response = requests.get(url, cookies=cookies, timeout=5)
        print(f"관리자 쿠키로 접근 시 응답 상태: {response.status_code}")
        
        if response.ok:
            print("✅ 관리자 쿠키로 접근 성공")
            if "관리자" in response.text or "Admin" in response.text:
                print("✅ 관리자 페이지 내용 확인됨")
            else:
                print("⚠️ 관리자 페이지 내용을 찾을 수 없음")
        else:
            print(f"❌ 관리자 쿠키로 접근 실패: {response.text[:100]}...")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def test_login_page():
    """로그인 페이지 접근 테스트"""
    print("\n3️⃣ 로그인 페이지 접근 테스트")
    
    url = f"{BASE_URL}/login"
    
    try:
        response = requests.get(url, timeout=5)
        print(f"응답 상태: {response.status_code}")
        
        if response.ok:
            print("✅ 로그인 페이지 접근 성공")
            if "로그인" in response.text or "Login" in response.text:
                print("✅ 로그인 페이지 내용 확인됨")
            else:
                print("⚠️ 로그인 페이지 내용을 찾을 수 없음")
        else:
            print(f"❌ 로그인 페이지 접근 실패: {response.text[:100]}...")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def test_home_page():
    """홈페이지 접근 테스트"""
    print("\n4️⃣ 홈페이지 접근 테스트")
    
    url = f"{BASE_URL}/"
    
    try:
        response = requests.get(url, timeout=5)
        print(f"응답 상태: {response.status_code}")
        
        if response.ok:
            print("✅ 홈페이지 접근 성공")
            # 일반 사용자로 접근
            if "관리자" not in response.text and "Admin" not in response.text:
                print("✅ 일반 사용자 접근 시 관리자 메뉴 없음 확인")
            else:
                print("⚠️ 일반 사용자 접근인데 관리자 메뉴가 보임")
            
            # 관리자로 접근
            cookies = {
                "user_email": "admin@eora.ai",
                "is_admin": "true",
                "role": "admin"
            }
            
            response = requests.get(url, cookies=cookies, timeout=5)
            if "관리자" in response.text or "Admin" in response.text:
                print("✅ 관리자 접근 시 관리자 메뉴 표시 확인")
            else:
                print("⚠️ 관리자 접근인데 관리자 메뉴가 보이지 않음")
        else:
            print(f"❌ 홈페이지 접근 실패: {response.text[:100]}...")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def main():
    print("=" * 60)
    print("EORA AI System - 서버 테스트")
    print(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 서버 상태 확인
    server_running = test_server_status()
    
    if not server_running:
        print("\n❌ 서버가 실행되지 않았습니다. 테스트를 중단합니다.")
        return
    
    # 2. 관리자 페이지 접근 테스트
    test_admin_page()
    
    # 3. 로그인 페이지 접근 테스트
    test_login_page()
    
    # 4. 홈페이지 접근 테스트
    test_home_page()
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    main() 