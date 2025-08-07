#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
채팅 기능 테스트 스크립트
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001"

def test_chat_functionality():
    """채팅 기능 종합 테스트"""
    print("🧪 채팅 기능 테스트 시작")
    
    # 1. 세션 생성 테스트
    print("\n1️⃣ 세션 생성 테스트")
    try:
        response = requests.post(f"{BASE_URL}/api/sessions")
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data.get("session_id")
            print(f"✅ 세션 생성 성공: {session_id}")
        else:
            print(f"❌ 세션 생성 실패: {response.status_code}")
            return
    except Exception as e:
        print(f"💥 세션 생성 오류: {e}")
        return
    
    # 2. 메시지 저장 테스트
    print("\n2️⃣ 메시지 저장 테스트")
    test_message = {
        "session_id": session_id,
        "role": "user",
        "content": "안녕하세요! 테스트 메시지입니다.",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/messages", json=test_message)
        if response.status_code == 200:
            print("✅ 메시지 저장 성공")
        else:
            print(f"❌ 메시지 저장 실패: {response.status_code}")
            print(f"응답: {response.text}")
    except Exception as e:
        print(f"💥 메시지 저장 오류: {e}")
    
    # 3. AI 응답 테스트
    print("\n3️⃣ AI 응답 테스트")
    chat_message = {
        "message": "안녕하세요!",
        "session_id": session_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/chat", json=chat_message)
        if response.status_code == 200:
            chat_data = response.json()
            print(f"✅ AI 응답 성공: {chat_data.get('response', '')[:50]}...")
        else:
            print(f"❌ AI 응답 실패: {response.status_code}")
            print(f"응답: {response.text}")
    except Exception as e:
        print(f"💥 AI 응답 오류: {e}")
    
    # 4. 메시지 조회 테스트
    print("\n4️⃣ 메시지 조회 테스트")
    try:
        response = requests.get(f"{BASE_URL}/api/sessions/{session_id}/messages")
        if response.status_code == 200:
            messages_data = response.json()
            messages = messages_data.get("messages", [])
            print(f"✅ 메시지 조회 성공: {len(messages)}개 메시지")
            for i, msg in enumerate(messages):
                print(f"  {i+1}. {msg.get('role', 'unknown')}: {msg.get('content', '')[:30]}...")
        else:
            print(f"❌ 메시지 조회 실패: {response.status_code}")
            print(f"응답: {response.text}")
    except Exception as e:
        print(f"💥 메시지 조회 오류: {e}")
    
    # 5. 세션 목록 조회 테스트
    print("\n5️⃣ 세션 목록 조회 테스트")
    try:
        response = requests.get(f"{BASE_URL}/api/sessions")
        if response.status_code == 200:
            sessions_data = response.json()
            sessions = sessions_data.get("sessions", [])
            print(f"✅ 세션 목록 조회 성공: {len(sessions)}개 세션")
            for i, session in enumerate(sessions):
                print(f"  {i+1}. {session.get('name', 'Unknown')} ({session.get('id', 'No ID')})")
        else:
            print(f"❌ 세션 목록 조회 실패: {response.status_code}")
            print(f"응답: {response.text}")
    except Exception as e:
        print(f"💥 세션 목록 조회 오류: {e}")
    
    print("\n🎉 채팅 기능 테스트 완료!")

if __name__ == "__main__":
    test_chat_functionality() 