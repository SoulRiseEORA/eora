#!/usr/bin/env python3
"""
OpenAI API 키 로드 테스트
"""

import os
from dotenv import load_dotenv

# dotenv 로드
load_dotenv()

print("=== OpenAI API 키 로드 테스트 ===")
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY', 'None')}")
print(f"OPENAI_API_KEY 길이: {len(os.getenv('OPENAI_API_KEY', ''))}")
print(f"OPENAI_API_KEY 시작: {os.getenv('OPENAI_API_KEY', '')[:10]}...")

# OpenAI 클라이언트 테스트 (1.3.7 버전)
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    print("✅ OpenAI 클라이언트 생성 성공")
    
    # 간단한 API 호출 테스트
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "안녕하세요"}],
        max_tokens=10
    )
    print(f"✅ OpenAI API 호출 성공: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ OpenAI API 오류: {e}") 