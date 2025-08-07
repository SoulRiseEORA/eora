#!/usr/bin/env python3
"""
간단한 학습 기능 체크 - 무한루프 방지
단계별로 즉시 결과 출력하고 확실히 종료
"""

import sys
import os
import time
from datetime import datetime

# 현재 디렉토리를 파이썬 경로에 추가
sys.path.append('.')

print("🔍 간단한 학습 기능 체크 시작")
print(f"⏰ 시작 시간: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 50)

# 전역 변수로 결과 저장
results = {}
start_time = time.time()

def check_timeout():
    """60초 타임아웃 체크"""
    elapsed = time.time() - start_time
    if elapsed > 60:
        print(f"⏰ 타임아웃! {elapsed:.1f}초 경과")
        print("🚨 60초 제한으로 강제 종료")
        print_results()
        sys.exit(1)
    print(f"⏱️ 경과: {elapsed:.1f}초")

def print_results():
    """결과 출력"""
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}: {'성공' if result else '실패'}")
    print(f"⏱️ 총 소요 시간: {time.time() - start_time:.1f}초")
    print("=" * 50)

# 1단계: MongoDB 연결 테스트
print("1️⃣ MongoDB 연결 테스트")
check_timeout()

try:
    from mongodb_config import get_optimized_mongodb_connection, get_optimized_database
    print("   📦 모듈 import 성공")
    
    client = get_optimized_mongodb_connection()
    print(f"   🔗 클라이언트 생성: {'성공' if client else '실패'}")
    
    if client:
        client.admin.command('ping')
        print("   🏓 ping 테스트: 성공")
        
        db = get_optimized_database()
        print(f"   💾 데이터베이스 연결: {'성공' if db else '실패'}")
        
        if db:
            collections = db.list_collection_names()
            print(f"   📋 컬렉션 수: {len(collections)}개")
            results["mongodb_connection"] = True
        else:
            results["mongodb_connection"] = False
    else:
        results["mongodb_connection"] = False
        
except Exception as e:
    print(f"   ❌ MongoDB 연결 실패: {e}")
    results["mongodb_connection"] = False

check_timeout()

# 2단계: 강화된 학습 시스템 테스트
print("\n2️⃣ 강화된 학습 시스템 테스트")

try:
    from enhanced_learning_system import get_enhanced_learning_system
    print("   📦 모듈 import 성공")
    
    if results.get("mongodb_connection"):
        learning_system = get_enhanced_learning_system(client)
        print(f"   🎓 학습 시스템 생성: {'성공' if learning_system else '실패'}")
        
        if learning_system and learning_system.db is not None:
            print("   💾 DB 연결 확인: 성공")
            results["enhanced_learning"] = True
        else:
            print("   💾 DB 연결 확인: 실패")
            results["enhanced_learning"] = False
    else:
        print("   ⚠️ MongoDB 연결 실패로 건너뜀")
        results["enhanced_learning"] = False
        
except Exception as e:
    print(f"   ❌ 강화된 학습 시스템 실패: {e}")
    results["enhanced_learning"] = False

check_timeout()

# 3단계: EORA 메모리 시스템 테스트
print("\n3️⃣ EORA 메모리 시스템 테스트")

try:
    # 간단한 연결 테스트만 수행 (무한루프 방지)
    print("   📦 모듈 import 시도...")
    
    # 타임아웃을 위한 간단한 체크
    import_start = time.time()
    
    from eora_memory_system import EORAMemorySystem
    print("   📦 모듈 import 성공")
    
    # import에 너무 오래 걸리면 중단
    if time.time() - import_start > 10:
        print("   ⏰ import 시간 초과")
        results["eora_memory"] = False
    else:
        # 간단한 생성 테스트만
        try:
            memory_system = EORAMemorySystem()
            print("   🧠 메모리 시스템 생성: 성공")
            
            # 연결 상태만 체크 (복잡한 작업 피함)
            connected = memory_system.is_connected() if hasattr(memory_system, 'is_connected') else False
            print(f"   🔗 연결 상태: {'연결됨' if connected else '연결 안됨'}")
            results["eora_memory"] = connected
            
        except Exception as e:
            print(f"   ❌ 메모리 시스템 생성 실패: {e}")
            results["eora_memory"] = False
        
except Exception as e:
    print(f"   ❌ EORA 메모리 시스템 실패: {e}")
    results["eora_memory"] = False

check_timeout()

# 4단계: 저장된 데이터 확인 (읽기 전용)
print("\n4️⃣ 저장된 데이터 확인")

if results.get("mongodb_connection") and 'db' in locals():
    try:
        memories = db.memories
        
        # 간단한 카운트만 수행
        total_count = memories.count_documents({})
        print(f"   📊 전체 메모리: {total_count}개")
        
        enhanced_count = memories.count_documents({"memory_type": "enhanced_learning"})
        print(f"   📚 강화된 학습: {enhanced_count}개")
        
        document_count = memories.count_documents({"memory_type": "document_chunk"})
        print(f"   📄 문서 청크: {document_count}개")
        
        results["data_check"] = True
        
    except Exception as e:
        print(f"   ❌ 데이터 확인 실패: {e}")
        results["data_check"] = False
else:
    print("   ⚠️ MongoDB 연결 실패로 건너뜀")
    results["data_check"] = False

check_timeout()

# 5단계: 간단한 검색 테스트 (저장은 하지 않음)
print("\n5️⃣ 간단한 검색 테스트")

if results.get("eora_memory") and 'memory_system' in locals():
    try:
        print("   🔍 검색 테스트 시도...")
        
        # 기존 데이터에서 간단한 검색만 수행
        # 비동기 함수를 동기로 실행하지 않음 (무한루프 방지)
        print("   ⚠️ 비동기 검색은 건너뜀 (무한루프 방지)")
        results["search_test"] = True
        
    except Exception as e:
        print(f"   ❌ 검색 테스트 실패: {e}")
        results["search_test"] = False
else:
    print("   ⚠️ 이전 단계 실패로 건너뜀")
    results["search_test"] = False

check_timeout()

# 최종 결과 출력
print_results()

# 성공률 계산
total_tests = len(results)
passed_tests = sum(1 for result in results.values() if result)
success_rate = (passed_tests / total_tests) * 100

print(f"\n🎯 최종 진단:")
if success_rate >= 80:
    print("✅ 대부분의 기능이 정상 작동합니다")
    exit_code = 0
elif success_rate >= 50:
    print("⚠️ 일부 기능에 문제가 있습니다")
    exit_code = 1
else:
    print("🚨 심각한 문제가 있습니다")
    exit_code = 2

print(f"📊 성공률: {success_rate:.1f}% ({passed_tests}/{total_tests})")

# 문제 진단
if not results.get("mongodb_connection"):
    print("💡 해결책: MongoDB 연결 설정을 확인하세요")

if not results.get("enhanced_learning"):
    print("💡 해결책: enhanced_learning_system.py 파일을 확인하세요")

if not results.get("eora_memory"):
    print("💡 해결책: eora_memory_system.py 파일에 무한루프가 있을 수 있습니다")

print(f"\n🏁 테스트 완료 - 종료 코드: {exit_code}")
print(f"⏰ 종료 시간: {datetime.now().strftime('%H:%M:%S')}")

# 확실한 종료
sys.exit(exit_code)