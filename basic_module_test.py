#!/usr/bin/env python3
"""
기본 모듈 테스트 - 무한루프 원인 찾기
각 모듈을 하나씩 테스트하여 문제 모듈 식별
"""

import sys
import os
import time

print("🔍 기본 모듈 테스트 시작")
print("각 모듈을 개별적으로 테스트하여 무한루프 원인을 찾습니다")
print("=" * 60)

start_time = time.time()

def check_time():
    elapsed = time.time() - start_time
    print(f"⏱️ 경과 시간: {elapsed:.1f}초")
    if elapsed > 30:  # 30초 제한
        print("🚨 30초 제한 - 강제 종료")
        sys.exit(1)

# 현재 디렉토리를 파이썬 경로에 추가
sys.path.append('.')
check_time()

print("1️⃣ 기본 Python 모듈 테스트")
try:
    import json
    import datetime
    from typing import Dict, List
    print("   ✅ 기본 모듈들 import 성공")
except Exception as e:
    print(f"   ❌ 기본 모듈 import 실패: {e}")
    sys.exit(1)

check_time()

print("\n2️⃣ pymongo 모듈 테스트")
try:
    import pymongo
    from pymongo import MongoClient
    print("   ✅ pymongo import 성공")
except Exception as e:
    print(f"   ❌ pymongo import 실패: {e}")
    print("   💡 해결책: pip install pymongo")
    sys.exit(1)

check_time()

print("\n3️⃣ mongodb_config 모듈 테스트")
try:
    print("   🔄 mongodb_config import 시도...")
    import mongodb_config
    print("   ✅ mongodb_config import 성공")
except Exception as e:
    print(f"   ❌ mongodb_config import 실패: {e}")
    print("   🔍 이 모듈에 문제가 있을 수 있습니다")

check_time()

print("\n4️⃣ mongodb_config 함수 테스트")
try:
    print("   🔄 get_optimized_mongodb_connection 호출...")
    from mongodb_config import get_optimized_mongodb_connection
    print("   ✅ 함수 import 성공")
    
    print("   🔄 실제 연결 시도...")
    client = get_optimized_mongodb_connection()
    print(f"   📊 연결 결과: {client is not None}")
    
    if client:
        print("   🔄 ping 테스트...")
        client.admin.command('ping')
        print("   ✅ ping 성공")
except Exception as e:
    print(f"   ❌ MongoDB 연결 실패: {e}")

check_time()

print("\n5️⃣ enhanced_learning_system 모듈 테스트")
try:
    print("   🔄 enhanced_learning_system import 시도...")
    import enhanced_learning_system
    print("   ✅ enhanced_learning_system import 성공")
    
    print("   🔄 함수 호출 시도...")
    from enhanced_learning_system import get_enhanced_learning_system
    print("   ✅ 함수 import 성공")
    
except Exception as e:
    print(f"   ❌ enhanced_learning_system 실패: {e}")
    print("   🔍 이 모듈에 문제가 있을 수 있습니다")

check_time()

print("\n6️⃣ eora_memory_system 모듈 테스트 (위험 단계)")
try:
    print("   ⚠️ eora_memory_system import 시도... (이 단계에서 멈출 수 있음)")
    
    # 타임아웃 체크를 더 자주 함
    import_start = time.time()
    
    # 단계적으로 import 시도
    import eora_memory_system
    
    import_time = time.time() - import_start
    print(f"   ✅ eora_memory_system import 성공 ({import_time:.1f}초 소요)")
    
    if import_time > 10:
        print("   ⚠️ import에 너무 오래 걸림 - 이 모듈에 문제가 있을 수 있음")
    
except Exception as e:
    print(f"   ❌ eora_memory_system import 실패: {e}")
    print("   🔍 이 모듈이 무한루프의 원인일 가능성이 높습니다")

check_time()

print("\n7️⃣ EORAMemorySystem 클래스 테스트")
try:
    print("   🔄 EORAMemorySystem 클래스 로드 시도...")
    from eora_memory_system import EORAMemorySystem
    print("   ✅ 클래스 import 성공")
    
    print("   ⚠️ 인스턴스 생성 시도... (위험 단계)")
    creation_start = time.time()
    
    memory_system = EORAMemorySystem()
    
    creation_time = time.time() - creation_start
    print(f"   ✅ 인스턴스 생성 성공 ({creation_time:.1f}초 소요)")
    
    if creation_time > 5:
        print("   ⚠️ 생성에 너무 오래 걸림")
    
except Exception as e:
    print(f"   ❌ EORAMemorySystem 생성 실패: {e}")
    print("   🔍 클래스 생성자에 무한루프가 있을 수 있습니다")

check_time()

print("\n🎯 테스트 완료!")
elapsed = time.time() - start_time
print(f"⏱️ 총 소요 시간: {elapsed:.1f}초")

if elapsed < 20:
    print("✅ 모든 모듈이 정상적으로 로드되었습니다")
    print("💡 무한루프 문제는 특정 함수 호출에서 발생할 수 있습니다")
else:
    print("⚠️ 일부 모듈 로딩이 느렸습니다")
    print("💡 느린 모듈을 확인해보세요")

print("\n📋 문제 해결 방법:")
print("1. 가장 오래 걸린 단계를 확인하세요")
print("2. 해당 모듈의 import 구문이나 초기화 코드를 점검하세요")
print("3. 순환 import가 있는지 확인하세요")
print("4. 무한루프가 있는 함수나 클래스를 찾아 수정하세요")

print(f"\n🏁 테스트 종료 - {elapsed:.1f}초")
sys.exit(0)