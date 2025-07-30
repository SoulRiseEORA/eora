#!/usr/bin/env python3
"""새로운 세션 시스템 테스트"""
import requests
import json
import time
from datetime import datetime
import os

# 기본 설정
BASE_URL = "http://127.0.0.1:8010"  # 서버 포트에 맞게 수정
USER_EMAIL = "admin@eora.ai"
USER_PASSWORD = "admin"
HEADERS = {}

def login_user():
    """사용자 로그인 및 인증 토큰 획득"""
    print("\n🔑 로그인 테스트")
    
    url = f"{BASE_URL}/api/auth/login"
    data = {"email": USER_EMAIL, "password": USER_PASSWORD}
    
    try:
        response = requests.post(url, json=data)
        print(f"응답 상태: {response.status_code}")
        
        if response.ok:
            result = response.json()
            if result.get("success"):
                print(f"✅ 로그인 성공: {USER_EMAIL}")
                # 쿠키 및 토큰 저장
                cookies = response.cookies
                token = result.get("access_token", "")
                global HEADERS
                HEADERS = {
                    "Authorization": f"Bearer {token}",
                    "Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()])
                }
                return True
            else:
                print(f"❌ 로그인 실패: {result.get('message', '알 수 없는 오류')}")
                return False
        else:
            print(f"❌ 로그인 실패: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 로그인 오류: {e}")
        return False

def test_create_new_session():
    """새 세션 생성 테스트"""
    print("\n1️⃣ 새 세션 생성 테스트")
    
    url = f"{BASE_URL}/api/sessions"
    data = {"name": f"테스트 세션 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
    
    response = requests.post(url, json=data, headers=HEADERS)
    print(f"응답 상태: {response.status_code}")
    
    if response.ok:
        session_data = response.json()
        print(f"✅ 세션 생성 성공: {json.dumps(session_data, indent=2, ensure_ascii=False)}")
        return session_data.get("session_id")
    else:
        print(f"❌ 세션 생성 실패: {response.text}")
        return None

def test_send_message(session_id):
    """메시지 전송 테스트"""
    print(f"\n2️⃣ 메시지 전송 테스트 (세션: {session_id})")
    
    url = f"{BASE_URL}/api/sessions/{session_id}/messages"
    messages = [
        "안녕하세요! 새로운 세션 시스템을 테스트합니다.",
        "오늘 날씨가 어떻습니까?",
        "감사합니다. 좋은 하루 보내세요!"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n메시지 {i}: {message}")
        data = {"message": message}
        
        response = requests.post(url, json=data, headers=HEADERS)
        if response.ok:
            result = response.json()
            print(f"✅ 메시지 전송 성공: {result.get('message_id', '')}")
            print(f"✅ AI 응답: {result.get('ai_response', '')[:100]}...")
        else:
            print(f"❌ 메시지 전송 실패: {response.text}")
        
        time.sleep(1)  # API 부하 방지

def test_get_sessions():
    """세션 목록 조회 테스트"""
    print(f"\n3️⃣ 세션 목록 조회 테스트")
    
    url = f"{BASE_URL}/api/sessions"
    response = requests.get(url, headers=HEADERS)
    
    if response.ok:
        data = response.json()
        sessions = data.get("sessions", [])
        print(f"✅ 총 {len(sessions)}개 세션:")
        for session in sessions[:5]:  # 최대 5개만 표시
            print(f"  - {session['name']} (ID: {session.get('session_id', session.get('id', ''))}, 메시지: {session.get('message_count', 0)}개)")
    else:
        print(f"❌ 세션 목록 조회 실패: {response.text}")

def test_get_messages(session_id):
    """세션 메시지 조회 테스트"""
    print(f"\n4️⃣ 세션 메시지 조회 테스트 (세션: {session_id})")
    
    url = f"{BASE_URL}/api/sessions/{session_id}/messages"
    response = requests.get(url, headers=HEADERS)
    
    if response.ok:
        data = response.json()
        messages = data.get("messages", [])
        print(f"✅ 총 {len(messages)}개 메시지:")
        for msg in messages[:3]:  # 최대 3개만 표시
            print(f"  - User: {msg.get('user_message', '')[:50]}...")
            print(f"  - AI: {msg.get('ai_response', '')[:50]}...")
    else:
        print(f"❌ 메시지 조회 실패: {response.text}")

def test_backup_session(session_id):
    """세션 백업 테스트"""
    print(f"\n5️⃣ 세션 백업 테스트 (세션: {session_id})")
    
    url = f"{BASE_URL}/api/sessions/{session_id}/backup"
    response = requests.post(url, headers=HEADERS)
    
    if response.ok:
        result = response.json()
        print(f"✅ 세션 백업 성공:")
        print(f"  - 백업 파일: {result.get('backup_file', '')}")
        print(f"  - 메타데이터 파일: {result.get('metadata_file', '')}")
        
        # 백업 파일 확인
        backup_file = result.get('backup_file', '')
        metadata_file = result.get('metadata_file', '')
        
        if os.path.exists(backup_file):
            print(f"✅ 백업 파일 존재: {backup_file}")
        else:
            print(f"❌ 백업 파일 없음: {backup_file}")
            
        if os.path.exists(metadata_file):
            print(f"✅ 메타데이터 파일 존재: {metadata_file}")
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                print(f"  메타데이터: {json.dumps(metadata, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 메타데이터 파일 없음: {metadata_file}")
    else:
        print(f"❌ 세션 백업 실패: {response.text}")

def main():
    print("=" * 60)
    print("새로운 세션 시스템 종합 테스트")
    print("=" * 60)
    
    # 0. 로그인
    if not login_user():
        print("❌ 로그인 실패로 테스트 중단")
        return
    
    # 1. 새 세션 생성
    session_id = test_create_new_session()
    if not session_id:
        print("❌ 세션 생성 실패로 테스트 중단")
        return
    
    # 2. 메시지 전송
    test_send_message(session_id)
    
    # 3. 세션 목록 조회
    test_get_sessions()
    
    # 4. 메시지 조회
    test_get_messages(session_id)
    
    # 5. 세션 백업
    test_backup_session(session_id)
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    main() 