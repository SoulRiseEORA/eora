#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from dotenv import load_dotenv

def fix_api_key():
    print("🔧 OpenAI API 키 자동 수정")
    print("=" * 40)
    
    # .env 파일 경로
    env_path = ".env"
    
    if not os.path.exists(env_path):
        print("❌ .env 파일을 찾을 수 없습니다!")
        return
    
    # .env 파일 읽기
    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    print("📝 현재 .env 파일에서 API 키 확인...")
    
    # 현재 OPENAI_API_KEY 찾기
    current_match = re.search(r"OPENAI_API_KEY=(.+)", content)
    if current_match:
        current_key = current_match.group(1).strip()
        print(f"🔍 현재 키: {current_key[:10]}...{current_key[-4:]}")
        
        if current_key.endswith("TGcA"):
            print("⚠️ 이 키가 문제입니다! 교체합니다...")
            
            # OPENAI_API_KEY_1로 교체
            key1_match = re.search(r"OPENAI_API_KEY_1=(.+)", content)
            if key1_match:
                new_key = key1_match.group(1).strip()
                print(f"🔄 새로운 키: {new_key[:10]}...{new_key[-4:]}")
                
                # 교체
                content = re.sub(
                    r"OPENAI_API_KEY=.+",
                    f"OPENAI_API_KEY={new_key}",
                    content
                )
                
                # .env 파일 저장
                with open(env_path, "w", encoding="utf-8") as f:
                    f.write(content)
                
                print("✅ API 키 교체 완료!")
                print("🔄 서버를 재시작해주세요.")
                
                return True
            else:
                print("❌ OPENAI_API_KEY_1을 찾을 수 없습니다!")
        else:
            print("✅ 현재 키는 문제없어 보입니다.")
    else:
        print("❌ OPENAI_API_KEY를 찾을 수 없습니다!")
    
    return False

if __name__ == "__main__":
    success = fix_api_key()
    if success:
        print("\n🚀 다음 단계:")
        print("1. cd src")
        print("2. python -m uvicorn app:app --host 0.0.0.0 --port 8002 --reload")
        print("3. 금강2.docx 재학습")
    else:
        print("\n❌ 수동으로 .env 파일을 수정해주세요.") 