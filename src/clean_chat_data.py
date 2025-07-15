#!/usr/bin/env python3
"""
채팅 데이터 정리 스크립트
"""

import json
import os
from pathlib import Path

def clean_chat_data():
    """채팅 데이터 정리"""
    print("=== 채팅 데이터 정리 ===")
    
    data_dir = Path("chat_data")
    sessions_file = data_dir / "sessions.json"
    messages_file = data_dir / "messages.json"
    
    # 기존 데이터 백업
    if sessions_file.exists():
        backup_file = data_dir / "sessions_backup.json"
        with open(sessions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 세션 데이터 백업: {backup_file}")
    
    if messages_file.exists():
        backup_file = data_dir / "messages_backup.json"
        with open(messages_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 메시지 데이터 백업: {backup_file}")
    
    # 새로운 빈 데이터 생성
    empty_sessions = []
    empty_messages = []
    
    with open(sessions_file, 'w', encoding='utf-8') as f:
        json.dump(empty_sessions, f, ensure_ascii=False, indent=2)
    
    with open(messages_file, 'w', encoding='utf-8') as f:
        json.dump(empty_messages, f, ensure_ascii=False, indent=2)
    
    print("✅ 채팅 데이터가 정리되었습니다.")
    print("이제 새로운 세션과 메시지가 올바르게 저장됩니다.")

if __name__ == "__main__":
    clean_chat_data() 