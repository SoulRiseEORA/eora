#!/usr/bin/env python3
"""
실제 사용자 시나리오 테스트 스크립트
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8001"

async def test_real_user_scenario():
    """실제 사용자 시나리오 테스트"""
    print("🚀 실제 사용자 시나리오 테스트 시작")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. 관리자 로그인
        print("1️⃣ 관리자 로그인 테스트")
        login_data = {
            "email": "admin@eora.ai",
            "password": "admin123"
        }
        
        async with session.post(f"{BASE_URL}/api/login", json=login_data) as response:
            if response.status == 200:
                login_result = await response.json()
                print(f"✅ 로그인 성공: {login_result.get('success')}")
                print(f"   사용자 ID: {login_result.get('user_id')}")
                print(f"   관리자 여부: {login_result.get('is_admin')}")
                print(f"   메시지: {login_result.get('message')}")
                user_id = login_result.get('user_id')
                if not user_id:
                    print(f"❌ 사용자 ID가 없습니다: {login_result}")
                    return
            else:
                print(f"❌ 로그인 실패: {response.status}")
                error_text = await response.text()
                print(f"   오류 내용: {error_text}")
                return
        
        # 2. 세션 생성
        print("\n2️⃣ 세션 생성 테스트")
        session_data = {
            "user_id": user_id,
            "session_name": "실제 테스트 세션"
        }
        
        async with session.post(f"{BASE_URL}/api/sessions", json=session_data) as response:
            if response.status == 200:
                session_result = await response.json()
                print(f"✅ 세션 생성 성공: {session_result.get('success')}")
                print(f"   세션 ID: {session_result.get('session_id')}")
                session_id = session_result.get('session_id')
            else:
                print(f"❌ 세션 생성 실패: {response.status}")
                return
        
        # 3. 사용자 메시지 전송 (채팅 API에서 자동으로 저장되므로 생략)
        print("\n3️⃣ 사용자 메시지 전송 테스트")
        user_message = "안녕하세요! 오늘 날씨가 정말 좋네요."
        print(f"   메시지: {user_message}")
        print("   (채팅 API에서 자동으로 저장됨)")
        
        # 4. AI 채팅 (GPT 응답)
        print("\n4️⃣ AI 채팅 테스트")
        chat_data = {
            "message": user_message,
            "user_id": user_id,
            "session_id": session_id
        }
        
        start_time = time.time()
        async with session.post(f"{BASE_URL}/api/chat", json=chat_data) as response:
            if response.status == 200:
                chat_result = await response.json()
                end_time = time.time()
                response_time = end_time - start_time
                print(f"✅ AI 채팅 성공: {chat_result.get('success')}")
                print(f"   응답 시간: {response_time:.2f}초")
                print(f"   AI 응답: {chat_result.get('response', '')[:100]}...")
                
                # AI 응답은 채팅 API에서 자동으로 저장됨
                print(f"   (AI 메시지는 채팅 API에서 자동으로 저장됨)")
            else:
                print(f"❌ AI 채팅 실패: {response.status}")
        
        # 5. 세션 메시지 조회 (새로고침 시뮬레이션)
        print("\n5️⃣ 세션 메시지 조회 테스트 (새로고침 시뮬레이션)")
        await asyncio.sleep(1)  # 잠시 대기
        
        async with session.get(f"{BASE_URL}/api/sessions/{session_id}/messages") as response:
            if response.status == 200:
                messages_result = await response.json()
                print(f"✅ 메시지 조회 성공: {messages_result.get('success')}")
                print(f"   메시지 수: {messages_result.get('count')}")
                
                messages = messages_result.get('messages', [])
                for i, msg in enumerate(messages, 1):
                    role = msg.get('role', msg.get('sender', 'unknown'))
                    content = msg.get('content', '')[:50]
                    print(f"   {i}. {role}: {content}...")
            else:
                print(f"❌ 메시지 조회 실패: {response.status}")
        
        # 6. 세션 목록 조회
        print("\n6️⃣ 세션 목록 조회 테스트")
        async with session.get(f"{BASE_URL}/api/sessions?user_id={user_id}") as response:
            if response.status == 200:
                sessions_result = await response.json()
                print(f"✅ 세션 목록 조회 성공: {sessions_result.get('success')}")
                
                sessions = sessions_result.get('sessions', [])
                print(f"   세션 수: {len(sessions)}")
                for i, session_info in enumerate(sessions[:3], 1):
                    name = session_info.get('session_name', 'Unknown')
                    session_id = session_info.get('session_id', 'Unknown')
                    print(f"   {i}. {name} (ID: {session_id[:20]}...)")
            else:
                print(f"❌ 세션 목록 조회 실패: {response.status}")
        
        # 7. 관리자 사용자 목록 조회
        print("\n7️⃣ 관리자 사용자 목록 조회 테스트")
        async with session.get(f"{BASE_URL}/api/admin/users") as response:
            if response.status == 200:
                users_result = await response.json()
                print(f"✅ 사용자 목록 조회 성공: {users_result.get('success')}")
                
                users = users_result.get('users', [])
                print(f"   사용자 수: {len(users)}")
                for i, user in enumerate(users, 1):
                    name = user.get('name', 'Unknown')
                    email = user.get('email', 'Unknown')
                    is_admin = user.get('is_admin', False)
                    print(f"   {i}. {name} ({email}) - 관리자: {is_admin}")
            else:
                print(f"❌ 사용자 목록 조회 실패: {response.status}")
    
    print("\n" + "=" * 60)
    print("🎉 실제 사용자 시나리오 테스트 완료!")
    print(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(test_real_user_scenario()) 