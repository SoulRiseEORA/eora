#!/usr/bin/env python3
"""
응급 테스트 - 무한루프 완전 회피
sys.path 조작 없이 절대 경로로만 테스트
"""

import os
import time
import sys

print("🚨 응급 테스트 시작")
print(f"현재 디렉토리: {os.getcwd()}")
print(f"Python 경로: {sys.executable}")

start_time = time.time()

def force_exit_if_timeout():
    """5초 후 강제 종료"""
    elapsed = time.time() - start_time
    if elapsed > 5:
        print(f"🚨 5초 타임아웃 - 강제 종료 (경과: {elapsed:.1f}초)")
        os._exit(1)
    return elapsed

# 1. 기본 테스트
elapsed = force_exit_if_timeout()
print(f"1. 기본 동작 확인 - {elapsed:.1f}초")

# 2. 파일 존재 확인 (import 없이)
elapsed = force_exit_if_timeout()
print("2. 파일 존재 확인")

critical_files = [
    "mongodb_config.py",
    "enhanced_learning_system.py", 
    "eora_memory_system.py",
    "database.py"
]

for filename in critical_files:
    exists = os.path.exists(filename)
    size = os.path.getsize(filename) if exists else 0
    print(f"   {filename}: {'존재' if exists else '없음'} ({size} bytes)")

# 3. 간단한 MongoDB 테스트 (pymongo만)
elapsed = force_exit_if_timeout()
print("3. pymongo 직접 테스트")

try:
    import pymongo
    print("   ✅ pymongo import 성공")
    
    # 로컬 MongoDB만 테스트
    client = pymongo.MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
    client.admin.command('ping')
    print("   ✅ localhost MongoDB 연결 성공")
    
    db = client["eora_ai"]
    collections = db.list_collection_names()
    print(f"   📋 컬렉션 수: {len(collections)}")
    
    if 'memories' in collections:
        count = db.memories.count_documents({})
        print(f"   💾 메모리 문서 수: {count}")
    
    client.close()
    
except Exception as e:
    print(f"   ❌ MongoDB 테스트 실패: {e}")

# 4. 최종 체크
elapsed = force_exit_if_timeout()
print(f"4. 최종 체크 - 총 {elapsed:.1f}초 소요")

if elapsed < 3:
    print("✅ 기본 환경은 정상입니다")
    print("💡 무한루프는 특정 모듈의 import나 초기화에서 발생합니다")
    
    print("\n🔍 무한루프 원인 추정:")
    print("1. eora_memory_system.py의 EORAMemorySystem 생성자")
    print("2. mongodb_config.py의 자동 연결 시도")
    print("3. database.py의 init_mongodb_connection() 자동 실행")
    print("4. 순환 import 문제")
    
    print("\n💡 해결 방법:")
    print("1. 모든 자동 초기화 코드를 지연 로딩으로 변경")
    print("2. import 시점에 실행되는 코드 제거")
    print("3. 명시적 초기화 함수 사용")
    
else:
    print("⚠️ 기본 환경에도 문제가 있을 수 있습니다")

print(f"\n🏁 응급 테스트 완료 - {time.time() - start_time:.1f}초")

# 안전한 종료
try:
    sys.exit(0)
except:
    os._exit(0)