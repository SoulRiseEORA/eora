#!/usr/bin/env python3
import requests

# 세션 목록 조회
print("1. 세션 목록 조회")
r = requests.get('http://127.0.0.1:8001/api/sessions')
data = r.json()
sessions = data.get('sessions', [])
print(f"세션 수: {len(sessions)}")

if sessions:
    first_session = sessions[0]
    print(f"첫 번째 세션: {first_session['id']}")
    
    # 첫 번째 세션의 메시지 조회
    print("\n2. 첫 번째 세션 메시지 조회")
    r2 = requests.get(f'http://127.0.0.1:8001/api/sessions/{first_session["id"]}/messages')
    data2 = r2.json()
    messages = data2.get('messages', [])
    print(f"메시지 수: {len(messages)}")
    
    for i, msg in enumerate(messages):
        print(f"{i+1}. [{msg['role']}] {msg['content']}")
else:
    print("세션이 없습니다.") 