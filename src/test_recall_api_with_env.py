#!/usr/bin/env python3
"""
회상 API 테스트 (환경변수 포함)
"""

import requests
import json
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# OpenAI API 키 확인
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print("✅ .env에서 OPENAI_API_KEY를 성공적으로 불러왔습니다.")
else:
    print("❌ .env에서 OPENAI_API_KEY를 불러올 수 없습니다.")

# 테스트할 recall_type들
recall_types = ["normal", "window", "wisdom", "intuition"]

# API 엔드포인트
url = "http://127.0.0.1:8001/api/chat"

for recall_type in recall_types:
    print(f"\n===== [recall_type: {recall_type}] =====")
    
    # 요청 데이터 (첫 번째 엔드포인트용)
    data = {
        "message": f"실제 AI 응답 검증 ({recall_type})",
        "session_id": f"test_session_{recall_type}",
        "user_id": "test_user_123",  # user_id 추가
        "recall_type": recall_type
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"오류: HTTP {response.status_code}")
            print(f"응답: {response.text}")
    except Exception as e:
        print(f"예외 발생: {e}") 