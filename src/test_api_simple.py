#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 API 테스트 스크립트
"""

import urllib.request
import urllib.parse
import json

def test_api(url, method="GET", data=None):
    """API 테스트 함수"""
    try:
        if data:
            data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header('Content-Type', 'application/json')
        else:
            req = urllib.request.Request(url, method=method)
        
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print(f"✅ {method} {url} - 상태: {response.status}")
            try:
                json_result = json.loads(result)
                print(f"📄 응답: {json.dumps(json_result, indent=2, ensure_ascii=False)}")
            except:
                print(f"📄 응답: {result}")
            return True
    except Exception as e:
        print(f"❌ {method} {url} - 오류: {e}")
        return False

def main():
    """메인 테스트 함수"""
    base_url = "http://localhost:8081"
    
    print("🚀 EORA AI System API 테스트 시작")
    print("=" * 50)
    
    # 1. 상태 확인
    print("\n1️⃣ 서버 상태 확인")
    test_api(f"{base_url}/api/status")
    
    # 2. 프롬프트 API 테스트
    print("\n2️⃣ 프롬프트 API 테스트")
    test_api(f"{base_url}/api/prompts")
    
    # 3. 세션 API 테스트
    print("\n3️⃣ 세션 API 테스트")
    test_api(f"{base_url}/api/sessions")
    
    # 4. 관리자 로그인 테스트
    print("\n4️⃣ 관리자 로그인 테스트")
    login_data = {
        "email": "admin@eora.ai",
        "password": "admin123"
    }
    test_api(f"{base_url}/api/admin/login", "POST", login_data)
    
    # 5. 채팅 API 테스트
    print("\n5️⃣ 채팅 API 테스트")
    chat_data = {
        "message": "안녕하세요!",
        "session_id": "test_session",
        "user_id": "test_user"
    }
    test_api(f"{base_url}/api/chat", "POST", chat_data)
    
    print("\n" + "=" * 50)
    print("✅ API 테스트 완료")

if __name__ == "__main__":
    main() 