#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB 세션 지속성 테스트
세션과 메시지가 MongoDB에 정상적으로 저장되고 복원되는지 확인
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# 프로젝트 경로 추가
sys.path.append('src')

async def test_mongodb_session_persistence():
    """MongoDB 세션 지속성 테스트"""
    
    print("🧪 MongoDB 세션 지속성 테스트 시작...")
    
    try:
        # database 모듈 import
        from database import db_manager, init_mongodb_connection
        
        # MongoDB 연결 테스트
        print("🔌 MongoDB 연결 테스트...")
        mongo_connected = init_mongodb_connection()
        
        if not mongo_connected:
            print("❌ MongoDB 연결 실패 - 테스트 중단")
            return False
        
        print("✅ MongoDB 연결 성공")
        
        # 데이터베이스 매니저 초기화
        db_mgr = db_manager()
        
        # 연결 상태 확인
        if not db_mgr.is_connected():
            print("❌ MongoDB 연결 상태 확인 실패")
            return False
        
        print("✅ MongoDB 연결 상태 확인됨")
        
        # 테스트 데이터 준비
        test_user_id = "test_user@eora.ai"
        test_session_id = f"test_session_{int(datetime.now().timestamp())}"
        
        print(f"👤 테스트 사용자: {test_user_id}")
        print(f"📝 테스트 세션: {test_session_id}")
        
        # 1. 세션 생성 테스트
        print("\n1️⃣ 세션 생성 테스트...")
        session_data = {
            "session_id": test_session_id,
            "id": test_session_id,
            "user_id": test_user_id,
            "user_email": test_user_id,
            "name": "MongoDB 테스트 세션",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "message_count": 0
        }
        
        session_id = await db_mgr.create_session(session_data)
        if session_id:
            print(f"✅ 세션 생성 성공: {session_id}")
        else:
            print("❌ 세션 생성 실패")
            return False
        
        # 2. 메시지 저장 테스트
        print("\n2️⃣ 메시지 저장 테스트...")
        test_messages = [
            {"role": "user", "content": "안녕하세요! 첫 번째 테스트 메시지입니다."},
            {"role": "assistant", "content": "안녕하세요! MongoDB 연동이 정상적으로 작동하고 있습니다."},
            {"role": "user", "content": "세션이 장기간 보존되나요?"},
            {"role": "assistant", "content": "네, MongoDB에 저장되어 영구적으로 보존됩니다."}
        ]
        
        message_ids = []
        for msg in test_messages:
            message_id = await db_mgr.save_message(test_session_id, msg["role"], msg["content"])
            if message_id:
                message_ids.append(message_id)
                print(f"✅ 메시지 저장 성공: {msg['role']} - {msg['content'][:20]}...")
            else:
                print(f"❌ 메시지 저장 실패: {msg['role']}")
                return False
        
        print(f"📨 총 {len(message_ids)}개 메시지 저장 완료")
        
        # 3. 세션 조회 테스트
        print("\n3️⃣ 세션 조회 테스트...")
        user_sessions = await db_mgr.get_user_sessions(test_user_id)
        print(f"📂 사용자 세션 수: {len(user_sessions)}")
        
        test_session_found = False
        for session in user_sessions:
            if session.get("session_id") == test_session_id:
                test_session_found = True
                print(f"✅ 테스트 세션 발견: {session.get('name')}")
                break
        
        if not test_session_found:
            print("❌ 테스트 세션을 찾을 수 없음")
            return False
        
        # 4. 메시지 조회 테스트
        print("\n4️⃣ 메시지 조회 테스트...")
        retrieved_messages = await db_mgr.get_session_messages(test_session_id)
        print(f"📥 조회된 메시지 수: {len(retrieved_messages)}")
        
        if len(retrieved_messages) != len(test_messages):
            print(f"❌ 메시지 수 불일치: 저장 {len(test_messages)} vs 조회 {len(retrieved_messages)}")
            return False
        
        # 조회된 메시지 출력 (디버깅용)
        print("📝 조회된 메시지:")
        for i, msg in enumerate(retrieved_messages):
            print(f"  [{i}] {msg.get('role', 'unknown')}: {msg.get('content', '')[:30]}...")
        
        print("📝 원본 메시지:")
        for i, msg in enumerate(test_messages):
            print(f"  [{i}] {msg['role']}: {msg['content'][:30]}...")
        
        # 메시지 내용 검증
        for i, (original, retrieved) in enumerate(zip(test_messages, retrieved_messages)):
            if retrieved.get("content") != original["content"]:
                print(f"❌ 메시지 내용 불일치 [{i}]: {original['content']} vs {retrieved.get('content')}")
                return False
            print(f"✅ 메시지 [{i}] 내용 일치")
        
        # 5. 세션 업데이트 테스트
        print("\n5️⃣ 세션 업데이트 테스트...")
        update_data = {
            "name": "MongoDB 테스트 세션 (수정됨)",
            "updated_at": datetime.now().isoformat(),
            "message_count": len(test_messages)
        }
        
        updated = await db_mgr.update_session(test_session_id, update_data)
        if updated:
            print("✅ 세션 업데이트 성공")
        else:
            print("❌ 세션 업데이트 실패")
            return False
        
        # 6. 세션 삭제 테스트 (정리)
        print("\n6️⃣ 테스트 세션 정리...")
        deleted = await db_mgr.remove_session(test_session_id)
        if deleted:
            print("✅ 테스트 세션 삭제 완료")
        else:
            print("⚠️ 테스트 세션 삭제 실패 (수동 정리 필요)")
        
        print("\n🎉 MongoDB 세션 지속성 테스트 모두 통과!")
        print("✅ 세션과 메시지가 MongoDB에 정상적으로 저장되고 조회됩니다.")
        print("✅ 장기 기억 시스템이 활성화되었습니다!")
        
        return True
        
    except ImportError as e:
        print(f"❌ 모듈 import 실패: {e}")
        print("💡 database.py 파일이 src/ 디렉토리에 있는지 확인하세요.")
        return False
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {e}")
        return False

def main():
    """메인 함수"""
    print("=" * 60)
    print("🚀 EORA AI - MongoDB 세션 지속성 테스트")
    print("=" * 60)
    
    # 비동기 테스트 실행
    success = asyncio.run(test_mongodb_session_persistence())
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 테스트 완료: MongoDB 장기 기억 시스템 정상 작동")
    else:
        print("❌ 테스트 실패: MongoDB 연동 문제 해결 필요")
    print("=" * 60)

if __name__ == "__main__":
    main() 