#!/usr/bin/env python3
"""
회상 시스템 테스트 스크립트
- 태그 기반 회상 테스트
- 키워드 기반 회상 테스트
- 시퀀스 기반 회상 테스트
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_recall_engine import get_enhanced_recall_engine
from pymongo import MongoClient
from datetime import datetime

async def test_recall_system():
    """회상 시스템 테스트"""
    print("🧠 회상 시스템 테스트 시작")
    
    try:
        # MongoDB 연결
        mongo_client = MongoClient("mongodb://localhost:27017")
        db = mongo_client.get_database()
        
        # 테스트 데이터 삽입
        test_memories = [
            {
                "content": "내일 일본에 가요",
                "message": "내일 일본에 가요",
                "tags": ["일정", "여행", "일본"],
                "user_id": "test_user",
                "timestamp": datetime.now(),
                "source": "대화기록"
            },
            {
                "content": "그 다음날은 베트남어 시험이 있어요",
                "message": "그 다음날은 베트남어 시험이 있어요", 
                "tags": ["일정", "시험", "베트남어"],
                "user_id": "test_user",
                "timestamp": datetime.now(),
                "source": "대화기록"
            },
            {
                "content": "그 다음날은 스위스에서 친구가 와요",
                "message": "그 다음날은 스위스에서 친구가 와요",
                "tags": ["일정", "친구", "스위스"],
                "user_id": "test_user", 
                "timestamp": datetime.now(),
                "source": "대화기록"
            },
            {
                "content": "몇일전 비가 왔어요",
                "message": "몇일전 비가 왔어요",
                "tags": ["날씨", "비"],
                "user_id": "test_user",
                "timestamp": datetime.now(),
                "source": "대화기록"
            }
        ]
        
        # 기존 테스트 데이터 삭제
        db.memories.delete_many({"user_id": "test_user"})
        
        # 테스트 데이터 삽입
        result = db.memories.insert_many(test_memories)
        print(f"✅ 테스트 데이터 삽입 완료: {len(result.inserted_ids)}개")
        
        # 강화된 회상 엔진 초기화
        recall_engine = get_enhanced_recall_engine(mongo_client)
        
        # 테스트 쿼리들
        test_queries = [
            "다음주에 무슨일들이 있죠?",
            "다음주 일정이 뭐에요?",
            "다음주에 무슨일이 있죠?>",
            "비가 온게 언제죠?",
            "내일은 무슨일이 있죠? 제일정이 뭐죠?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 테스트 쿼리: {query}")
            
            # 회상 실행
            memories = await recall_engine.recall_memories(
                query=query,
                user_id="test_user",
                limit=5
            )
            
            print(f"📝 회상 결과: {len(memories)}개")
            for i, memory in enumerate(memories):
                content = memory.get("content", "") or memory.get("message", "")
                tags = memory.get("tags", [])
                print(f"  {i+1}. {content[:50]}... (태그: {tags})")
        
        print("\n✅ 회상 시스템 테스트 완료")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_recall_system()) 