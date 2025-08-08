#!/usr/bin/env python3
"""
학습된 데이터 저장 및 불러오기 상태 확인 스크립트
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, List

# 현재 디렉토리를 파이썬 경로에 추가
sys.path.append('.')

async def check_learning_data():
    """학습된 데이터 상태 확인"""
    print("🔍 학습된 데이터 상태 확인")
    print("=" * 60)
    
    try:
        # 1. MongoDB 연결 확인
        print("1️⃣ MongoDB 연결 확인...")
        from mongodb_config import get_optimized_mongodb_connection, get_optimized_database
        
        client = get_optimized_mongodb_connection()
        if client is None:
            print("❌ MongoDB 연결 실패")
            return False
        
        db = get_optimized_database()
        if db is None:
            print("❌ 데이터베이스 연결 실패")
            return False
        
        print("✅ MongoDB 연결 성공")
        
        # 2. 메모리 컬렉션 확인
        print("\n2️⃣ 메모리 컬렉션 데이터 확인...")
        memories = db.memories
        
        # 전체 메모리 수
        total_memories = memories.count_documents({})
        print(f"📊 전체 메모리 수: {total_memories}")
        
        # 학습 관련 메모리 타입별 분석
        memory_types = memories.distinct("memory_type")
        print(f"📋 메모리 타입들: {memory_types}")
        
        for memory_type in memory_types:
            count = memories.count_documents({"memory_type": memory_type})
            print(f"   - {memory_type}: {count}개")
        
        # 3. 강화된 학습 시스템으로 저장된 데이터 확인
        print("\n3️⃣ 강화된 학습 시스템 데이터 확인...")
        enhanced_learning_memories = list(memories.find({"memory_type": "enhanced_learning"}))
        print(f"📚 강화된 학습 메모리: {len(enhanced_learning_memories)}개")
        
        if enhanced_learning_memories:
            for i, mem in enumerate(enhanced_learning_memories[:3]):  # 최대 3개만 표시
                print(f"   📄 메모리 {i+1}:")
                print(f"      - ID: {mem.get('_id')}")
                print(f"      - 파일명: {mem.get('source_file', 'N/A')}")
                print(f"      - 카테고리: {mem.get('category', 'N/A')}")
                print(f"      - 청크 인덱스: {mem.get('chunk_index', 'N/A')}")
                print(f"      - 내용 미리보기: {mem.get('response', '')[:50]}...")
                print(f"      - 타임스탬프: {mem.get('timestamp', 'N/A')}")
        
        # 4. document_chunk 타입 데이터 확인
        print("\n4️⃣ document_chunk 타입 데이터 확인...")
        document_chunks = list(memories.find({"memory_type": "document_chunk"}))
        print(f"📄 문서 청크: {len(document_chunks)}개")
        
        if document_chunks:
            for i, chunk in enumerate(document_chunks[:3]):  # 최대 3개만 표시
                print(f"   📄 청크 {i+1}:")
                print(f"      - ID: {chunk.get('_id')}")
                print(f"      - 파일명: {chunk.get('filename', 'N/A')}")
                print(f"      - 내용 미리보기: {chunk.get('content', '')[:50]}...")
                print(f"      - admin_shared: {chunk.get('metadata', {}).get('admin_shared', 'N/A')}")
                print(f"      - 소스: {chunk.get('source', 'N/A')}")
        
        # 5. 회상 기능 테스트
        print("\n5️⃣ 회상 기능 테스트...")
        
        try:
            from eora_memory_system import EORAMemorySystem
            memory_system = EORAMemorySystem()
            
            if memory_system.is_connected():
                print("✅ EORA 메모리 시스템 연결 성공")
                
                # 테스트 쿼리들
                test_queries = ["Python", "프로그래밍", "명상", "영업시간"]
                
                for query in test_queries:
                    print(f"\n   🔍 '{query}' 검색 테스트:")
                    
                    # enhanced_learning 타입으로 검색
                    results1 = await memory_system.recall_learned_content(
                        query=query,
                        memory_type="enhanced_learning",
                        limit=3
                    )
                    print(f"      enhanced_learning 결과: {len(results1)}개")
                    
                    # document_chunk 타입으로 검색
                    results2 = await memory_system.recall_learned_content(
                        query=query,
                        memory_type="document_chunk",
                        limit=3
                    )
                    print(f"      document_chunk 결과: {len(results2)}개")
                    
                    # 타입 제한 없이 검색
                    results3 = await memory_system.recall_learned_content(
                        query=query,
                        limit=3
                    )
                    print(f"      전체 검색 결과: {len(results3)}개")
                    
                    # 결과 미리보기
                    if results1 or results2 or results3:
                        all_results = results1 + results2 + results3
                        unique_results = {r['_id']: r for r in all_results}.values()
                        for j, result in enumerate(list(unique_results)[:2]):  # 최대 2개
                            content_preview = result.get('content', result.get('response', ''))[:30]
                            filename = result.get('filename', result.get('source_file', 'unknown'))
                            print(f"         📝 결과 {j+1}: {filename} - {content_preview}...")
            else:
                print("❌ EORA 메모리 시스템 연결 실패")
                
        except Exception as e:
            print(f"❌ EORA 메모리 시스템 테스트 실패: {e}")
        
        # 6. 인덱스 확인
        print("\n6️⃣ 인덱스 확인...")
        try:
            indexes = memories.list_indexes()
            print("📋 생성된 인덱스:")
            for index in indexes:
                print(f"   - {index}")
        except Exception as e:
            print(f"❌ 인덱스 확인 실패: {e}")
        
        # 7. 최근 저장된 메모리 확인
        print("\n7️⃣ 최근 저장된 메모리 확인...")
        recent_memories = list(memories.find({}).sort("timestamp", -1).limit(5))
        print(f"📅 최근 메모리 5개:")
        
        for i, mem in enumerate(recent_memories):
            print(f"   {i+1}. 타입: {mem.get('memory_type', 'N/A')}")
            print(f"      파일: {mem.get('filename', mem.get('source_file', 'N/A'))}")
            print(f"      시간: {mem.get('timestamp', 'N/A')}")
            content = mem.get('content', mem.get('response', ''))
            print(f"      내용: {content[:30]}...")
        
        print("\n" + "=" * 60)
        print("🎯 학습 데이터 상태 확인 완료!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 확인 중 오류 발생: {e}")
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")
        return False

def main():
    """메인 실행"""
    print("🚀 학습된 데이터 상태 확인 스크립트")
    print("=" * 60)
    
    # 비동기 테스트 실행
    result = asyncio.run(check_learning_data())
    
    if result:
        print("\n✅ 확인 완료!")
    else:
        print("\n❌ 확인 실패!")

if __name__ == "__main__":
    main()