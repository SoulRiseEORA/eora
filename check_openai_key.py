#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI API 키 상태 확인 스크립트
"""

import os
from dotenv import load_dotenv

def check_openai_keys():
    """OpenAI API 키 상태를 확인합니다."""
    
    print("🔍 OpenAI API 키 상태 확인")
    print("=" * 50)
    
    # .env 파일 로드
    try:
        load_dotenv()
        print("✅ .env 파일 로드 성공")
    except Exception as e:
        print(f"⚠️ .env 파일 로드 실패: {e}")
    
    # 가능한 모든 OpenAI API 키 환경변수 확인
    possible_keys = [
        "OPENAI_API_KEY",
        "OPENAI_API_KEY_1", 
        "OPENAI_API_KEY_2",
        "OPENAI_API_KEY_3",
        "OPENAI_KEY",
        "API_KEY",
        "GPT_API_KEY"
    ]
    
    print(f"\n📊 전체 환경변수 개수: {len(os.environ)}")
    
    # API 관련 환경변수 찾기
    env_keys = list(os.environ.keys())
    api_related_keys = [k for k in env_keys if any(word in k.upper() for word in ['OPENAI', 'API', 'GPT'])]
    
    if api_related_keys:
        print(f"🔍 API 관련 환경변수들: {api_related_keys}")
    else:
        print("⚠️ API 관련 환경변수가 전혀 없습니다!")
    
    print("\n🔑 OpenAI API 키 상태:")
    valid_key_found = False
    
    for key_name in possible_keys:
        key_value = os.getenv(key_name)
        if key_value:
            if key_value.startswith("sk-"):
                print(f"   ✅ {key_name}: 유효함 (sk-...{key_value[-8:]})")
                valid_key_found = True
            else:
                print(f"   ❌ {key_name}: 유효하지 않음 ({key_value[:15]}...)")
        else:
            print(f"   ❌ {key_name}: 미설정")
    
    print("\n" + "=" * 50)
    if valid_key_found:
        print("✅ 유효한 OpenAI API 키를 찾았습니다!")
        
        # 간단한 API 테스트
        try:
            import openai
            api_key = None
            for key_name in possible_keys:
                key_value = os.getenv(key_name)
                if key_value and key_value.startswith("sk-"):
                    api_key = key_value
                    break
            
            if api_key:
                client = openai.OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
                print("🎉 OpenAI API 연결 테스트 성공!")
                print(f"📝 응답: {response.choices[0].message.content}")
            
        except Exception as e:
            print(f"❌ OpenAI API 연결 테스트 실패: {e}")
            
    else:
        print("❌ 유효한 OpenAI API 키가 없습니다!")
        print("\n💡 해결 방법:")
        print("1. .env 파일에 OPENAI_API_KEY=sk-proj-your-key-here 추가")
        print("2. 환경변수로 OPENAI_API_KEY 설정")
        print("3. Railway 환경에서는 Variables에 OPENAI_API_KEY 설정")

if __name__ == "__main__":
    check_openai_keys() 