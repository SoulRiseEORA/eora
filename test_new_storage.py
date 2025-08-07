#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
새로운 MongoDB 저장 기능 테스트
"""

import requests
import json
import time
import sys
from pathlib import Path

# 프로젝트 루트 설정
project_root = Path(__file__).parent
sys.path.append(str(project_root / "src"))

SERVER_URL = "http://127.0.0.1:8300"

def admin_login():
    """관리자 로그인"""
    try:
        # 세션 생성
        session = requests.Session()
        
        # 로그인 페이지 먼저 방문
        login_page = session.get(f"{SERVER_URL}/login")
        if login_page.status_code != 200:
            print(f"❌ 로그인 페이지 접속 실패: {login_page.status_code}")
            return None
        
        # 로그인 API 호출
        login_data = {
            "email": "admin@eora.ai",
            "password": "admin123"
        }
        
        login_response = session.post(
            f"{SERVER_URL}/api/login",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if login_response.status_code == 200:
            result = login_response.json()
            if result.get("success"):
                print("✅ 로그인 성공")
                return session
            else:
                print(f"❌ 로그인 실패: {result.get('error', '알 수 없는 오류')}")
                return None
        else:
            print(f"❌ 로그인 API 호출 실패: {login_response.status_code}")
            print(f"응답: {login_response.text}")
            return None
    except Exception as e:
        print(f"❌ 로그인 중 오류: {e}")
        return None

def check_mongodb_counts():
    """MongoDB 데이터 개수 확인"""
    try:
        from database import (
            sessions_collection, chat_logs_collection, memories_collection
        )
        
        session_count = sessions_collection.count_documents({}) if sessions_collection is not None else 0
        message_count = chat_logs_collection.count_documents({}) if chat_logs_collection is not None else 0
        memory_count = memories_collection.count_documents({}) if memories_collection is not None else 0
        
        return session_count, message_count, memory_count
    except Exception as e:
        print(f"❌ MongoDB 확인 실패: {e}")
        return 0, 0, 0

def test_session_creation(session):
    """세션 생성 테스트"""
    try:
        session_data = {
            "name": "MongoDB 테스트 세션"
        }
        
        response = session.post(
            f"{SERVER_URL}/api/sessions",
            json=session_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                session_id = result.get("session_id")
                print(f"✅ 세션 생성 성공: {session_id}")
                return session_id
            else:
                print(f"❌ 세션 생성 실패: {result.get('error')}")
                return None
        else:
            print(f"❌ 세션 생성 요청 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 세션 생성 중 오류: {e}")
        return None

def test_chat_message(session, session_id):
    """채팅 메시지 테스트"""
    try:
        chat_data = {
            "message": "MongoDB 저장 테스트 메시지입니다.",
            "session_id": session_id
        }
        
        response = session.post(
            f"{SERVER_URL}/api/chat",
            json=chat_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 채팅 메시지 전송 성공")
                return True
            else:
                print(f"❌ 채팅 메시지 실패: {result.get('error')}")
                return False
        else:
            print(f"❌ 채팅 요청 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 채팅 중 오류: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("=" * 60)
    print("🧪 새로운 MongoDB 저장 기능 테스트")
    print("=" * 60)
    
    # 1. 관리자 로그인
    print("\n1️⃣ 관리자 로그인...")
    session = admin_login()
    if not session:
        print("❌ 로그인 실패 - 테스트 중단")
        return False
    
    # 2. 저장 전 상태 확인
    print("\n2️⃣ 저장 전 MongoDB 상태 확인...")
    before_sessions, before_messages, before_memories = check_mongodb_counts()
    print(f"   📊 저장 전 - 세션: {before_sessions}개, 메시지: {before_messages}개, 메모리: {before_memories}개")
    
    # 3. 새 세션 생성
    print("\n3️⃣ 새 세션 생성...")
    session_id = test_session_creation(session)
    if not session_id:
        print("❌ 세션 생성 실패 - 테스트 중단")
        return False
    
    # 4. 채팅 메시지 전송
    print("\n4️⃣ 채팅 메시지 전송...")
    chat_success = test_chat_message(session, session_id)
    if not chat_success:
        print("❌ 채팅 실패")
        return False
    
    # 5. 저장 후 상태 확인
    print("\n5️⃣ 저장 후 MongoDB 상태 확인...")
    time.sleep(1)  # 저장 시간 대기
    after_sessions, after_messages, after_memories = check_mongodb_counts()
    print(f"   📊 저장 후 - 세션: {after_sessions}개, 메시지: {after_messages}개, 메모리: {after_memories}개")
    
    # 6. 결과 분석
    session_increase = after_sessions - before_sessions
    message_increase = after_messages - before_messages
    memory_increase = after_memories - before_memories
    
    print(f"\n📈 증가량:")
    print(f"   - 세션: +{session_increase}개")
    print(f"   - 메시지: +{message_increase}개")
    print(f"   - 메모리: +{memory_increase}개")
    
    # 결과 평가
    success = (session_increase >= 1 and message_increase >= 2)  # 사용자 + AI 메시지
    
    print("\n" + "=" * 60)
    print("📊 테스트 결과")
    print("=" * 60)
    
    if success:
        print("🎉 성공: MongoDB에 대화가 정상적으로 저장되었습니다!")
        print("   📈 세션과 메시지가 MongoDB에 영구 저장됨")
        print("   🔒 레일웨이 배포 시 데이터 보존 가능")
        print("   ☁️ 클라우드 환경에서 안정적으로 작동")
    else:
        print("❌ 실패: MongoDB 저장에 문제가 있습니다")
        print("   🔧 코드 수정이 필요할 수 있습니다")
    
    print("=" * 60)
    return success

if __name__ == "__main__":
    main() 