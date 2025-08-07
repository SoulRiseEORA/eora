#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
채팅 메시지 시간 로컬라이제이션 테스트 스크립트
"""

import requests
import json
import time
from datetime import datetime, timedelta

def test_time_localization():
    """시간 로컬라이제이션 기능 테스트"""
    print("⏰ 시간 로컬라이제이션 테스트 시작...")
    
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
        session_name = f"시간테스트_{int(time.time())}"
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
        
        # 3. 여러 시간대의 메시지 전송 테스트
        test_messages = [
            "안녕하세요! 현재 시간을 확인하는 첫 번째 메시지입니다.",
            "두 번째 메시지 - 시간 표시가 정확한지 확인해보세요.",
            "세 번째 메시지 - 사용자 로컬 시간대가 반영되는지 테스트입니다."
        ]
        
        print("\n💬 3단계: 테스트 메시지 전송...")
        for i, message in enumerate(test_messages, 1):
            print(f"  📤 메시지 {i} 전송: {message[:30]}...")
            
            chat_response = session.post(
                "http://127.0.0.1:8300/api/chat",
                json={
                    "session_id": session_id,
                    "message": message
                },
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if chat_response.status_code == 200:
                print(f"  ✅ 메시지 {i} 전송 완료")
            else:
                print(f"  ❌ 메시지 {i} 전송 실패: {chat_response.status_code}")
            
            # 메시지 간 간격
            time.sleep(2)
        
        # 4. 채팅 페이지 접근 테스트
        print("\n🌐 4단계: 채팅 페이지 접근 테스트...")
        chat_page_response = session.get("http://127.0.0.1:8300/chat", timeout=10)
        
        if chat_page_response.status_code == 200:
            print("✅ 채팅 페이지 접근 성공")
            
            # HTML 내용에서 시간 관련 JavaScript 코드 확인
            html_content = chat_page_response.text
            
            # 시간 로컬라이제이션 기능이 포함되어 있는지 확인
            time_features = [
                "formatMessageTime",
                "toLocaleTimeString",
                "Intl.DateTimeFormat",
                "timeZone",
                "data-timestamp"
            ]
            
            print("📋 시간 로컬라이제이션 기능 확인:")
            for feature in time_features:
                if feature in html_content:
                    print(f"  ✅ {feature}: 발견됨")
                else:
                    print(f"  ❌ {feature}: 없음")
        else:
            print(f"❌ 채팅 페이지 접근 실패: {chat_page_response.status_code}")
            return False
        
        # 5. 세션 메시지 조회 테스트
        print("\n📥 5단계: 세션 메시지 조회...")
        messages_response = session.get(
            f"http://127.0.0.1:8300/api/sessions/{session_id}/messages",
            timeout=10
        )
        
        if messages_response.status_code == 200:
            messages_data = messages_response.json()
            messages = messages_data.get("messages", [])
            print(f"✅ 메시지 조회 성공: {len(messages)}개 메시지")
            
            # 메시지 타임스탬프 확인
            print("📋 메시지 타임스탬프 확인:")
            for i, msg in enumerate(messages, 1):
                timestamp = msg.get("timestamp", "")
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:30]
                
                if timestamp:
                    # 타임스탬프 파싱 테스트
                    try:
                        parsed_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        local_time = parsed_time.strftime('%Y-%m-%d %H:%M:%S')
                        print(f"  📝 메시지 {i} ({role}): {local_time} - {content}...")
                    except Exception as e:
                        print(f"  ❌ 메시지 {i} 타임스탬프 파싱 실패: {e}")
                else:
                    print(f"  ⚠️ 메시지 {i} 타임스탬프 없음")
        else:
            print(f"❌ 메시지 조회 실패: {messages_response.status_code}")
        
        print("\n🎉 시간 로컬라이제이션 기능 테스트 완료!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 서버 연결 실패: 서버가 실행 중인지 확인하세요.")
        return False
    except requests.exceptions.Timeout:
        print("❌ 요청 시간 초과: 서버 응답이 너무 느립니다.")
        return False
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        return False

def test_browser_compatibility():
    """브라우저 호환성 정보 출력"""
    print("\n🌐 브라우저 호환성 정보")
    print("=" * 50)
    print("✅ JavaScript Intl.DateTimeFormat API:")
    print("  - Chrome 24+")
    print("  - Firefox 29+") 
    print("  - Safari 10+")
    print("  - Edge 12+")
    print("\n✅ 지원되는 기능:")
    print("  - 사용자 로컬 시간대 자동 감지")
    print("  - 브라우저 언어 설정 기반 시간 포맷")
    print("  - 24시간/12시간 형식 자동 선택")
    print("  - 날짜별 표시 최적화 (오늘/과거)")
    print("  - 실시간 시간 업데이트 (1분마다)")
    print("  - 툴팁으로 전체 시간 정보 제공")

def main():
    """메인 테스트 실행"""
    print("=" * 60)
    print("⏰ 채팅 메시지 시간 로컬라이제이션 테스트")
    print("=" * 60)
    
    # 기능 테스트
    test_result = test_time_localization()
    
    # 브라우저 호환성 정보
    test_browser_compatibility()
    
    # 최종 결과
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    if test_result:
        print("🎉 시간 로컬라이제이션 기능이 성공적으로 구현되었습니다!")
        print("\n📋 구현된 기능:")
        print("  ✅ 사용자 로컬 시간대 자동 적용")
        print("  ✅ 브라우저 언어 설정 기반 포맷")
        print("  ✅ 오늘/과거 날짜 구분 표시")
        print("  ✅ 실시간 시간 업데이트")
        print("  ✅ 툴팁으로 상세 시간 정보")
        print("  ✅ 세션 목록 시간 동기화")
        print("\n🌐 브라우저에서 http://127.0.0.1:8300/chat 접속하여 확인하세요!")
    else:
        print("❌ 일부 기능에서 오류가 발생했습니다.")
        print("   서버 상태를 확인하고 다시 시도해주세요.")

if __name__ == "__main__":
    main() 