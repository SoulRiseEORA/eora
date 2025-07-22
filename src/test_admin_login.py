#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
관리자 로그인 API 테스트 스크립트
"""

import urllib.request
import urllib.parse
import json

def test_admin_login():
    try:
        print("🔍 관리자 로그인 API 테스트 중...")
        
        # 테스트 데이터
        test_data = {
            "email": "admin@eora.ai",
            "password": "admin123"
        }
        
        # JSON 데이터를 바이트로 변환
        data = json.dumps(test_data).encode('utf-8')
        
        # 요청 생성
        req = urllib.request.Request(
            "http://127.0.0.1:8001/api/admin/login",
            data=data,
            method='POST'
        )
        req.add_header('Content-Type', 'application/json')
        
        # 요청 전송
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print(f"📊 응답 상태: {response.status}")
            print(f"📄 응답 내용: {result}")
            
            try:
                json_result = json.loads(result)
                print(f"✅ JSON 파싱 성공!")
                
                if json_result.get('success'):
                    print("🎉 관리자 로그인 성공!")
                    access_token = json_result.get('access_token', '')
                    print(f"🔑 Access Token: {access_token[:50]}...")
                    
                    # 토큰으로 관리자 페이지 접근 테스트
                    test_admin_page_access(access_token)
                else:
                    print("❌ 관리자 로그인 실패!")
                    print(f"Error: {json_result.get('message', 'Unknown error')}")
                    
            except json.JSONDecodeError:
                print(f"📄 응답 (JSON 아님): {result}")
                
    except Exception as e:
        print(f"💥 테스트 실패: {e}")

def test_admin_page_access(access_token):
    try:
        print("\n🔍 관리자 페이지 접근 테스트 중...")
        
        req = urllib.request.Request("http://127.0.0.1:8001/admin")
        req.add_header('Authorization', f'Bearer {access_token}')
        
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print(f"📊 관리자 페이지 응답 상태: {response.status}")
            
            if response.status == 200:
                print("✅ 관리자 페이지 접근 성공!")
                if "관리자" in result or "admin" in result.lower():
                    print("✅ 관리자 페이지 내용이 포함되어 있습니다.")
                else:
                    print("⚠️ 관리자 페이지 내용을 찾을 수 없습니다.")
            else:
                print(f"❌ 관리자 페이지 접근 실패: {response.status}")
                print(f"응답: {result[:200]}...")
                
    except Exception as e:
        print(f"💥 관리자 페이지 테스트 실패: {e}")

if __name__ == "__main__":
    print("🚀 관리자 로그인 테스트 시작...")
    test_admin_login()
    print("\n✅ 테스트 완료!") 