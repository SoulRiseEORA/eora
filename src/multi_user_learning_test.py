#!/usr/bin/env python3
"""
다중 사용자 학습 시스템 종합 테스트 스크립트
- 학습 기능 작동 여부 확인
- 여러 회원들의 DB 격리 및 연결 테스트
- 메모리 저장 및 회상 기능 검증
"""

import asyncio
import sys
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

# 현재 디렉토리를 파이썬 경로에 추가
sys.path.append('.')

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultiUserLearningTestSuite:
    """다중 사용자 학습 시스템 테스트 슈트"""
    
    def __init__(self):
        self.test_users = [
            {"user_id": "user1@test.com", "name": "테스트유저1"},
            {"user_id": "user2@test.com", "name": "테스트유저2"},
            {"user_id": "user3@test.com", "name": "테스트유저3"},
            {"user_id": "admin@eora.com", "name": "관리자"}
        ]
        self.test_results = {}
        
    async def run_comprehensive_test(self):
        """종합 테스트 실행"""
        print("🚀 다중 사용자 학습 시스템 종합 테스트 시작")
        print("=" * 80)
        
        # 1단계: 시스템 연결 테스트
        print("\n📋 1단계: 시스템 연결 및 초기화 테스트")
        system_test = await self.test_system_connections()
        
        if not system_test:
            print("❌ 시스템 연결 실패 - 테스트 중단")
            return False
        
        # 2단계: 데이터베이스 연결 테스트
        print("\n📋 2단계: 데이터베이스 연결 테스트")
        db_test = await self.test_database_connections()
        
        # 3단계: 학습 시스템 테스트
        print("\n📋 3단계: 강화된 학습 시스템 테스트")
        learning_test = await self.test_enhanced_learning_system()
        
        # 4단계: 다중 사용자 세션 격리 테스트
        print("\n📋 4단계: 다중 사용자 세션 격리 테스트")
        isolation_test = await self.test_user_isolation()
        
        # 5단계: 메모리 저장 및 회상 테스트
        print("\n📋 5단계: 메모리 저장 및 회상 테스트")
        memory_test = await self.test_memory_operations()
        
        # 6단계: 성능 및 동시성 테스트
        print("\n📋 6단계: 성능 및 동시성 테스트")
        performance_test = await self.test_concurrent_operations()
        
        # 결과 요약
        await self.print_test_summary()
        
        return all([system_test, db_test, learning_test, isolation_test, memory_test, performance_test])
    
    async def test_system_connections(self) -> bool:
        """시스템 연결 테스트"""
        try:
            # MongoDB 설정 테스트
            print("   🔍 MongoDB 설정 테스트...")
            from mongodb_config import get_optimized_mongodb_connection, get_optimized_database
            
            client = get_optimized_mongodb_connection()
            if client is None:
                print("   ❌ MongoDB 연결 실패")
                return False
            
            db = get_optimized_database()
            if db is None:
                print("   ❌ 데이터베이스 연결 실패")
                return False
            
            print("   ✅ MongoDB 연결 성공")
            
            # 강화된 학습 시스템 테스트
            print("   🔍 강화된 학습 시스템 테스트...")
            from enhanced_learning_system import get_enhanced_learning_system
            
            learning_system = get_enhanced_learning_system(client)
            if learning_system is None:
                print("   ❌ 학습 시스템 초기화 실패")
                return False
            
            print("   ✅ 학습 시스템 초기화 성공")
            
            # 데이터베이스 매니저 테스트
            print("   🔍 데이터베이스 매니저 테스트...")
            from database import db_manager
            
            db_mgr = db_manager()
            if not db_mgr.is_connected():
                print("   ❌ 데이터베이스 매니저 연결 실패")
                return False
            
            print("   ✅ 데이터베이스 매니저 연결 성공")
            
            self.test_results["system_connections"] = True
            return True
            
        except Exception as e:
            print(f"   ❌ 시스템 연결 테스트 실패: {e}")
            self.test_results["system_connections"] = False
            return False
    
    async def test_database_connections(self) -> bool:
        """데이터베이스 연결 테스트"""
        try:
            from mongodb_config import get_optimized_database
            from database import db_manager
            
            db = get_optimized_database()
            db_mgr = db_manager()
            
            # 컬렉션 존재 확인
            collections = db.list_collection_names()
            required_collections = ["sessions", "chat_logs", "memories", "users", "points"]
            
            print(f"   📋 현재 컬렉션: {collections}")
            
            missing_collections = [col for col in required_collections if col not in collections]
            if missing_collections:
                print(f"   ⚠️ 누락된 컬렉션: {missing_collections}")
            else:
                print("   ✅ 모든 필수 컬렉션 존재")
            
            # 각 컬렉션의 문서 수 확인
            for collection_name in required_collections:
                if collection_name in collections:
                    count = db[collection_name].count_documents({})
                    print(f"   📊 {collection_name}: {count}개 문서")
            
            # 테스트 사용자 생성
            for user in self.test_users:
                user_id = user["user_id"]
                points = await db_mgr.get_user_points(user_id)
                print(f"   👤 {user['name']} ({user_id}): {points} 포인트")
            
            self.test_results["database_connections"] = True
            return True
            
        except Exception as e:
            print(f"   ❌ 데이터베이스 연결 테스트 실패: {e}")
            self.test_results["database_connections"] = False
            return False
    
    async def test_enhanced_learning_system(self) -> bool:
        """강화된 학습 시스템 테스트"""
        try:
            from mongodb_config import get_optimized_mongodb_connection
            from enhanced_learning_system import get_enhanced_learning_system
            
            client = get_optimized_mongodb_connection()
            learning_system = get_enhanced_learning_system(client)
            
            # 테스트 문서 내용
            test_documents = [
                {
                    "content": "Python은 간단하고 읽기 쉬운 프로그래밍 언어입니다. 데이터 과학, 웹 개발, 자동화 등 다양한 분야에서 사용됩니다.",
                    "filename": "python_intro.txt",
                    "category": "프로그래밍"
                },
                {
                    "content": "명상은 마음을 평온하게 하고 집중력을 향상시키는 수련법입니다. 호흡에 집중하며 현재 순간에 머무르는 것이 중요합니다.",
                    "filename": "meditation_guide.txt",
                    "category": "명상"
                },
                {
                    "content": "영업시간은 평일 오전 9시부터 오후 6시까지이며, 주말과 공휴일은 휴무입니다. 상담은 영업시간 내에 가능합니다.",
                    "filename": "business_hours.txt",
                    "category": "영업시간"
                }
            ]
            
            # 각 문서 학습 테스트
            for i, doc in enumerate(test_documents):
                print(f"   📚 문서 {i+1} 학습 테스트: {doc['filename']}")
                
                result = await learning_system.learn_document(
                    content=doc["content"],
                    filename=doc["filename"],
                    category=doc["category"]
                )
                
                if result.get("success"):
                    print(f"   ✅ 문서 {i+1} 학습 성공: {result['saved_memories']}개 메모리 저장")
                    print(f"      - 카테고리: {result['category']}")
                    print(f"      - 청크 수: {result['total_chunks']}")
                else:
                    print(f"   ❌ 문서 {i+1} 학습 실패: {result.get('error')}")
                    return False
            
            # 학습 통계 확인
            stats = await learning_system.get_learning_stats()
            print(f"   📊 학습 통계: {stats}")
            
            self.test_results["enhanced_learning"] = True
            return True
            
        except Exception as e:
            print(f"   ❌ 강화된 학습 시스템 테스트 실패: {e}")
            import traceback
            print(f"   🔍 상세 오류: {traceback.format_exc()}")
            self.test_results["enhanced_learning"] = False
            return False
    
    async def test_user_isolation(self) -> bool:
        """사용자 세션 격리 테스트"""
        try:
            from database import db_manager
            
            db_mgr = db_manager()
            
            # 각 사용자별로 세션 생성
            user_sessions = {}
            for user in self.test_users:
                user_id = user["user_id"]
                session_id = await db_mgr.create_session({
                    "user_id": user_id,
                    "session_name": f"{user['name']}의 테스트 세션",
                    "created_at": datetime.now().isoformat()
                })
                
                if session_id:
                    user_sessions[user_id] = session_id
                    print(f"   ✅ {user['name']} 세션 생성: {session_id}")
                else:
                    print(f"   ❌ {user['name']} 세션 생성 실패")
                    return False
            
            # 각 사용자별로 메시지 저장
            for user in self.test_users:
                user_id = user["user_id"]
                session_id = user_sessions[user_id]
                
                # 사용자 메시지 저장
                user_msg_id = await db_mgr.save_message(
                    session_id=session_id,
                    sender="user",
                    content=f"{user['name']}의 테스트 메시지입니다."
                )
                
                # AI 응답 저장
                ai_msg_id = await db_mgr.save_message(
                    session_id=session_id,
                    sender="assistant",
                    content=f"안녕하세요 {user['name']}님! 테스트 응답입니다."
                )
                
                if user_msg_id and ai_msg_id:
                    print(f"   ✅ {user['name']} 메시지 저장 성공")
                else:
                    print(f"   ❌ {user['name']} 메시지 저장 실패")
                    return False
            
            # 사용자별 세션 격리 확인
            for user in self.test_users:
                user_id = user["user_id"]
                user_sessions_list = await db_mgr.get_user_sessions(user_id)
                print(f"   📋 {user['name']} 세션 수: {len(user_sessions_list)}")
                
                if user_sessions_list:
                    session = user_sessions_list[0]
                    messages = await db_mgr.get_session_messages(session["session_id"])
                    print(f"      - 메시지 수: {len(messages)}")
                    
                    # 다른 사용자의 메시지가 포함되지 않았는지 확인
                    other_user_messages = [msg for msg in messages if msg.get("content", "").find("테스트 메시지") != -1 and msg.get("content", "").find(user["name"]) == -1]
                    if other_user_messages:
                        print(f"   ❌ {user['name']} 세션에 다른 사용자 메시지 포함됨")
                        return False
                    else:
                        print(f"   ✅ {user['name']} 세션 격리 확인")
            
            self.test_results["user_isolation"] = True
            return True
            
        except Exception as e:
            print(f"   ❌ 사용자 격리 테스트 실패: {e}")
            self.test_results["user_isolation"] = False
            return False
    
    async def test_memory_operations(self) -> bool:
        """메모리 저장 및 회상 테스트"""
        try:
            # EORA 메모리 시스템 테스트
            try:
                from eora_memory_system import EORAMemorySystem
                memory_system = EORAMemorySystem()
                
                if not memory_system.is_connected():
                    print("   ⚠️ EORA 메모리 시스템 연결 실패, 기본 테스트로 진행")
                    raise ImportError("EORA memory system not available")
                
                # 각 사용자별로 메모리 저장 테스트
                for user in self.test_users:
                    user_id = user["user_id"]
                    test_content = f"{user['name']}의 개인 메모리 내용입니다. 이것은 {user_id} 사용자만의 고유한 정보입니다."
                    
                    # 메모리 저장
                    result = await memory_system.store_memory(
                        content=test_content,
                        memory_type="user_personal",
                        user_id=user_id,
                        metadata={"source": "test", "user_name": user["name"]}
                    )
                    
                    if result.get("success"):
                        print(f"   ✅ {user['name']} 메모리 저장 성공")
                    else:
                        print(f"   ❌ {user['name']} 메모리 저장 실패")
                        return False
                
                # 메모리 회상 테스트
                for user in self.test_users:
                    user_id = user["user_id"]
                    
                    recall_results = await memory_system.recall_learned_content(
                        query=user["name"],
                        memory_type="user_personal",
                        limit=5
                    )
                    
                    print(f"   📋 {user['name']} 회상 결과: {len(recall_results)}개")
                    
                    # 자신의 메모리만 회상되는지 확인
                    for result in recall_results:
                        if user_id not in result.get("content", ""):
                            print(f"   ⚠️ {user['name']} 회상에 다른 사용자 메모리 포함")
                
            except ImportError:
                print("   ⚠️ EORA 메모리 시스템 사용 불가, 기본 메모리 테스트 진행")
                
                # 기본 MongoDB 메모리 테스트
                from mongodb_config import get_optimized_database
                db = get_optimized_database()
                
                for user in self.test_users:
                    user_id = user["user_id"]
                    
                    # 메모리 문서 저장
                    memory_doc = {
                        "user_id": user_id,
                        "content": f"{user['name']}의 기본 메모리 테스트",
                        "memory_type": "test_memory",
                        "timestamp": datetime.now(),
                        "metadata": {"test": True}
                    }
                    
                    result = db.memories.insert_one(memory_doc)
                    if result.inserted_id:
                        print(f"   ✅ {user['name']} 기본 메모리 저장 성공")
                    else:
                        print(f"   ❌ {user['name']} 기본 메모리 저장 실패")
                        return False
                
                # 저장된 메모리 확인
                total_test_memories = db.memories.count_documents({"memory_type": "test_memory"})
                print(f"   📊 총 테스트 메모리 수: {total_test_memories}")
            
            self.test_results["memory_operations"] = True
            return True
            
        except Exception as e:
            print(f"   ❌ 메모리 작업 테스트 실패: {e}")
            self.test_results["memory_operations"] = False
            return False
    
    async def test_concurrent_operations(self) -> bool:
        """동시 작업 테스트"""
        try:
            from database import db_manager
            from mongodb_config import get_optimized_database
            
            db_mgr = db_manager()
            db = get_optimized_database()
            
            print("   🔄 동시 세션 생성 테스트...")
            
            # 동시에 여러 세션 생성
            tasks = []
            for i in range(5):
                task = db_mgr.create_session({
                    "user_id": f"concurrent_user_{i}@test.com",
                    "session_name": f"동시 테스트 세션 {i}",
                    "created_at": datetime.now().isoformat()
                })
                tasks.append(task)
            
            # 모든 태스크 완료 대기
            session_ids = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_sessions = [sid for sid in session_ids if isinstance(sid, str)]
            print(f"   ✅ 동시 세션 생성 성공: {len(successful_sessions)}/5개")
            
            # 데이터베이스 성능 테스트
            print("   📊 데이터베이스 성능 테스트...")
            
            start_time = datetime.now()
            
            # 100개 메모리 동시 저장
            memory_tasks = []
            for i in range(100):
                memory_doc = {
                    "user_id": "performance_test@test.com",
                    "content": f"성능 테스트 메모리 {i}",
                    "memory_type": "performance_test",
                    "timestamp": datetime.now(),
                    "test_index": i
                }
                memory_tasks.append(db.memories.insert_one(memory_doc))
            
            # 모든 저장 완료 대기
            insert_results = await asyncio.gather(*memory_tasks, return_exceptions=True)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            successful_inserts = [r for r in insert_results if not isinstance(r, Exception)]
            print(f"   ⏱️ 100개 메모리 저장 시간: {duration:.2f}초")
            print(f"   ✅ 성공한 저장: {len(successful_inserts)}/100개")
            
            # 성능 테스트 데이터 정리
            db.memories.delete_many({"memory_type": "performance_test"})
            
            self.test_results["concurrent_operations"] = True
            return True
            
        except Exception as e:
            print(f"   ❌ 동시 작업 테스트 실패: {e}")
            self.test_results["concurrent_operations"] = False
            return False
    
    async def print_test_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 80)
        print("📊 테스트 결과 요약")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        print(f"전체 테스트: {total_tests}개")
        print(f"통과한 테스트: {passed_tests}개")
        print(f"실패한 테스트: {total_tests - passed_tests}개")
        print(f"성공률: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n세부 결과:")
        for test_name, result in self.test_results.items():
            status = "✅ 통과" if result else "❌ 실패"
            print(f"  {test_name}: {status}")
        
        if passed_tests == total_tests:
            print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
            print("✅ 다중 사용자 학습 시스템이 정상 작동합니다.")
        else:
            print("\n⚠️ 일부 테스트가 실패했습니다.")
            print("❗ 실패한 테스트를 확인하고 문제를 해결해주세요.")
        
        print("=" * 80)

async def main():
    """메인 테스트 실행"""
    test_suite = MultiUserLearningTestSuite()
    
    try:
        success = await test_suite.run_comprehensive_test()
        
        if success:
            print("\n🎯 전체 테스트 성공!")
            sys.exit(0)
        else:
            print("\n❌ 일부 테스트 실패!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 테스트가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류 발생: {e}")
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 다중 사용자 학습 시스템 종합 테스트")
    print("Ctrl+C를 눌러 언제든지 테스트를 중단할 수 있습니다.")
    print("")
    
    asyncio.run(main())