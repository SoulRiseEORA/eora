import requests
import json

API_URL = "http://127.0.0.1:8001/api/chat"

# 테스트할 회상 유형
recall_types = [
    "normal",
    "window",
    "wisdom",
    "intuition"
]

user_id = "test_user"
session_id = "test_session"

for recall_type in recall_types:
    payload = {
        "message": f"테스트 회상 요청 ({recall_type})",
        "session_id": session_id,
        "user_id": user_id,
        "recall_type": recall_type
    }
    print(f"\n===== [recall_type: {recall_type}] =====")
    try:
        response = requests.post(API_URL, json=payload)
        if response.ok:
            data = response.json()
            print("응답:", json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"오류: {response.status_code}", response.text)
    except Exception as e:
        print(f"예외 발생: {e}") 