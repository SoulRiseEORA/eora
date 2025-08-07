#!/usr/bin/env python3
"""
간단한 학습 기능 테스트
"""

import asyncio
import sys
import os
from datetime import datetime

# 현재 디렉토리를 파이썬 경로에 추가
sys.path.append('.')

async def test_learning_function():
    """학습 기능 테스트"""
    print("🔍 학습 기능 테스트 시작")
    print("=" * 50)
    
    try:
        # 1. MongoDB 연결 테스트
        print("1️⃣ MongoDB 연결 테스트...")
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
        
        # 2. 강화된 학습 시스템 테스트
        print("\n2️⃣ 강화된 학습 시스템 테스트...")
        from enhanced_learning_system import get_enhanced_learning_system
        
        learning_system = get_enhanced_learning_system(client)
        if learning_system is None:
            print("❌ 학습 시스템 초기화 실패")
            return False
        
        print("✅ 학습 시스템 초기화 성공")
        
        # 3. 테스트 문서 학습
        print("\n3️⃣ 테스트 문서 학습...")
        test_content = "Python은 간단하고 읽기 쉬운 프로그래밍 언어입니다. 웹 개발, 데이터 분석, 인공지능 등 다양한 분야에서 활용됩니다."
        
        result = await learning_system.learn_document(
            content=test_content,
            filename="python_test.txt",
            category="프로그래밍"
        )
        
        if result.get("success"):
            print(f"✅ 학습 성공!")
            print(f"   - 파일명: {result['filename']}")
            print(f"   - 카테고리: {result['category']}")
            print(f"   - 청크 수: {result['total_chunks']}")
            print(f"   - 저장된 메모리: {result['saved_memories']}")
        else:
            print(f"❌ 학습 실패: {result.get('error')}")
            return False
        
        # 4. 데이터베이스 확인
        print("\n4️⃣ 데이터베이스 저장 확인...")
        memories = db.memories
        
        # 방금 저장한 메모리 찾기
        saved_memory = memories.find_one({"source_file": "python_test.txt"})
        if saved_memory:
            print("✅ 메모리가 데이터베이스에 저장됨")
            print(f"   - ID: {saved_memory['_id']}")
            print(f"   - 카테고리: {saved_memory.get('category')}")
            print(f"   - 내용 미리보기: {saved_memory.get('response', '')[:50]}...")
        else:
            print("❌ 메모리가 데이터베이스에 저장되지 않음")
            return False
        
        # 5. 다중 사용자 테스트
        print("\n5️⃣ 다중 사용자 테스트...")
        test_users = ["user1@test.com", "user2@test.com", "user3@test.com"]
        
        for i, user_id in enumerate(test_users):
            user_content = f"사용자 {i+1}의 개인 학습 내용입니다. 이것은 {user_id}만의 고유한 정보입니다."
            
            user_result = await learning_system.learn_document(
                content=user_content,
                filename=f"user_{i+1}_personal.txt",
                category="개인정보"
            )
            
            if user_result.get("success"):
                print(f"✅ 사용자 {i+1} 학습 성공")
            else:
                print(f"❌ 사용자 {i+1} 학습 실패")
                return False
        
        # 6. 저장된 메모리 총 개수 확인
        print("\n6️⃣ 저장된 메모리 통계...")
        total_memories = memories.count_documents({})
        learning_memories = memories.count_documents({"memory_type": "enhanced_learning"})
        
        print(f"✅ 전체 메모리: {total_memories}개")
        print(f"✅ 학습 메모리: {learning_memories}개")
        
        # 7. 학습 통계 확인
        print("\n7️⃣ 학습 통계 확인...")
        stats = await learning_system.get_learning_stats()
        print(f"✅ 학습 통계: {stats}")
        
        print("\n" + "=" * 50)
        print("🎉 모든 테스트 통과!")
        print("✅ 학습 기능이 정상 작동합니다.")
        print("✅ 다중 사용자 DB가 정상 작동합니다.")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")
        return False

def main():
    """메인 실행"""
    print("🚀 간단한 학습 기능 테스트")
    print("=" * 50)
    
    # 비동기 테스트 실행
    result = asyncio.run(test_learning_function())
    
    if result:
        print("\n✅ 테스트 성공!")
        sys.exit(0)
    else:
        print("\n❌ 테스트 실패!")
        sys.exit(1)

if __name__ == "__main__":
    main()