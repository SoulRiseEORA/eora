#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from dotenv import load_dotenv

def test_openai_api():
    print("🔑 OpenAI API 키 테스트")
    print("=" * 40)
    
    # .env 파일 로드
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY", "")
    
    print(f"📝 API 키 로드: {'✅' if api_key else '❌'}")
    
    if api_key:
        print(f"🔍 키 형식: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else ''}")
        print(f"📏 키 길이: {len(api_key)} 문자")
        print(f"🎯 형식 확인: {'✅' if api_key.startswith('sk-proj-') else '❌'}")
        
        # OpenAI 클라이언트 테스트
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            print("📡 OpenAI 연결 테스트 중...")
            
            # 간단한 API 호출
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            print("✅ API 연결 성공!")
            print(f"📤 응답: {response.choices[0].message.content}")
            
        except Exception as e:
            print(f"❌ API 연결 실패: {e}")
            
            if "401" in str(e):
                print("🚨 API 키가 유효하지 않습니다!")
                print("📍 새로운 API 키가 필요합니다.")
            elif "insufficient" in str(e).lower():
                print("💳 OpenAI 크레딧이 부족합니다.")
            else:
                print("🔍 다른 문제가 있는 것 같습니다.")
    else:
        print("❌ .env 파일에 OPENAI_API_KEY가 없습니다.")
        
    print("\n" + "=" * 40)

if __name__ == "__main__":
    test_openai_api() 