#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
서버 완전 테스트 스크립트
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8300"

# 세션 유지를 위한 requests 세션
session = requests.Session()

def test_login():
    """로그인 테스트"""
    print("\n1. 로그인 테스트")
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@eora.ai",
        "password": "admin123"
    })
    print(f"   상태: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   성공: {data.get('success')}")
        print(f"   사용자: {data.get('user', {}).get('email')}")
        return True
    else:
        print(f"   오류: {response.text}")
        return False

def test_create_session():
    """세션 생성 테스트"""
    print("\n2. 세션 생성 테스트")
    response = session.post(f"{BASE_URL}/api/sessions", json={
        "name": f"테스트 세션 {time.strftime('%Y-%m-%d %H:%M:%S')}"
    })
    print(f"   상태: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   성공: {data.get('success')}")
        session_id = data.get('session', {}).get('id')
        print(f"   세션 ID: {session_id}")
        return session_id
    else:
        print(f"   오류: {response.text}")
        return None

def test_get_sessions():
    """세션 목록 조회 테스트"""
    print("\n3. 세션 목록 조회 테스트")
    response = session.get(f"{BASE_URL}/api/sessions")
    print(f"   상태: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        sessions = data.get('sessions', [])
        print(f"   세션 수: {len(sessions)}")
        for s in sessions[:3]:  # 최대 3개만 표시
            print(f"   - {s.get('name')} (메시지: {s.get('message_count')}개)")
        return True
    else:
        print(f"   오류: {response.text}")
        return False

def test_chat(session_id, message):
    """채팅 테스트"""
    print(f"\n4. 채팅 테스트: '{message}'")
    response = session.post(f"{BASE_URL}/api/chat", json={
        "session_id": session_id,
        "message": message
    })
    print(f"   상태: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   성공: {data.get('success')}")
        print(f"   AI 응답: {data.get('response')}")
        return True
    else:
        print(f"   오류: {response.text}")
        return False

def test_get_messages(session_id):
    """메시지 조회 테스트"""
    print(f"\n5. 메시지 조회 테스트")
    response = session.get(f"{BASE_URL}/api/sessions/{session_id}/messages")
    print(f"   상태: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        messages = data.get('messages', [])
        print(f"   메시지 수: {len(messages)}")
        for msg in messages:
            role = "사용자" if msg.get('role') == 'user' else "AI"
            print(f"   - {role}: {msg.get('content')[:50]}...")
        return True
    else:
        print(f"   오류: {response.text}")
        return False

def test_delete_session(session_id):
    """세션 삭제 테스트"""
    print(f"\n6. 세션 삭제 테스트")
    response = session.delete(f"{BASE_URL}/api/sessions/{session_id}")
    print(f"   상태: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   성공: {data.get('success')}")
        return True
    else:
        print(f"   오류: {response.text}")
        return False

def verify_data_files():
    """데이터 파일 확인"""
    print("\n7. 데이터 파일 확인")
    import os
    
    files = ['users.json', 'sessions.json', 'messages.json']
    for file in files:
        path = f"data/{file}"
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"   ✓ {file}: {size} bytes")
            
            # 내용 확인
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        print(f"     항목 수: {len(data)}")
            except Exception as e:
                print(f"     읽기 오류: {e}")
        else:
            print(f"   ✗ {file}: 없음")

def main():
    """전체 테스트 실행"""
    print("=" * 50)
    print("EORA 서버 완전 테스트")
    print("=" * 50)
    
    # 1. 로그인
    if not test_login():
        print("\n❌ 로그인 실패. 테스트 중단.")
        return
    
    # 2. 세션 목록 조회
    test_get_sessions()
    
    # 3. 새 세션 생성
    session_id = test_create_session()
    if not session_id:
        print("\n❌ 세션 생성 실패. 테스트 중단.")
        return
    
    # 4. 채팅 테스트 (여러 메시지)
    messages = [
        "안녕하세요!",
        "오늘 날씨가 어떤가요?",
        "EORA AI의 기능을 알려주세요."
    ]
    
    for msg in messages:
        test_chat(session_id, msg)
        time.sleep(1)  # 서버 부하 방지
    
    # 5. 메시지 조회
    test_get_messages(session_id)
    
    # 6. 세션 목록 다시 조회
    test_get_sessions()
    
    # 7. 데이터 파일 확인
    verify_data_files()
    
    # 8. 세션 삭제
    test_delete_session(session_id)
    
    print("\n" + "=" * 50)
    print("✅ 테스트 완료!")
    print("=" * 50)

if __name__ == "__main__":
    main() 