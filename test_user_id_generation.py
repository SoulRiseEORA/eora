#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사용자 ID 생성 알고리즘 테스트
"""

import random
import string
import time

def test_user_id_generation():
    """사용자 ID 생성 테스트"""
    print("=" * 60)
    print("🆔 사용자 ID 생성 알고리즘 테스트")
    print("=" * 60)
    
    # 현재 시스템과 동일한 방식
    chars = string.ascii_uppercase + string.digits
    print(f"📝 사용 가능한 문자: {chars}")
    print(f"📊 문자 수: {len(chars)}개")
    print(f"📈 12자리 조합 가능 수: {len(chars)**12:,}개")
    
    # 100개의 ID 생성 테스트
    generated_ids = set()
    duplicates = 0
    
    print(f"\n🧪 100개 ID 생성 테스트:")
    
    for i in range(100):
        user_id = ''.join(random.choice(chars) for _ in range(12))
        
        if user_id in generated_ids:
            duplicates += 1
            print(f"   ⚠️ 중복 발견: {user_id}")
        else:
            generated_ids.add(user_id)
        
        if i < 10:  # 처음 10개만 출력
            print(f"   {i+1:2d}. {user_id}")
    
    print(f"\n📊 테스트 결과:")
    print(f"   ✅ 생성된 ID 수: {len(generated_ids)}개")
    print(f"   ❌ 중복 발생: {duplicates}개")
    print(f"   📈 중복 확률: {duplicates/100:.2%}")
    
    # 길이 검증
    print(f"\n📏 길이 검증:")
    all_correct_length = all(len(uid) == 12 for uid in generated_ids)
    print(f"   ✅ 모든 ID가 12자리: {all_correct_length}")
    
    # 문자 검증
    print(f"\n🔤 문자 검증:")
    all_valid_chars = all(
        all(c in chars for c in uid) 
        for uid in generated_ids
    )
    print(f"   ✅ 모든 ID가 유효한 문자만 사용: {all_valid_chars}")
    
    # 성능 테스트
    print(f"\n⚡ 성능 테스트:")
    start_time = time.time()
    
    for _ in range(10000):
        user_id = ''.join(random.choice(chars) for _ in range(12))
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"   📈 10,000개 생성 시간: {elapsed:.4f}초")
    print(f"   📊 초당 생성 속도: {10000/elapsed:.0f}개/초")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_user_id_generation()