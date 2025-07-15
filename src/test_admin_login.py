#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
관리자 로그인 API 테스트 스크립트
"""

import urllib.request
import urllib.parse
import json

def test_admin_login():
    """관리자 로그인 API 테스트"""
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
            "http://localhost:8081/api/admin/login",
            data=data,
            method='POST'
        )
        req.add_header('Content-Type', 'application/json')
        
        # 요청 전송
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print(f"📊 응답 상태: {response.status}")
            
            try:
                json_result = json.loads(result)
                print(f"✅ 응답: {json.dumps(json_result, indent=2, ensure_ascii=False)}")
                
                if json_result.get('success'):
                    print("🎉 관리자 로그인 성공!")
                else:
                    print("❌ 관리자 로그인 실패!")
                    
            except json.JSONDecodeError:
                print(f"📄 응답 (JSON 아님): {result}")
                
    except Exception as e:
        print(f"💥 테스트 실패: {e}")

def test_admin_page():
    """관리자 페이지 접근 테스트"""
    try:
        print("\n🔍 관리자 페이지 접근 테스트 중...")
        
        req = urllib.request.Request("http://localhost:8081/admin")
        
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print(f"📊 응답 상태: {response.status}")
            
            if response.status == 200:
                print("✅ 관리자 페이지 접근 성공!")
                if "EORA AI 관리자 로그인" in result:
                    print("✅ 로그인 폼이 포함되어 있습니다.")
                else:
                    print("⚠️ 로그인 폼을 찾을 수 없습니다.")
            else:
                print(f"❌ 관리자 페이지 접근 실패: {response.status}")
                
    except Exception as e:
        print(f"💥 테스트 실패: {e}")

if __name__ == "__main__":
    print("🚀 관리자 로그인 테스트 시작...")
    test_admin_login()
    test_admin_page()
    print("\n✅ 테스트 완료!") 