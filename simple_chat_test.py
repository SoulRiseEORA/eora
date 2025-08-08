#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 채팅 API 테스트 (MongoDB 없이)
OpenAI API 키만 있으면 작동
"""

import os
import requests
import json
from datetime import datetime

def test_server_status():
    """서버 상태 확인"""
    try:
        response = requests.get("http://127.0.0.1:8300/", timeout=5)
        if response.status_code == 200:
            print("✅ 서버가 정상적으로 실행 중입니다!")
            return True
        else:
            print(f"⚠️ 서버 응답 상태: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        print("💡 다음 명령어로 서버를 시작하세요:")
        print("   cd src && python app.py")
        return False
    except Exception as e:
        print(f"❌ 서버 상태 확인 실패: {e}")
        return False

def test_admin_login():
    """관리자 로그인 테스트"""
    try:
        login_data = {
            "email": "admin@eora.ai", 
            "password": "admin123"
        }
        
        response = requests.post(
            "http://127.0.0.1:8300/api/auth/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                user_info = result.get("user", {})
                print("✅ 관리자 로그인 성공!")
                print(f"   📧 이메일: {user_info.get('email')}")
                print(f"   👤 이름: {user_info.get('name')}")
                print(f"   👑 관리자: {user_info.get('is_admin')}")
                print(f"   💰 포인트: {user_info.get('points', 0):,}")
                return True
            else:
                print("❌ 관리자 로그인 실패:", result.get("error"))
                return False
        else:
            print(f"❌ 관리자 로그인 요청 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 관리자 로그인 테스트 오류: {e}")
        return False

def test_user_registration():
    """일반 회원 가입 테스트"""
    try:
        # 랜덤 이메일 생성 (테스트용)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_email = f"test_user_{timestamp}@example.com"
        
        register_data = {
            "name": "테스트 사용자",
            "email": test_email,
            "password": "test123456"
        }
        
        response = requests.post(
            "http://127.0.0.1:8300/api/auth/register",
            json=register_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                user_info = result.get("user", {})
                print("✅ 일반 회원 가입 성공!")
                print(f"   📧 이메일: {user_info.get('email')}")
                print(f"   👤 이름: {user_info.get('name')}")
                print(f"   💰 초기 포인트: {user_info.get('points', 0):,}")
                return test_email
            else:
                print("❌ 일반 회원 가입 실패:", result.get("error"))
                return None
        else:
            print(f"❌ 일반 회원 가입 요청 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 일반 회원 가입 테스트 오류: {e}")
        return None

def test_chat_without_api_key():
    """API 키 없이 채팅 테스트 (오류 메시지 확인)"""
    try:
        # 관리자로 로그인 먼저
        login_data = {"email": "admin@eora.ai", "password": "admin123"}
        login_response = requests.post("http://127.0.0.1:8300/api/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print("❌ 로그인 실패로 채팅 테스트 불가")
            return False
        
        # 세션 생성
        session_data = {"name": "테스트 채팅"}
        session_response = requests.post(
            "http://127.0.0.1:8300/api/sessions", 
            json=session_data,
            cookies=login_response.cookies
        )
        
        if session_response.status_code != 200:
            print("❌ 세션 생성 실패로 채팅 테스트 불가")
            return False
        
        session_id = session_response.json().get("session_id")
        
        # 채팅 테스트
        chat_data = {
            "session_id": session_id,
            "message": "안녕하세요! API 키 테스트입니다."
        }
        
        chat_response = requests.post(
            "http://127.0.0.1:8300/api/chat",
            json=chat_data,
            cookies=login_response.cookies,
            timeout=30
        )
        
        print(f"💬 채팅 응답 상태: {chat_response.status_code}")
        
        if chat_response.status_code == 503:
            result = chat_response.json()
            error_msg = result.get("error", "")
            if "OpenAI API" in error_msg:
                print("✅ OpenAI API 키 없음을 올바르게 감지!")
                print(f"   📝 오류 메시지: {error_msg}")
                return True
        elif chat_response.status_code == 200:
            result = chat_response.json()
            if result.get("success"):
                print("✅ OpenAI API 연결 성공!")
                print(f"   🤖 AI 응답: {result.get('response', '')[:100]}...")
                return True
        
        print(f"⚠️ 예상과 다른 응답: {chat_response.text}")
        return False
        
    except Exception as e:
        print(f"❌ 채팅 테스트 오류: {e}")
        return False

def main():
    """메인 테스트 실행"""
    print("🧪 EORA AI 간단 채팅 테스트")
    print("=" * 50)
    
    results = {}
    
    # 1. 서버 상태 확인
    print("\n🌐 1. 서버 상태 확인")
    print("-" * 30)
    results['server_status'] = test_server_status()
    
    if not results['server_status']:
        print("\n❌ 서버가 실행되지 않아 다른 테스트를 진행할 수 없습니다.")
        return
    
    # 2. 관리자 로그인 테스트
    print("\n👑 2. 관리자 로그인 테스트")
    print("-" * 30)
    results['admin_login'] = test_admin_login()
    
    # 3. 일반 회원 가입 테스트
    print("\n👤 3. 일반 회원 가입 테스트")
    print("-" * 30)
    test_user_email = test_user_registration()
    results['user_registration'] = bool(test_user_email)
    
    # 4. 채팅 테스트 (API 키 유무에 따른 동작 확인)
    print("\n💬 4. 채팅 기능 테스트")
    print("-" * 30)
    results['chat_function'] = test_chat_without_api_key()
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, result in results.items():
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name:20}: {status}")
    
    print(f"\n🎯 총 {total_tests}개 테스트 중 {passed_tests}개 통과 ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests >= 3:  # 서버, 로그인, 회원가입이 성공하면 기본 기능 OK
        print("\n✅ 기본 기능이 정상적으로 작동합니다!")
        print("💡 OpenAI API 키를 설정하면 GPT 대화도 가능합니다.")
    else:
        print("\n⚠️ 기본 기능에 문제가 있습니다. 서버 로그를 확인해주세요.")

if __name__ == "__main__":
    main()