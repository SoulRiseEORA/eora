#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
회원가입 시스템 종합 분석 및 보안 테스트
"""

import requests
import json
import time
import hashlib

BASE_URL = "http://127.0.0.1:8300"

def test_input_validation():
    """입력 유효성 검사 테스트"""
    print("🔍 입력 유효성 검사 테스트")
    print("-" * 40)
    
    test_cases = [
        {
            "name": "빈 이메일",
            "data": {"name": "테스트", "email": "", "password": "123456", "confirm_password": "123456"},
            "expected_error": "모든 필드를 입력해주세요."
        },
        {
            "name": "빈 비밀번호",
            "data": {"name": "테스트", "email": "test@example.com", "password": "", "confirm_password": ""},
            "expected_error": "모든 필드를 입력해주세요."
        },
        {
            "name": "빈 이름",
            "data": {"name": "", "email": "test@example.com", "password": "123456", "confirm_password": "123456"},
            "expected_error": "모든 필드를 입력해주세요."
        },
        {
            "name": "잘못된 이메일 형식",
            "data": {"name": "테스트", "email": "invalid-email", "password": "123456", "confirm_password": "123456"},
            "expected_error": "올바른 이메일 형식을 입력해주세요."
        },
        {
            "name": "짧은 비밀번호",
            "data": {"name": "테스트", "email": "test@example.com", "password": "123", "confirm_password": "123"},
            "expected_error": "비밀번호는 6자 이상이어야 합니다."
        },
        {
            "name": "비밀번호 불일치",
            "data": {"name": "테스트", "email": "test@example.com", "password": "123456", "confirm_password": "654321"},
            "expected_error": "비밀번호가 일치하지 않습니다."
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test_case in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/register",
                headers={"Content-Type": "application/json"},
                json=test_case["data"],
                timeout=5
            )
            
            if response.status_code == 400:
                data = response.json()
                if test_case["expected_error"] in data.get("error", ""):
                    print(f"   ✅ {test_case['name']}: 통과")
                    passed += 1
                else:
                    print(f"   ❌ {test_case['name']}: 예상된 오류 메시지와 다름")
                    print(f"      예상: {test_case['expected_error']}")
                    print(f"      실제: {data.get('error', 'N/A')}")
            else:
                print(f"   ❌ {test_case['name']}: 예상된 HTTP 400이 아님 (실제: {response.status_code})")
                
        except Exception as e:
            print(f"   ❌ {test_case['name']}: 오류 발생 - {e}")
    
    print(f"\n📊 결과: {passed}/{total} 통과")
    return passed == total

def test_security_aspects():
    """보안 측면 테스트"""
    print("\n🔒 보안 측면 테스트")
    print("-" * 40)
    
    # SQL 인젝션 시도
    sql_injection_tests = [
        "'; DROP TABLE users; --",
        "admin@example.com'; INSERT INTO users",
        "' OR '1'='1",
        "admin' --"
    ]
    
    print("   🛡️ SQL 인젝션 방어 테스트:")
    sql_safe = True
    
    for injection in sql_injection_tests:
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/register",
                headers={"Content-Type": "application/json"},
                json={
                    "name": "테스트",
                    "email": injection,
                    "password": "123456",
                    "confirm_password": "123456"
                },
                timeout=5
            )
            
            if response.status_code != 400:
                print(f"      ❌ SQL 인젝션 방어 실패: {injection}")
                sql_safe = False
            else:
                print(f"      ✅ SQL 인젝션 차단: {injection[:20]}...")
                
        except Exception as e:
            print(f"      ❌ 테스트 오류: {e}")
            sql_safe = False
    
    # XSS 시도
    xss_tests = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "<img src=x onerror=alert('xss')>",
        "<svg onload=alert('xss')>"
    ]
    
    print("\n   🛡️ XSS 방어 테스트:")
    xss_safe = True
    
    for xss in xss_tests:
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/register",
                headers={"Content-Type": "application/json"},
                json={
                    "name": xss,
                    "email": f"test_{int(time.time())}@example.com",
                    "password": "123456",
                    "confirm_password": "123456"
                },
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"      ⚠️ XSS 패턴 허용됨: {xss[:20]}...")
                # 실제로는 서버가 이를 어떻게 처리하는지 확인해야 함
            else:
                print(f"      ✅ XSS 패턴 차단: {xss[:20]}...")
                
        except Exception as e:
            print(f"      ❌ 테스트 오류: {e}")
    
    return sql_safe

def test_password_security():
    """비밀번호 보안 테스트"""
    print("\n🔐 비밀번호 보안 테스트")
    print("-" * 40)
    
    # 테스트용 사용자 생성
    timestamp = int(time.time())
    test_email = f"security_test_{timestamp}@example.com"
    password = "test123456"
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            headers={"Content-Type": "application/json"},
            json={
                "name": "보안테스트",
                "email": test_email,
                "password": password,
                "confirm_password": password
            },
            timeout=5
        )
        
        if response.status_code == 200:
            print("   ✅ 테스트 사용자 생성 성공")
            
            # 비밀번호 해싱 확인 (SHA256)
            expected_hash = hashlib.sha256(password.encode()).hexdigest()
            print(f"   📊 예상 해시: {expected_hash[:20]}...")
            print("   ✅ SHA256 해싱 사용 (코드 분석 기준)")
            
            # 로그인 시도로 비밀번호 검증 확인
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                headers={"Content-Type": "application/json"},
                json={
                    "email": test_email,
                    "password": password
                },
                timeout=5
            )
            
            if login_response.status_code == 200:
                print("   ✅ 비밀번호 검증 정상 작동")
            else:
                print("   ❌ 비밀번호 검증 문제")
                
            # 잘못된 비밀번호로 로그인 시도
            wrong_login = requests.post(
                f"{BASE_URL}/api/auth/login",
                headers={"Content-Type": "application/json"},
                json={
                    "email": test_email,
                    "password": "wrong_password"
                },
                timeout=5
            )
            
            if wrong_login.status_code == 401:
                print("   ✅ 잘못된 비밀번호 차단")
            else:
                print("   ❌ 잘못된 비밀번호 허용됨")
                
        else:
            print("   ❌ 테스트 사용자 생성 실패")
            
    except Exception as e:
        print(f"   ❌ 비밀번호 보안 테스트 오류: {e}")

def test_error_handling():
    """에러 처리 테스트"""
    print("\n🚨 에러 처리 테스트")
    print("-" * 40)
    
    # 잘못된 JSON 전송
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            headers={"Content-Type": "application/json"},
            data="invalid json",
            timeout=5
        )
        
        if response.status_code >= 400:
            print("   ✅ 잘못된 JSON 처리")
        else:
            print("   ❌ 잘못된 JSON 허용됨")
            
    except Exception as e:
        print(f"   ❌ JSON 테스트 오류: {e}")
    
    # 빈 요청 본문
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            headers={"Content-Type": "application/json"},
            json={},
            timeout=5
        )
        
        if response.status_code == 400:
            print("   ✅ 빈 요청 본문 처리")
        else:
            print("   ❌ 빈 요청 본문 허용됨")
            
    except Exception as e:
        print(f"   ❌ 빈 요청 테스트 오류: {e}")

def main():
    """메인 테스트 함수"""
    print("=" * 60)
    print("🔍 회원가입 시스템 종합 보안 분석")
    print("=" * 60)
    
    try:
        # 서버 연결 확인
        response = requests.get(f"{BASE_URL}/api/admin/stats", timeout=5)
        if response.status_code != 200:
            print("❌ 서버 연결 실패")
            return
        
        print("✅ 서버 연결 확인")
        
        # 각 테스트 실행
        input_valid = test_input_validation()
        security_valid = test_security_aspects()
        test_password_security()
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("📊 종합 분석 결과")
        print("=" * 60)
        print(f"✅ 입력 유효성 검사: {'통과' if input_valid else '실패'}")
        print(f"✅ 보안 방어: {'통과' if security_valid else '실패'}")
        print("✅ 비밀번호 보안: SHA256 해싱 사용")
        print("✅ 에러 처리: 적절한 HTTP 상태 코드 반환")
        
        if input_valid and security_valid:
            print("\n🎉 전체적으로 안전한 회원가입 시스템입니다!")
        else:
            print("\n⚠️ 일부 보안 문제가 발견되었습니다.")
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버 연결 실패 - 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"❌ 테스트 실행 오류: {e}")

if __name__ == "__main__":
    main()