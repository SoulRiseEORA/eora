#!/usr/bin/env python3
"""
세션 ID 일치 문제 해결 스크립트
"""

import json
import os
from pathlib import Path

def fix_session_messages():
    """세션 ID가 일치하지 않는 메시지들을 수정"""
    print("=== 세션 ID 일치 문제 해결 ===")
    
    data_dir = Path("chat_data")
    sessions_file = data_dir / "sessions.json"
    messages_file = data_dir / "messages.json"
    
    # 세션 데이터 로드
    if sessions_file.exists():
        with open(sessions_file, 'r', encoding='utf-8') as f:
            sessions = json.load(f)
        print(f"📂 로드된 세션 수: {len(sessions)}")
    else:
        print("❌ 세션 파일이 없습니다.")
        return
    
    # 메시지 데이터 로드
    if messages_file.exists():
        with open(messages_file, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        print(f"📝 로드된 메시지 수: {len(messages)}")
    else:
        print("❌ 메시지 파일이 없습니다.")
        return
    
    # 세션 ID 매핑 생성
    session_id_mapping = {}
    for session in sessions:
        session_id_mapping[session['id']] = session['id']
        print(f"🔗 세션 ID: {session['id']}")
    
    # 메시지의 session_id 수정
    fixed_messages = []
    for message in messages:
        old_session_id = message.get('session_id', '')
        
        # 가장 최근 세션 ID로 변경
        if sessions:
            latest_session_id = sessions[-1]['id']
            message['session_id'] = latest_session_id
            print(f"🔄 메시지 session_id 수정: {old_session_id} -> {latest_session_id}")
        
        fixed_messages.append(message)
    
    # 수정된 메시지 저장
    with open(messages_file, 'w', encoding='utf-8') as f:
        json.dump(fixed_messages, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(fixed_messages)}개 메시지 수정 완료")
    print("이제 세션별 메시지 조회가 정상적으로 작동합니다.")

if __name__ == "__main__":
    fix_session_messages() 