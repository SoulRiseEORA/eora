#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
import os
from dotenv import load_dotenv

def main():
    print("🔍 EORA AI 문제 진단 시작")
    print("=" * 50)
    
    # .env 파일 로드
    load_dotenv()
    
    # 1. MongoDB 데이터 확인
    print("\n📊 1. MongoDB 데이터 확인:")
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017")
        db = client["eora_ai"]
        
        total_memories = db.memories.count_documents({})
        learning_materials = db.memories.count_documents({"memory_type": "learning_material"})
        
        print(f"   - 총 메모리: {total_memories:,}개")
        print(f"   - 학습 자료: {learning_materials:,}개")
        
        if total_memories > 0:
            print("   🔍 최신 3개 메모리:")
            for i, doc in enumerate(db.memories.find().sort("timestamp", -1).limit(3), 1):
                memory_type = doc.get("memory_type", "N/A")
                content_length = len(doc.get("content", ""))
                print(f"     {i}. {memory_type}: {content_length}자")
        else:
            print("   ❌ 메모리 데이터가 없습니다!")
            
    except Exception as e:
        print(f"   ❌ MongoDB 연결 실패: {e}")
    
    # 2. OpenAI API 키 확인
    print("\n🔑 2. OpenAI API 키 확인:")
    api_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OPENAI_API_KEY_1": os.getenv("OPENAI_API_KEY_1", ""),
        "OPENAI_API_KEY_2": os.getenv("OPENAI_API_KEY_2", ""),
        "OPENAI_API_KEY_3": os.getenv("OPENAI_API_KEY_3", ""),
        "OPENAI_API_KEY_4": os.getenv("OPENAI_API_KEY_4", ""),
        "OPENAI_API_KEY_5": os.getenv("OPENAI_API_KEY_5", ""),
    }
    
    for key_name, key_value in api_keys.items():
        if key_value:
            print(f"   - {key_name}: {key_value[:10]}...{key_value[-4:]} ({len(key_value)}자)")
        else:
            print(f"   - {key_name}: 없음")
    
    # 3. 현재 사용 중인 키 확인
    current_key = os.getenv("OPENAI_API_KEY", "")
    if current_key:
        print(f"\n📍 현재 사용 중인 키: {current_key[:10]}...{current_key[-4:]}")
        if current_key.endswith("TGcA"):
            print("   ⚠️ 이 키가 401 오류를 발생시키고 있습니다!")
            print("   💡 다른 키로 교체가 필요합니다.")
    
    print("\n" + "=" * 50)
    print("🎯 결론:")
    if total_memories == 0:
        print("❌ 학습 데이터가 저장되지 않았음")
    else:
        print("✅ 학습 데이터 저장 완료")
        
    if current_key.endswith("TGcA"):
        print("❌ OpenAI API 키 문제 있음")
    else:
        print("✅ OpenAI API 키 정상")

if __name__ == "__main__":
    main() 