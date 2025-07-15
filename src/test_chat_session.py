#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
채팅 세션 기능 테스트 스크립트
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001"

def test_chat_session():
    print("🧪 채팅 세션 기능 테스트 시작")
    
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
    try:
        message_data = {
            "session_id": session_id,
            "role": "user",
            "content": "안녕하세요! 테스트 메시지입니다."
        }
        response = requests.post(f"{BASE_URL}/api/messages", json=message_data)
        if response.status_code == 200:
            print("✅ 메시지 저장 성공")
        else:
            print(f"❌ 메시지 저장 실패: {response.status_code}")
    except Exception as e:
        print(f"💥 메시지 저장 오류: {e}")

    # 3. AI 응답 테스트
    print("\n3️⃣ AI 응답 테스트")
    try:
        chat_data = {
            "message": "안녕하세요!",
            "session_id": session_id
        }
        response = requests.post(f"{BASE_URL}/api/chat", json=chat_data)
        if response.status_code == 200:
            chat_response = response.json()
            print(f"✅ AI 응답 성공: {chat_response.get('response', '')[:50]}...")
        else:
            print(f"❌ AI 응답 실패: {response.status_code}")
    except Exception as e:
        print(f"💥 AI 응답 오류: {e}")

    # 4. 세션 목록 조회 테스트
    print("\n4️⃣ 세션 목록 조회 테스트")
    try:
        response = requests.get(f"{BASE_URL}/api/sessions")
        if response.status_code == 200:
            sessions = response.json()
            print(f"✅ 세션 목록 조회 성공: {len(sessions)}개 세션")
        else:
            print(f"❌ 세션 목록 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"💥 세션 목록 조회 오류: {e}")

    # 5. 세션 메시지 조회 테스트
    print("\n5️⃣ 세션 메시지 조회 테스트")
    try:
        response = requests.get(f"{BASE_URL}/api/sessions/{session_id}/messages")
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ 세션 메시지 조회 성공: {len(messages)}개 메시지")
        else:
            print(f"❌ 세션 메시지 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"💥 세션 메시지 조회 오류: {e}")

    # 6. 세션 이름 변경 테스트
    print("\n6️⃣ 세션 이름 변경 테스트")
    try:
        name_data = {"name": "테스트 세션"}
        response = requests.put(f"{BASE_URL}/api/sessions/{session_id}/name", json=name_data)
        if response.status_code == 200:
            print("✅ 세션 이름 변경 성공")
        else:
            print(f"❌ 세션 이름 변경 실패: {response.status_code}")
    except Exception as e:
        print(f"💥 세션 이름 변경 오류: {e}")

    # 7. 세션 삭제 테스트
    print("\n7️⃣ 세션 삭제 테스트")
    try:
        response = requests.delete(f"{BASE_URL}/api/sessions/{session_id}")
        if response.status_code == 200:
            print("✅ 세션 삭제 성공")
        else:
            print(f"❌ 세션 삭제 실패: {response.status_code}")
    except Exception as e:
        print(f"💥 세션 삭제 오류: {e}")

    print("\n🎉 채팅 세션 기능 테스트 완료!")

if __name__ == "__main__":
    test_chat_session() 