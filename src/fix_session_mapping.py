#!/usr/bin/env python3
"""
세션 ID 매핑 수정 스크립트
"""

import json
import os
from pathlib import Path

def fix_session_mapping():
    """세션 ID 매핑 수정"""
    print("=== 세션 ID 매핑 수정 ===")
    
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
    
    # 세션 ID 매핑 생성 (타임스탬프 기반)
    session_mapping = {}
    for session in sessions:
        # 세션 ID에서 타임스탬프 추출
        session_id = session['id']
        if session_id.startswith('session_'):
            timestamp_str = session_id.replace('session_', '')
            try:
                timestamp = float(timestamp_str)
                session_mapping[timestamp] = session_id
                print(f"🔗 세션 매핑: {timestamp} -> {session_id}")
            except ValueError:
                print(f"⚠️ 잘못된 세션 ID 형식: {session_id}")
    
    # 메시지의 session_id 수정
    fixed_messages = []
    for message in messages:
        old_session_id = message.get('session_id', '')
        
        # 메시지의 session_id에서 타임스탬프 추출
        if old_session_id.startswith('session_'):
            # 다양한 형식 처리
            if '_' in old_session_id and not old_session_id.endswith('_'):
                # session_1752465700543_tevavilxq 형식
                parts = old_session_id.split('_')
                if len(parts) >= 2:
                    try:
                        timestamp = float(parts[1])
                        if timestamp in session_mapping:
                            new_session_id = session_mapping[timestamp]
                            message['session_id'] = new_session_id
                            print(f"🔄 메시지 session_id 수정: {old_session_id} -> {new_session_id}")
                        else:
                            print(f"⚠️ 매칭되는 세션을 찾을 수 없음: {old_session_id}")
                    except ValueError:
                        print(f"⚠️ 잘못된 타임스탬프: {old_session_id}")
            else:
                # session_1752462789.921662 형식
                timestamp_str = old_session_id.replace('session_', '')
                try:
                    timestamp = float(timestamp_str)
                    if timestamp in session_mapping:
                        new_session_id = session_mapping[timestamp]
                        message['session_id'] = new_session_id
                        print(f"🔄 메시지 session_id 수정: {old_session_id} -> {new_session_id}")
                    else:
                        print(f"⚠️ 매칭되는 세션을 찾을 수 없음: {old_session_id}")
                except ValueError:
                    print(f"⚠️ 잘못된 타임스탬프: {old_session_id}")
        
        fixed_messages.append(message)
    
    # 수정된 메시지 저장
    with open(messages_file, 'w', encoding='utf-8') as f:
        json.dump(fixed_messages, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(fixed_messages)}개 메시지 수정 완료")
    print("이제 세션별 메시지 조회가 정상적으로 작동합니다.")

if __name__ == "__main__":
    fix_session_mapping() 