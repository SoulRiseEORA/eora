#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
메시지 저장 디버그 스크립트
"""

import json
import os
from datetime import datetime

# 데이터 파일 경로
MESSAGES_FILE = "data/messages.json"
SESSIONS_FILE = "data/sessions.json"

def check_files():
    """파일 상태 확인"""
    print("📁 파일 상태 확인")
    print("-" * 50)
    
    # data 폴더 확인
    if os.path.exists("data"):
        print("✅ data 폴더 존재")
        files = os.listdir("data")
        print(f"   파일 목록: {files}")
    else:
        print("❌ data 폴더 없음")
        return
    
    # messages.json 확인
    if os.path.exists(MESSAGES_FILE):
        print(f"\n✅ {MESSAGES_FILE} 존재")
        
        # 파일 권한 확인
        if os.access(MESSAGES_FILE, os.W_OK):
            print("   ✅ 쓰기 권한 있음")
        else:
            print("   ❌ 쓰기 권한 없음")
        
        # 파일 내용 읽기
        try:
            with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                messages_data = json.load(f)
            print(f"   세션 수: {len(messages_data)}")
            
            for session_id, messages in messages_data.items():
                print(f"   - {session_id}: {len(messages)} 메시지")
        except Exception as e:
            print(f"   ❌ 읽기 오류: {e}")
    else:
        print(f"\n❌ {MESSAGES_FILE} 없음")
    
    # sessions.json 확인
    if os.path.exists(SESSIONS_FILE):
        print(f"\n✅ {SESSIONS_FILE} 존재")
        
        try:
            with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
                sessions_data = json.load(f)
            print(f"   세션 수: {len(sessions_data)}")
            
            for session_id, session in sessions_data.items():
                print(f"   - {session_id}: {session.get('name', 'Unknown')}")
                print(f"     생성: {session.get('created_at', 'Unknown')}")
                print(f"     메시지 수: {session.get('message_count', 0)}")
        except Exception as e:
            print(f"   ❌ 읽기 오류: {e}")
    else:
        print(f"\n❌ {SESSIONS_FILE} 없음")

def test_save():
    """직접 메시지 저장 테스트"""
    print("\n\n💾 직접 저장 테스트")
    print("-" * 50)
    
    try:
        # 현재 데이터 읽기
        with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
            messages_data = json.load(f)
        
        # 테스트 메시지 추가
        test_session_id = "test_session_" + str(int(datetime.now().timestamp()))
        test_message = {
            "role": "user",
            "content": "테스트 메시지입니다.",
            "timestamp": datetime.now().isoformat()
        }
        
        messages_data[test_session_id] = [test_message]
        
        # 저장
        with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 테스트 메시지 저장 성공: {test_session_id}")
        
        # 다시 읽어서 확인
        with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
            messages_data = json.load(f)
        
        if test_session_id in messages_data:
            print("✅ 저장된 메시지 확인됨")
        else:
            print("❌ 저장된 메시지를 찾을 수 없음")
            
    except Exception as e:
        print(f"❌ 저장 테스트 실패: {e}")

def main():
    print("=" * 50)
    print("🔍 메시지 저장 디버그")
    print("=" * 50)
    
    check_files()
    test_save()
    
    print("\n\n📌 최종 파일 상태")
    print("-" * 50)
    check_files()

if __name__ == "__main__":
    main() 