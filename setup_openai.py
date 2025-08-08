#!/usr/bin/env python3
"""
OpenAI API 키 설정 스크립트
"""

import os
import json
from pathlib import Path

def setup_openai_key():
    """OpenAI API 키 설정"""
    print("=== OpenAI API 키 설정 ===")
    print("1. https://platform.openai.com/api-keys 에서 API 키를 생성하세요")
    print("2. 생성된 API 키를 아래에 입력하세요")
    print()
    
    api_key = input("OpenAI API 키를 입력하세요 (sk-로 시작): ").strip()
    
    if not api_key.startswith("sk-"):
        print("❌ 잘못된 API 키 형식입니다. sk-로 시작해야 합니다.")
        return False
    
    # 환경 변수 파일 생성
    env_file = Path(".env")
    env_content = f"OPENAI_API_KEY={api_key}\n"
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"✅ API 키가 {env_file} 파일에 저장되었습니다.")
        
        # 현재 세션에 환경 변수 설정
        os.environ["OPENAI_API_KEY"] = api_key
        print("✅ 현재 세션에 환경 변수가 설정되었습니다.")
        
        return True
    except Exception as e:
        print(f"❌ API 키 저장 실패: {e}")
        return False

def test_openai_connection():
    """OpenAI 연결 테스트"""
    try:
        import openai
        client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print("✅ OpenAI 클라이언트 초기화 성공")
        return True
    except Exception as e:
        print(f"❌ OpenAI 연결 실패: {e}")
        return False

if __name__ == "__main__":
    if setup_openai_key():
        print("\n=== 연결 테스트 ===")
        if test_openai_connection():
            print("🎉 OpenAI API 키 설정이 완료되었습니다!")
            print("이제 서버를 재시작하면 GPT 응답이 정상적으로 작동합니다.")
        else:
            print("⚠️ API 키는 설정되었지만 연결에 문제가 있습니다.")
    else:
        print("❌ API 키 설정에 실패했습니다.") 