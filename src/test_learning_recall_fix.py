#!/usr/bin/env python3
"""
학습 데이터 불러오기 문제 해결 테스트
"""

import asyncio
import sys
import os
from datetime import datetime

# 현재 디렉토리를 파이썬 경로에 추가
sys.path.append('.')

async def test_learning_recall_fix():
    """학습 데이터 불러오기 수정 테스트"""
    print("🔧 학습 데이터 불러오기 수정 테스트")
    print("=" * 60)
    
    try:
        # 1. 먼저 학습 데이터 저장 테스트
        print("1️⃣ 학습 데이터 저장 테스트...")
        from mongodb_config import get_optimized_mongodb_connection
        from enhanced_learning_system import get_enhanced_learning_system
        
        client = get_optimized_mongodb_connection()
        if client is None:
            print("❌ MongoDB 연결 실패")
            return False
        
        learning_system = get_enhanced_learning_system(client)
        if learning_system is None:
            print("❌ 학습 시스템 초기화 실패")
            return False
        
        # 테스트 문서 학습
        test_documents = [
            {
                "content": "인공지능은 인간의 지능을 모방하는 컴퓨터 시스템입니다. 머신러닝, 딥러닝, 자연어처리 등의 기술을 포함합니다.",
                "filename": "ai_basics.txt",
                "category": "인공지능"
            },
            {
                "content": "마음챙김 명상은 현재 순간에 주의를 집중하는 수련법입니다. 호흡에 집중하며 생각과 감정을 관찰합니다.",
                "filename": "mindfulness.txt",
                "category": "명상"
            }
        ]
        
        saved_memory_ids = []
        for doc in test_documents:
            result = await learning_system.learn_document(
                content=doc["content"],
                filename=doc["filename"],
                category=doc["category"]
            )
            
            if result.get("success"):
                print(f"✅ '{doc['filename']}' 학습 성공")
                saved_memory_ids.append(result.get("saved_memories", []))
            else:
                print(f"❌ '{doc['filename']}' 학습 실패: {result.get('error')}")
                return False
        
        # 2. 기존 EORA 메모리 시스템으로 회상 테스트
        print("\n2️⃣ EORA 메모리 시스템 회상 테스트...")
        
        try:
            from eora_memory_system import EORAMemorySystem
            eora_memory = EORAMemorySystem()
            
            if eora_memory.is_connected():
                print("✅ EORA 메모리 시스템 연결 성공")
                
                test_queries = ["인공지능", "명상", "머신러닝", "호흡"]
                
                for query in test_queries:
                    print(f"\n   🔍 '{query}' 검색:")
                    
                    # enhanced_learning 타입으로 검색
                    results = await eora_memory.recall_learned_content(
                        query=query,
                        memory_type="enhanced_learning",
                        limit=3
                    )
                    
                    if results:
                        print(f"      ✅ EORA 검색 성공: {len(results)}개 결과")
                        for i, result in enumerate(results[:2]):
                            content = result.get('content', result.get('response', ''))
                            filename = result.get('filename', result.get('source_file', 'unknown'))
                            print(f"         📝 결과 {i+1}: {filename} - {content[:30]}...")
                    else:
                        print(f"      ⚠️ EORA 검색 결과 없음")
            else:
                print("❌ EORA 메모리 시스템 연결 실패")
                
        except Exception as e:
            print(f"❌ EORA 메모리 시스템 테스트 실패: {e}")
        
        # 3. 새로운 향상된 회상 시스템 테스트
        print("\n3️⃣ 향상된 회상 시스템 테스트...")
        
        try:
            from enhanced_recall_system import get_enhanced_recall_system
            
            enhanced_recall = get_enhanced_recall_system(client)
            
            if enhanced_recall.is_connected():
                print("✅ 향상된 회상 시스템 연결 성공")
                
                for query in test_queries:
                    print(f"\n   🔍 '{query}' 향상된 검색:")
                    
                    results = await enhanced_recall.recall_learning_data(
                        query=query,
                        limit=5
                    )
                    
                    if results:
                        print(f"      ✅ 향상된 검색 성공: {len(results)}개 결과")
                        for i, result in enumerate(results[:3]):
                            content = result.get('content', '')
                            filename = result.get('filename', 'unknown')
                            score = result.get('relevance_score', 0)
                            memory_type = result.get('memory_type', 'unknown')
                            print(f"         📝 결과 {i+1}: {filename} ({memory_type}) - 점수: {score:.1f}")
                            print(f"            내용: {content[:40]}...")
                    else:
                        print(f"      ⚠️ 향상된 검색 결과 없음")
                        
                # 통계 확인
                print(f"\n   📊 학습 데이터 통계:")
                stats = await enhanced_recall.get_learning_statistics()
                if "error" not in stats:
                    print(f"      - 전체 메모리: {stats.get('total_memories', 0)}개")
                    print(f"      - 강화된 학습: {stats.get('enhanced_learning', 0)}개")
                    print(f"      - 문서 청크: {stats.get('document_chunks', 0)}개")
                    
                    categories = stats.get('categories', [])
                    if categories:
                        print(f"      - 카테고리별:")
                        for cat in categories[:5]:
                            print(f"        * {cat['_id']}: {cat['count']}개")
                else:
                    print(f"      ❌ 통계 조회 실패: {stats.get('error')}")
            else:
                print("❌ 향상된 회상 시스템 연결 실패")
                
        except Exception as e:
            print(f"❌ 향상된 회상 시스템 테스트 실패: {e}")
            import traceback
            print(f"상세 오류: {traceback.format_exc()}")
        
        # 4. 직접 MongoDB 쿼리로 확인
        print("\n4️⃣ 직접 MongoDB 쿼리 확인...")
        
        try:
            from mongodb_config import get_optimized_database
            db = get_optimized_database()
            
            # 저장된 학습 데이터 직접 확인
            enhanced_count = db.memories.count_documents({"memory_type": "enhanced_learning"})
            print(f"✅ enhanced_learning 메모리: {enhanced_count}개")
            
            if enhanced_count > 0:
                # 최근 저장된 학습 데이터 확인
                recent_learning = list(db.memories.find(
                    {"memory_type": "enhanced_learning"}
                ).sort("timestamp", -1).limit(3))
                
                print("📚 최근 학습 데이터:")
                for i, mem in enumerate(recent_learning):
                    print(f"   {i+1}. 파일: {mem.get('source_file', 'N/A')}")
                    print(f"      카테고리: {mem.get('category', 'N/A')}")
                    print(f"      내용: {mem.get('response', '')[:40]}...")
                    print(f"      시간: {mem.get('timestamp', 'N/A')}")
            
            # 텍스트 검색 테스트
            for query in ["인공지능", "명상"][:2]:  # 2개만 테스트
                print(f"\n   🔍 '{query}' 직접 검색:")
                
                search_results = list(db.memories.find({
                    "memory_type": "enhanced_learning",
                    "$or": [
                        {"response": {"$regex": query, "$options": "i"}},
                        {"category": {"$regex": query, "$options": "i"}},
                        {"tags": {"$in": [query]}}
                    ]
                }).limit(3))
                
                print(f"      📊 직접 검색 결과: {len(search_results)}개")
                
                if search_results:
                    for j, result in enumerate(search_results):
                        filename = result.get('source_file', 'unknown')
                        category = result.get('category', 'N/A')
                        print(f"         📄 {j+1}. {filename} ({category})")
                        
        except Exception as e:
            print(f"❌ 직접 MongoDB 쿼리 실패: {e}")
        
        print("\n" + "=" * 60)
        print("🎯 학습 데이터 불러오기 테스트 완료!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")
        return False

def main():
    """메인 실행"""
    print("🚀 학습 데이터 불러오기 수정 테스트")
    print("=" * 60)
    
    # 비동기 테스트 실행
    result = asyncio.run(test_learning_recall_fix())
    
    if result:
        print("\n✅ 테스트 성공!")
        print("💡 학습 데이터 불러오기 문제가 해결되었는지 확인해주세요.")
        sys.exit(0)
    else:
        print("\n❌ 테스트 실패!")
        print("💡 추가 디버깅이 필요합니다.")
        sys.exit(1)

if __name__ == "__main__":
    main()