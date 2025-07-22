#!/usr/bin/env python3
"""
OpenAI API 테스트 스크립트 - 수정된 버전
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일 로드
load_dotenv(dotenv_path="../.env")

def test_openai_api():
    """OpenAI API 테스트"""
    print("=== OpenAI API 테스트 (수정된 버전) ===")
    
    # API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
        return
    
    print(f"API 키: {api_key[:20]}...")
    
    try:
        # OpenAI 클라이언트 생성
        client = OpenAI(
            api_key=api_key,
            # proxies 인수 제거 - httpx 0.28.1 호환성
        )
        print("✅ OpenAI 클라이언트 생성 성공")
        
        # 간단한 API 호출 테스트
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "안녕하세요"}
            ],
            max_tokens=50
        )
        
        print("✅ OpenAI API 호출 성공")
        print(f"응답: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ OpenAI API 오류: {e}")

if __name__ == "__main__":
    test_openai_api() 