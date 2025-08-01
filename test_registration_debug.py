#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
신규 회원가입 테스트 및 디버깅
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8300"

def test_registration():
    """신규 회원가입 테스트"""
    print("🔍 신규 회원가입 테스트 시작...")
    
    # 타임스탬프로 고유한 이메일 생성
    timestamp = int(time.time())
    test_email = f"testuser{timestamp}@test.eora.ai"
    
    registration_data = {
        "email": test_email,
        "password": "test123!",
        "name": "테스트 사용자"
    }
    
    print(f"📧 테스트 이메일: {test_email}")
    print(f"📝 등록 데이터: {registration_data}")
    
    try:
        # 회원가입 요청
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=registration_data,
            timeout=10
        )
        
        print(f"📊 응답 상태 코드: {response.status_code}")
        print(f"📄 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 회원가입 성공!")
            print(f"📝 응답 내용: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ 회원가입 실패! 상태 코드: {response.status_code}")
            print(f"📄 응답 내용: {response.text}")
            
            # 오류 응답을 JSON으로 파싱 시도
            try:
                error_data = response.json()
                print(f"📝 오류 데이터: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print("⚠️ JSON 파싱 실패")
            
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버 연결 실패! 서버가 실행 중인지 확인하세요.")
        return False
    except requests.exceptions.Timeout:
        print("❌ 요청 시간 초과!")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False

def check_server():
    """서버 상태 확인"""
    print("🔍 서버 상태 확인...")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ 서버가 정상적으로 실행 중입니다.")
            return True
        else:
            print(f"⚠️ 서버 응답 이상: {response.status_code}")
            return False
    except:
        print("❌ 서버에 연결할 수 없습니다.")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 EORA 신규 회원가입 디버깅 테스트")
    print("=" * 60)
    
    # 1. 서버 상태 확인
    if not check_server():
        print("\n🔧 서버를 먼저 시작해주세요: python src/app.py")
        exit(1)
    
    print()
    
    # 2. 회원가입 테스트
    success = test_registration()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 테스트 완료: 회원가입이 정상적으로 작동합니다!")
    else:
        print("❌ 테스트 실패: 회원가입에 문제가 있습니다.")
    print("=" * 60)