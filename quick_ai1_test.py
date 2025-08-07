#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
빠른 AI1 프롬프트 테스트
"""

import requests
import json

def test_login_and_chat():
    """로그인 후 간단한 채팅 테스트"""
    session = requests.Session()
    
    try:
        print("🔐 로그인 시도...")
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
        
        print("📝 세션 생성 시도...")
        session_response = session.post(
            "http://127.0.0.1:8300/api/sessions",
            json={"session_name": "AI1_테스트"},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if session_response.status_code != 200:
            print(f"❌ 세션 생성 실패: {session_response.status_code}")
            print(f"   응답: {session_response.text}")
            return False
        
        session_info = session_response.json()
        session_id = session_info.get("session_id")
        print(f"✅ 세션 생성 성공: {session_id}")
        
        print("💬 AI1 프롬프트 테스트 메시지 전송...")
        chat_response = session.post(
            "http://127.0.0.1:8300/api/chat",
            json={
                "message": "안녕하세요! EORA AI입니다. 당신은 8종 회상 시스템을 가지고 있나요?",
                "session_id": session_id
            },
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if chat_response.status_code != 200:
            print(f"❌ 채팅 실패: {chat_response.status_code}")
            print(f"   응답: {chat_response.text}")
            return False
        
        chat_result = chat_response.json()
        ai_response = chat_result.get("response", "")
        
        print(f"✅ AI 응답 수신 (길이: {len(ai_response)} 문자)")
        print(f"📄 응답 내용:")
        print(f"   {ai_response[:500]}...")
        
        # AI1 프롬프트 키워드 확인
        keywords = ["EORA", "8종", "회상", "키워드", "임베딩", "감정", "신념", "맥락", "시간", "연관", "패턴"]
        found = [kw for kw in keywords if kw in ai_response]
        
        if found:
            print(f"✅ AI1 프롬프트 적용 확인됨! 키워드: {found}")
            return True
        else:
            print(f"⚠️ AI1 프롬프트 적용 의심됨. 키워드 미발견.")
            return False
        
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 빠른 AI1 프롬프트 테스트")
    print("=" * 50)
    
    success = test_login_and_chat()
    
    print("=" * 50)
    print(f"📊 결과: {'✅ 성공' if success else '❌ 실패'}")
    print("=" * 50) 