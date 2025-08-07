#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최종 회원가입 시스템 테스트 (Railway 환경 호환성 확인)
"""

import asyncio
import aiohttp
import json
import random
import string
from datetime import datetime

# 테스트 서버 URL 설정
BASE_URL = "http://localhost:8000"  # 로컬 테스트용
# BASE_URL = "https://your-railway-app.railway.app"  # Railway 배포시 사용

async def generate_test_user():
    """테스트용 사용자 데이터 생성"""
    timestamp = int(datetime.now().timestamp())
    return {
        "email": f"fixed_test_{timestamp}@example.com",
        "password": "test123456",
        "confirm_password": "test123456",
        "name": "수정테스트"
    }

async def test_registration(session, user_data):
    """회원가입 테스트"""
    print(f"\n🧪 회원가입 테스트 시작: {user_data['email']}")
    
    try:
        async with session.post(
            f"{BASE_URL}/api/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            response_data = await response.json()
            
            print(f"📊 응답 상태코드: {response.status}")
            print(f"📊 응답 데이터: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            if response.status == 200 and response_data.get("success"):
                print("✅ 회원가입 성공!")
                
                # 자동 로그인 확인
                if response_data.get("auto_login"):
                    print("✅ 자동 로그인 설정됨")
                
                # 포인트 확인
                user = response_data.get("user", {})
                if user.get("initial_points") == 100000:
                    print("✅ 초기 포인트 100,000 지급 확인")
                
                # 12자리 사용자 ID 확인
                user_id = user.get("user_id", "")
                if len(user_id) == 12 and user_id.isalnum():
                    print(f"✅ 12자리 사용자 ID 생성 확인: {user_id}")
                else:
                    print(f"❌ 사용자 ID 형식 오류: {user_id}")
                
                return True, response_data
            else:
                print(f"❌ 회원가입 실패: {response_data.get('error', '알 수 없는 오류')}")
                return False, response_data
                
    except Exception as e:
        print(f"❌ 요청 오류: {e}")
        return False, None

async def test_duplicate_registration(session, user_data):
    """중복 회원가입 테스트"""
    print(f"\n🔄 중복 회원가입 테스트: {user_data['email']}")
    
    try:
        async with session.post(
            f"{BASE_URL}/api/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            response_data = await response.json()
            
            if response.status == 400 and "이미 존재하는 이메일" in response_data.get("error", ""):
                print("✅ 중복 이메일 검증 작동")
                return True
            else:
                print(f"❌ 중복 검증 실패: {response_data}")
                return False
                
    except Exception as e:
        print(f"❌ 중복 테스트 오류: {e}")
        return False

async def test_password_mismatch(session):
    """비밀번호 불일치 테스트"""
    user_data = await generate_test_user()
    user_data["confirm_password"] = "different_password"
    
    print(f"\n🔐 비밀번호 불일치 테스트: {user_data['email']}")
    
    try:
        async with session.post(
            f"{BASE_URL}/api/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            response_data = await response.json()
            
            if response.status == 400 and "비밀번호가 일치하지 않습니다" in response_data.get("error", ""):
                print("✅ 비밀번호 일치 검증 작동")
                return True
            else:
                print(f"❌ 비밀번호 검증 실패: {response_data}")
                return False
                
    except Exception as e:
        print(f"❌ 비밀번호 테스트 오류: {e}")
        return False

async def test_email_validation(session):
    """이메일 형식 검증 테스트"""
    invalid_emails = [
        "invalid-email",
        "test@",
        "@example.com",
        "test.example.com"
    ]
    
    print(f"\n📧 이메일 형식 검증 테스트")
    
    success_count = 0
    for email in invalid_emails:
        user_data = {
            "email": email,
            "password": "test123456",
            "confirm_password": "test123456",
            "name": "테스트"
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/auth/register",
                json=user_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 400 and "올바른 이메일 형식" in response_data.get("error", ""):
                    print(f"✅ 잘못된 이메일 검증 성공: {email}")
                    success_count += 1
                else:
                    print(f"❌ 이메일 검증 실패: {email} - {response_data}")
                    
        except Exception as e:
            print(f"❌ 이메일 테스트 오류 ({email}): {e}")
    
    return success_count == len(invalid_emails)

async def test_server_health(session):
    """서버 상태 확인"""
    print("\n🏥 서버 상태 확인")
    
    try:
        async with session.get(f"{BASE_URL}/") as response:
            if response.status == 200:
                print("✅ 서버 응답 정상")
                return True
            else:
                print(f"❌ 서버 응답 오류: {response.status}")
                return False
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return False

async def main():
    """메인 테스트 실행"""
    print("🚀 EORA 회원가입 시스템 최종 테스트 시작")
    print(f"🎯 테스트 대상: {BASE_URL}")
    print("=" * 50)
    
    connector = aiohttp.TCPConnector(limit=10)
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        test_results = []
        
        # 1. 서버 상태 확인
        health_result = await test_server_health(session)
        test_results.append(("서버 상태", health_result))
        
        if not health_result:
            print("❌ 서버가 응답하지 않습니다. 테스트를 중단합니다.")
            return
        
        # 2. 정상 회원가입 테스트
        user_data = await generate_test_user()
        registration_result, registration_response = await test_registration(session, user_data)
        test_results.append(("정상 회원가입", registration_result))
        
        # 3. 중복 회원가입 테스트 (위의 사용자로)
        if registration_result:
            duplicate_result = await test_duplicate_registration(session, user_data)
            test_results.append(("중복 이메일 검증", duplicate_result))
        
        # 4. 비밀번호 불일치 테스트
        password_result = await test_password_mismatch(session)
        test_results.append(("비밀번호 일치 검증", password_result))
        
        # 5. 이메일 형식 검증 테스트
        email_result = await test_email_validation(session)
        test_results.append(("이메일 형식 검증", email_result))
        
        # 결과 요약
        print("\n" + "=" * 50)
        print("📊 테스트 결과 요약")
        print("=" * 50)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:.<30} {status}")
            if result:
                passed += 1
        
        print("=" * 50)
        print(f"📈 전체 결과: {passed}/{total} 테스트 통과")
        
        if passed == total:
            print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
            print("✅ Railway 환경에서 정상 작동 예상")
        else:
            print("⚠️ 일부 테스트가 실패했습니다. 코드를 점검해주세요.")
        
        print("\n🔧 디버깅 정보:")
        if registration_response:
            print(f"마지막 등록 응답: {json.dumps(registration_response, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    asyncio.run(main())