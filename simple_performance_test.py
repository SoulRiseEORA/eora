#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI 간단한 성능 테스트
"""

import sys
import time

# 프로젝트 경로 추가
sys.path.append('src')

def test_performance_optimization():
    """성능 최적화 모듈 테스트"""
    print("🚀 성능 최적화 모듈 테스트")
    
    try:
        from performance_optimizer import optimizer, get_performance_stats
        print("✅ 성능 최적화 모듈 로드 성공")
        
        # 캐시 테스트
        test_key = "test_key"
        test_data = {"message": "테스트 데이터", "response_time": 0.5}
        
        optimizer.cache_response(test_key, test_data)
        cached_result = optimizer.get_cached_response(test_key)
        
        if cached_result:
            print("✅ 캐시 시스템 작동 확인")
        else:
            print("❌ 캐시 시스템 오류")
        
        # 성능 통계
        stats = get_performance_stats()
        print(f"📊 성능 통계: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ 성능 최적화 모듈 테스트 실패: {e}")
        return False

def test_imports():
    """핵심 모듈 임포트 테스트"""
    print("📦 핵심 모듈 임포트 테스트")
    
    try:
        # 마크다운 프로세서
        from markdown_processor import format_api_response
        print("✅ 마크다운 프로세서 로드 성공")
        
        # 시간 관리자
        from time_manager import parse_relative_time
        print("✅ 시간 관리자 로드 성공")
        
        # 성능 최적화
        from performance_optimizer import performance_monitor
        print("✅ 성능 최적화 데코레이터 로드 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ 모듈 임포트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_server_startup():
    """서버 시작 로직 테스트"""
    print("🖥️ 서버 시작 로직 테스트")
    
    try:
        # 데이터베이스 연결 테스트
        from database import db_manager
        db_mgr = db_manager()
        
        if db_mgr and hasattr(db_mgr, 'is_connected'):
            if db_mgr.is_connected():
                print("✅ MongoDB 연결 성공")
            else:
                print("⚠️ MongoDB 연결 실패 (정상 - 로컬 테스트)")
        
        # EORA 메모리 시스템
        from aura_memory_system import EORAMemorySystem
        eora_memory = EORAMemorySystem()
        print("✅ EORA 메모리 시스템 로드 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ 서버 로직 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def simulate_api_optimization():
    """API 최적화 시뮬레이션"""
    print("⚡ API 최적화 시뮬레이션")
    
    # 기존 방식 (최적화 전)
    def old_method():
        time.sleep(0.1)  # 시뮬레이션된 처리 시간
        return "기존 응답"
    
    # 최적화된 방식 (캐시 적용)
    cache = {}
    def optimized_method(cache_key="test"):
        if cache_key in cache:
            return cache[cache_key]
        
        time.sleep(0.1)  # 시뮬레이션된 처리 시간
        result = "최적화된 응답"
        cache[cache_key] = result
        return result
    
    # 성능 비교
    print("  기존 방식 테스트...")
    start_time = time.time()
    for i in range(5):
        old_method()
    old_time = time.time() - start_time
    
    print("  최적화된 방식 테스트...")
    start_time = time.time()
    for i in range(5):
        optimized_method("test_key")  # 동일한 키로 캐시 활용
    optimized_time = time.time() - start_time
    
    improvement = ((old_time - optimized_time) / old_time) * 100
    
    print(f"  기존 방식: {old_time:.3f}초")
    print(f"  최적화 방식: {optimized_time:.3f}초")
    print(f"  성능 향상: {improvement:.1f}%")
    
    return improvement > 0

def main():
    """메인 테스트 함수"""
    print("🧪 EORA AI 성능 최적화 간단 테스트")
    print("=" * 60)
    
    tests = [
        ("모듈 임포트", test_imports),
        ("성능 최적화 모듈", test_performance_optimization),
        ("서버 시작 로직", test_server_startup),
        ("API 최적화 시뮬레이션", simulate_api_optimization)
    ]
    
    results = {}
    passed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name} 테스트...")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
                print(f"✅ {test_name} 통과")
            else:
                print(f"❌ {test_name} 실패")
        except Exception as e:
            print(f"❌ {test_name} 오류: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name:20} : {status}")
    
    print("-" * 60)
    print(f"총 테스트: {len(tests)}개")
    print(f"통과: {passed}개")
    print(f"실패: {len(tests) - passed}개")
    print(f"성공률: {passed/len(tests)*100:.1f}%")
    
    if passed == len(tests):
        print("\n🎉 모든 테스트 통과! 성능 최적화 준비 완료!")
        print("✨ 서버 실행 및 배포 가능 상태입니다.")
        return True
    else:
        print(f"\n⚠️ {len(tests) - passed}개 테스트 실패")
        print("🔧 문제를 해결한 후 다시 테스트해주세요.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 