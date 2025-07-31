#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
세션 생성 API 디버깅 스크립트
"""

import requests
import json

def test_session_creation():
    """세션 생성 API 디버깅"""
    print("🔍 세션 생성 API 디버깅 시작...")
    
    # 1. 로그인
    session = requests.Session()
    
    # 로그인 페이지 방문
    login_page = session.get("http://127.0.0.1:8300/login")
    print(f"로그인 페이지: {login_page.status_code}")
    
    # 로그인 API 호출
    login_data = {
        "email": "admin@eora.ai",
        "password": "admin123"
    }
    
    login_response = session.post(
        "http://127.0.0.1:8300/api/login",
        json=login_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"로그인 응답: {login_response.status_code}")
    print(f"로그인 결과: {login_response.text}")
    
    if login_response.status_code != 200:
        return
    
    # 2. 세션 생성
    session_data = {
        "name": "디버깅 테스트 세션"
    }
    
    session_response = session.post(
        "http://127.0.0.1:8300/api/sessions",
        json=session_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"\n세션 생성 응답:")
    print(f"상태 코드: {session_response.status_code}")
    print(f"헤더: {dict(session_response.headers)}")
    print(f"응답 텍스트: {session_response.text}")
    
    try:
        response_json = session_response.json()
        print(f"JSON 파싱 성공:")
        print(json.dumps(response_json, indent=2, ensure_ascii=False))
        
        session_id = response_json.get("session_id")
        print(f"\n추출된 session_id: {session_id}")
        print(f"session_id 타입: {type(session_id)}")
        
    except Exception as e:
        print(f"JSON 파싱 실패: {e}")

if __name__ == "__main__":
    test_session_creation() 