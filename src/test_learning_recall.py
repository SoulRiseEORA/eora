#!/usr/bin/env python3
"""
학습하기와 회상 기능을 정밀하게 테스트하는 스크립트
"""

import asyncio
import sys
import os
sys.path.append('.')

from datetime import datetime

async def test_learning_and_recall():
    """학습과 회상 기능을 단계별로 테스트"""
    
    print("=" * 60)
    print("🔬 학습하기 & 회상 기능 정밀 테스트")
    print("=" * 60)
    
    # 1단계: EORAMemorySystem 초기화
    print("\n🔍 1단계: EORAMemorySystem 초기화 테스트")
    try:
        from eora_memory_system import EORAMemorySystem
        memory_system = EORAMemorySystem()
        
        print(f"   ✅ EORAMemorySystem 생성 완료")
        print(f"   🔗 MongoDB 연결 상태: {memory_system.is_connected()}")
        print(f"   🔌 클라이언트: {memory_system.client is not None}")
        print(f"   💾 데이터베이스: {memory_system.db is not None}")
        print(f"   📝 메모리 컬렉션: {memory_system.memories is not None}")
        print(f"   🧠 memory_manager: {memory_system.memory_manager is not None}")
        
        if memory_system.memory_manager:
            manager_type = type(memory_system.memory_manager).__name__
            print(f"   🎯 memory_manager 타입: {manager_type}")
            
        if not memory_system.is_connected():
            print("   ❌ MongoDB 연결 실패 - 테스트 중단")
            return False
            
    except Exception as e:
        print(f"   ❌ EORAMemorySystem 초기화 실패: {e}")
        return False
    
    # 2단계: 학습 기능 테스트 (store_memory)
    print("\n🔍 2단계: 학습 기능 테스트")
    
    test_content = "이것은 테스트용 학습 내용입니다. Python 프로그래밍에 대한 내용을 담고 있습니다."
    test_metadata = {
        "filename": "test_document.txt",
        "file_extension": ".txt", 
        "chunk_index": 0,
        "total_chunks": 1,
        "source": "file_learning",
        "admin_shared": True,
        "uploaded_by_admin": True,
        "uploader_email": "test@admin.com"
    }
    
    try:
        print(f"   📝 테스트 내용: {test_content}")
        print(f"   📋 메타데이터: {test_metadata}")
        
        # store_memory 호출
        store_result = await memory_system.store_memory(
            content=test_content,
            memory_type="document_chunk",
            user_id="test@admin.com",
            metadata=test_metadata
        )
        
        print(f"   🔍 저장 결과: {store_result}")
        
        if store_result.get("success"):
            memory_id = store_result.get("memory_id")
            print(f"   ✅ 학습 성공! 메모리 ID: {memory_id}")
        else:
            print(f"   ❌ 학습 실패: {store_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ 학습 테스트 예외: {e}")
        import traceback
        print(f"   🔍 상세 오류: {traceback.format_exc()}")
        return False
    
    # 3단계: 회상 기능 테스트 (recall_learned_content)
    print("\n🔍 3단계: 회상 기능 테스트")
    
    test_queries = [
        "Python",
        "프로그래밍", 
        "테스트",
        "test_document"
    ]
    
    for query in test_queries:
        try:
            print(f"\n   🔎 검색어: '{query}'")
            
            # recall_learned_content 호출
            recall_results = await memory_system.recall_learned_content(
                query=query,
                memory_type="document_chunk",
                limit=5
            )
            
            print(f"   📊 회상 결과 수: {len(recall_results)}")
            
            if recall_results:
                for i, result in enumerate(recall_results):
                    content_preview = result.get("content", "")[:50]
                    filename = result.get("filename", "unknown")
                    print(f"   📄 결과 {i+1}: {filename} - {content_preview}...")
                print(f"   ✅ 회상 성공!")
            else:
                print(f"   ⚠️ 회상 결과 없음")
                
        except Exception as e:
            print(f"   ❌ 회상 테스트 예외 ({query}): {e}")
    
    # 4단계: Enhanced Recall 테스트
    print("\n🔍 4단계: Enhanced Recall 테스트")
    
    try:
        enhanced_results = await memory_system.enhanced_recall(
            query="Python 프로그래밍",
            user_id="test@admin.com",
            limit=3
        )
        
        print(f"   📊 향상된 회상 결과 수: {len(enhanced_results)}")
        
        if enhanced_results:
            for i, result in enumerate(enhanced_results):
                if isinstance(result, dict):
                    content_preview = result.get("content", str(result))[:50]
                else:
                    content_preview = str(result)[:50]
                print(f"   🎯 향상된 결과 {i+1}: {content_preview}...")
            print(f"   ✅ 향상된 회상 성공!")
        else:
            print(f"   ⚠️ 향상된 회상 결과 없음")
            
    except Exception as e:
        print(f"   ❌ 향상된 회상 테스트 예외: {e}")
        import traceback
        print(f"   🔍 상세 오류: {traceback.format_exc()}")
    
    # 5단계: 데이터베이스 직접 확인
    print("\n🔍 5단계: 데이터베이스 직접 확인")
    
    try:
        # MongoDB에서 직접 조회
        total_memories = memory_system.memories.count_documents({})
        test_memories = memory_system.memories.count_documents({"filename": "test_document.txt"})
        
        print(f"   📊 전체 메모리 수: {total_memories}")
        print(f"   📊 테스트 메모리 수: {test_memories}")
        
        # 최근 메모리 확인
        recent_memories = list(memory_system.memories.find({}).sort("timestamp", -1).limit(3))
        print(f"   📊 최근 메모리 3개:")
        
        for i, mem in enumerate(recent_memories):
            content_preview = mem.get("content", "")[:30]
            filename = mem.get("filename", "unknown")
            memory_type = mem.get("memory_type", "unknown")
            timestamp = mem.get("timestamp", "unknown")
            print(f"     {i+1}. {filename} ({memory_type}) - {content_preview}... - {timestamp}")
        
    except Exception as e:
        print(f"   ❌ 데이터베이스 직접 확인 실패: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 테스트 완료!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    asyncio.run(test_learning_and_recall())