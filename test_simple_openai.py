#!/usr/bin/env python3
"""
OpenAI API 직접 테스트
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일 로드
load_dotenv()

print("=== OpenAI API 직접 테스트 ===")

# API 키 확인
api_key = os.getenv("OPENAI_API_KEY")
print(f"API 키: {api_key[:20]}..." if api_key else "API 키 없음")

if not api_key:
    print("❌ API 키가 없습니다.")
    exit(1)

try:
    # OpenAI 클라이언트 생성
    client = OpenAI(api_key=api_key)
    print("✅ OpenAI 클라이언트 생성 성공")
    
    # 간단한 API 호출
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": "안녕하세요"}
        ],
        max_tokens=50
    )
    
    print(f"✅ OpenAI API 호출 성공")
    print(f"응답: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ OpenAI API 오류: {e}")
    import traceback
    traceback.print_exc() 