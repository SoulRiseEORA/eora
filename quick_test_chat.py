#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
채팅 세션 빠른 테스트
"""

import requests
import json
from datetime import datetime
import time

# 서버 URL
SERVER_URL = "http://127.0.0.1:8100"

# 테스트용 세션
session = requests.Session()

def login():
    """관리자로 로그인"""
    print("🔐 관리자로 로그인...")
    response = session.post(f"{SERVER_URL}/api/auth/login", json={
        "email": "admin@eora.ai",
        "password": "admin123"
    })
    if response.ok:
        print("✅ 로그인 성공!")
        return True
    else:
        print(f"❌ 로그인 실패: {response.status_code}")
        print(response.text)
        return False

def get_sessions():
    """세션 목록 조회"""
    print("\n📂 세션 목록 조회...")
    response = session.get(f"{SERVER_URL}/api/sessions")
    if response.ok:
        data = response.json()
        sessions = data.get("sessions", [])
        print(f"✅ {len(sessions)}개 세션 발견")
        for i, sess in enumerate(sessions):
            print(f"  [{i+1}] {sess['name']} (ID: {sess['id']})")
        return sessions
    else:
        print(f"❌ 세션 조회 실패: {response.status_code}")
        return []

def create_session():
    """새 세션 생성"""
    print("\n🆕 새 세션 생성...")
    response = session.post(f"{SERVER_URL}/api/sessions", json={
        "name": f"테스트 세션 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    })
    if response.ok:
        data = response.json()
        session_id = data["session"]["id"]
        print(f"✅ 세션 생성 성공: {session_id}")
        return session_id
    else:
        print(f"❌ 세션 생성 실패: {response.status_code}")
        return None

def get_messages(session_id):
    """메시지 조회"""
    print(f"\n💬 메시지 조회: {session_id}")
    response = session.get(f"{SERVER_URL}/api/sessions/{session_id}/messages")
    if response.ok:
        data = response.json()
        messages = data.get("messages", [])
        print(f"✅ {len(messages)}개 메시지")
        for msg in messages:
            role = "👤 사용자" if msg["role"] == "user" else "🤖 AI"
            print(f"{role}: {msg['content']}")
        return messages
    else:
        print(f"❌ 메시지 조회 실패: {response.status_code}")
        print(f"응답: {response.text}")
        return []

def send_chat(session_id, message):
    """채팅 메시지 전송"""
    print(f"\n📤 메시지 전송: {message}")
    response = session.post(f"{SERVER_URL}/api/chat", json={
        "session_id": session_id,
        "message": message
    })
    print(f"응답 상태: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"응답 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
        ai_response = data.get("response", "")
        print(f"🤖 AI 응답: {ai_response}")
        return ai_response
    else:
        print(f"❌ 채팅 실패: {response.status_code}")
        print(f"응답: {response.text}")
        return None

def check_data_files():
    """데이터 파일 확인"""
    print("\n📁 데이터 파일 확인...")
    import os
    data_dir = "data"
    if os.path.exists(data_dir):
        files = ["sessions.json", "messages.json", "users.json"]
        for file in files:
            path = os.path.join(data_dir, file)
            if os.path.exists(path):
                size = os.path.getsize(path)
                print(f"  ✅ {file}: {size} bytes")
                
                # messages.json 내용 확인
                if file == "messages.json":
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"     세션 수: {len(data)}")
                    for session_id, messages in data.items():
                        print(f"     - {session_id}: {len(messages)} 메시지")
            else:
                print(f"  ❌ {file}: 없음")
    else:
        print("  ❌ data 폴더가 없습니다")

def main():
    print("=" * 50)
    print("🧪 EORA AI 채팅 테스트")
    print("=" * 50)
    
    # 1. 로그인
    if not login():
        return
    
    # 2. 세션 목록 확인
    sessions = get_sessions()
    
    # 3. 세션 선택 또는 생성
    if sessions:
        # 첫 번째 세션 사용
        session_id = sessions[0]["id"]
        print(f"\n✅ 기존 세션 사용: {session_id}")
    else:
        # 새 세션 생성
        session_id = create_session()
        if not session_id:
            return
    
    # 4. 이전 메시지 확인
    print("\n--- 채팅 전 메시지 ---")
    get_messages(session_id)
    
    # 5. 대화 테스트 (1개만)
    test_messages = [
        "안녕하세요! 테스트 메시지입니다."
    ]
    
    for msg in test_messages:
        send_chat(session_id, msg)
        time.sleep(2)  # 서버 처리 대기
    
    # 6. 최종 메시지 확인
    print("\n" + "=" * 50)
    print("📋 채팅 후 전체 대화 내역")
    print("=" * 50)
    get_messages(session_id)
    
    # 7. 데이터 파일 확인
    check_data_files()
    
    # 8. 세션 목록 다시 확인
    print("\n--- 최종 세션 목록 ---")
    get_sessions()
    
    print("\n✅ 테스트 완료!")

if __name__ == "__main__":
    main() 