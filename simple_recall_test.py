#!/usr/bin/env python3
"""
간단한 회상 시스템 테스트
"""

import asyncio
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

async def test_basic_recall():
    """기본 회상 테스트"""
    print("🧠 기본 회상 시스템 테스트")
    
    try:
        # 간단한 회상 시뮬레이션
        test_memories = [
            {
                "content": "내일 일본에 가요",
                "tags": ["일정", "여행", "일본"],
                "source": "대화기록"
            },
            {
                "content": "그 다음날은 베트남어 시험이 있어요",
                "tags": ["일정", "시험", "베트남어"],
                "source": "대화기록"
            },
            {
                "content": "그 다음날은 스위스에서 친구가 와요",
                "tags": ["일정", "친구", "스위스"],
                "source": "대화기록"
            },
            {
                "content": "몇일전 비가 왔어요",
                "tags": ["날씨", "비"],
                "source": "대화기록"
            }
        ]
        
        # 테스트 쿼리들
        test_queries = [
            "다음주에 무슨일들이 있죠?",
            "비가 온게 언제죠?",
            "내일은 무슨일이 있죠?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 테스트 쿼리: {query}")
            
            # 간단한 키워드 매칭
            matched_memories = []
            query_words = query.lower().split()
            
            for memory in test_memories:
                content = memory["content"].lower()
                tags = [tag.lower() for tag in memory["tags"]]
                
                # 키워드 매칭
                for word in query_words:
                    if word in content or any(word in tag for tag in tags):
                        matched_memories.append(memory)
                        break
            
            print(f"📝 회상 결과: {len(matched_memories)}개")
            for i, memory in enumerate(matched_memories):
                content = memory["content"]
                tags = memory["tags"]
                source = memory["source"]
                print(f"  {i+1}. [{source}] [태그: {', '.join(tags)}] {content}")
        
        print("\n✅ 기본 회상 테스트 완료")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_basic_recall()) 