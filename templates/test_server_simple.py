#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 간단한 서버 테스트
"""

import requests
import json
import time

def test_server():
    base_url = "http://localhost:8000"
    
    print("🚀 EORA AI System 서버 테스트 시작")
    print("=" * 50)
    
    # 1. 헬스 체크
    try:
        print("1. 헬스 체크 테스트...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 헬스 체크 성공: {data}")
        else:
            print(f"❌ 헬스 체크 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 헬스 체크 오류: {e}")
    
    # 2. API 상태 확인
    try:
        print("\n2. API 상태 확인...")
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API 상태 확인 성공: {data}")
        else:
            print(f"❌ API 상태 확인 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ API 상태 확인 오류: {e}")
    
    # 3. 세션 조회
    try:
        print("\n3. 세션 조회 테스트...")
        response = requests.get(f"{base_url}/api/sessions", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 세션 조회 성공: {len(data.get('sessions', []))}개 세션")
        else:
            print(f"❌ 세션 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 세션 조회 오류: {e}")
    
    # 4. 채팅 테스트
    try:
        print("\n4. 채팅 테스트...")
        chat_data = {
            "message": "안녕하세요! 테스트 메시지입니다.",
            "session_id": "test_session",
            "user_id": "test_user"
        }
        response = requests.post(f"{base_url}/api/chat", json=chat_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 채팅 성공: {data.get('response', '')[:50]}...")
        else:
            print(f"❌ 채팅 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 채팅 오류: {e}")
    
    # 5. 메시지 저장 테스트
    try:
        print("\n5. 메시지 저장 테스트...")
        message_data = {
            "session_id": "test_session",
            "user_id": "test_user",
            "content": "테스트 메시지",
            "role": "user"
        }
        response = requests.post(f"{base_url}/api/messages", json=message_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 메시지 저장 성공: {data.get('_id', '')}")
        else:
            print(f"❌ 메시지 저장 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 메시지 저장 오류: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 서버 테스트 완료!")

if __name__ == "__main__":
    test_server() 