#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
서버 상태 확인 스크립트
"""

import requests
import json

def test_server_status():
    """서버 상태 확인"""
    base_url = "http://127.0.0.1:8001"
    
    try:
        # 헬스 체크
        print("🔍 서버 상태 확인 중...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 서버가 정상적으로 실행 중입니다.")
            print(f"📊 응답: {response.json()}")
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}")
            
        # API 상태 확인
        print("\n🔍 API 상태 확인 중...")
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ API가 정상적으로 작동 중입니다.")
            data = response.json()
            print(f"📊 사용자 수: {data.get('users_count', 0)}")
            print(f"📊 세션 수: {data.get('sessions_count', 0)}")
        else:
            print(f"❌ API 응답 오류: {response.status_code}")
            
        # 홈페이지 접근 확인
        print("\n🔍 홈페이지 접근 확인 중...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 홈페이지가 정상적으로 접근 가능합니다.")
        else:
            print(f"❌ 홈페이지 접근 오류: {response.status_code}")
            
        # 관리자 페이지 접근 확인 (인증 필요)
        print("\n🔍 관리자 페이지 접근 확인 중...")
        response = requests.get(f"{base_url}/admin", timeout=5)
        if response.status_code == 401:
            print("✅ 관리자 페이지 인증이 정상적으로 작동합니다.")
        else:
            print(f"⚠️ 관리자 페이지 응답: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
    except requests.exceptions.Timeout:
        print("❌ 서버 응답 시간 초과")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    test_server_status() 