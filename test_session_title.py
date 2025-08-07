#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
세션 제목 자동 생성 테스트 스크립트
"""

import requests
import json
import time

def test_session_title_auto_generation():
    """세션 제목 자동 생성 테스트"""
    print("🧪 세션 제목 자동 생성 테스트 시작...")
    
    session = requests.Session()
    
    try:
        # 1. 로그인
        print("\n🔐 1단계: 로그인...")
        login_response = session.post(
            "http://127.0.0.1:8300/api/login",
            json={"email": "admin@eora.ai", "password": "admin123"},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ 로그인 실패: {login_response.status_code}")
            return False
        
        print("✅ 로그인 성공")
        
        # 2. 새 세션 생성
        print("\n📝 2단계: 새 세션 생성...")
        session_name = f"테스트세션_{int(time.time())}"
        session_response = session.post(
            "http://127.0.0.1:8300/api/sessions",
            json={"session_name": session_name},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if session_response.status_code != 200:
            print(f"❌ 세션 생성 실패: {session_response.status_code}")
            return False
        
        session_data = session_response.json()
        session_id = session_data.get("session_id")
        print(f"✅ 세션 생성 성공: {session_id}")
        print(f"📝 초기 세션 제목: '{session_data.get('session', {}).get('name', 'N/A')}'")
        
        # 3. 첫 번째 채팅 메시지 전송
        print("\n💬 3단계: 첫 번째 메시지 전송...")
        first_message = "안녕하세요! 오늘 날씨가 정말 좋네요. 어떻게 보내셨나요?"
        
        chat_response = session.post(
            "http://127.0.0.1:8300/api/chat",
            json={
                "session_id": session_id,
                "message": first_message
            },
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if chat_response.status_code != 200:
            print(f"❌ 채팅 실패: {chat_response.status_code}")
            return False
        
        chat_data = chat_response.json()
        print("✅ 첫 번째 메시지 전송 완료")
        print(f"🤖 AI 응답: {chat_data.get('response', 'N/A')[:100]}...")
        
        # 4. 잠시 대기 후 세션 목록 확인
        print("\n📋 4단계: 세션 목록 확인...")
        time.sleep(2)  # 서버에서 처리할 시간 제공
        
        sessions_response = session.get(
            "http://127.0.0.1:8300/api/sessions",
            timeout=10
        )
        
        if sessions_response.status_code != 200:
            print(f"❌ 세션 목록 조회 실패: {sessions_response.status_code}")
            return False
        
        sessions_data = sessions_response.json()
        sessions_list = sessions_data.get("sessions", [])
        
        # 방금 생성한 세션 찾기
        target_session = None
        for sess in sessions_list:
            if sess.get("id") == session_id or sess.get("session_id") == session_id:
                target_session = sess
                break
        
        if not target_session:
            print(f"❌ 대상 세션을 찾을 수 없음: {session_id}")
            return False
        
        # 5. 결과 검증
        print("\n🎯 5단계: 결과 검증...")
        updated_title = target_session.get("name", "")
        expected_title = first_message[:50] + ("..." if len(first_message) > 50 else "")
        
        print(f"📝 업데이트된 세션 제목: '{updated_title}'")
        print(f"🎯 예상 제목: '{expected_title}'")
        
        if updated_title == expected_title:
            print("✅ 세션 제목 자동 생성 성공! 첫 번째 메시지가 제목으로 설정됨")
            return True
        else:
            print("❌ 세션 제목이 예상과 다름")
            return False
            
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        return False

def test_long_message_title():
    """긴 메시지의 제목 처리 테스트"""
    print("\n\n🧪 긴 메시지 제목 처리 테스트 시작...")
    
    session = requests.Session()
    
    try:
        # 로그인
        login_response = session.post(
            "http://127.0.0.1:8300/api/login",
            json={"email": "admin@eora.ai", "password": "admin123"},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ 로그인 실패: {login_response.status_code}")
            return False
        
        # 새 세션 생성
        session_name = f"긴메시지테스트_{int(time.time())}"
        session_response = session.post(
            "http://127.0.0.1:8300/api/sessions",
            json={"session_name": session_name},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        session_data = session_response.json()
        session_id = session_data.get("session_id")
        
        # 긴 메시지 전송 (50자 이상)
        long_message = "이것은 매우 긴 메시지입니다. 50자를 초과하는 메시지가 세션 제목으로 설정될 때 어떻게 처리되는지 확인하는 테스트입니다. 줄임표가 제대로 추가되는지 확인해보겠습니다."
        
        chat_response = session.post(
            "http://127.0.0.1:8300/api/chat",
            json={
                "session_id": session_id,
                "message": long_message
            },
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if chat_response.status_code != 200:
            print(f"❌ 채팅 실패: {chat_response.status_code}")
            return False
        
        # 세션 목록 확인
        time.sleep(2)
        sessions_response = session.get("http://127.0.0.1:8300/api/sessions", timeout=10)
        sessions_data = sessions_response.json()
        sessions_list = sessions_data.get("sessions", [])
        
        target_session = None
        for sess in sessions_list:
            if sess.get("id") == session_id or sess.get("session_id") == session_id:
                target_session = sess
                break
        
        if target_session:
            updated_title = target_session.get("name", "")
            print(f"📝 긴 메시지 제목: '{updated_title}'")
            print(f"📏 제목 길이: {len(updated_title)}자")
            
            if len(updated_title) <= 53 and updated_title.endswith("..."):  # 50자 + "..."
                print("✅ 긴 메시지 제목 처리 성공! 50자로 제한되고 줄임표 추가됨")
                return True
            else:
                print("❌ 긴 메시지 제목 처리 실패")
                return False
        else:
            print("❌ 세션을 찾을 수 없음")
            return False
            
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        return False

def main():
    """메인 테스트 실행"""
    print("=" * 60)
    print("🎯 세션 제목 자동 생성 기능 테스트")
    print("=" * 60)
    
    # 기본 기능 테스트
    test1_result = test_session_title_auto_generation()
    
    # 긴 메시지 처리 테스트
    test2_result = test_long_message_title()
    
    # 최종 결과
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    print(f"✅ 기본 세션 제목 생성: {'성공' if test1_result else '실패'}")
    print(f"✅ 긴 메시지 제목 처리: {'성공' if test2_result else '실패'}")
    
    if test1_result and test2_result:
        print("\n🎉 모든 테스트 통과! 세션 제목 자동 생성 기능이 정상 작동합니다.")
        return True
    else:
        print("\n❌ 일부 테스트 실패. 코드 확인이 필요합니다.")
        return False

if __name__ == "__main__":
    main() 