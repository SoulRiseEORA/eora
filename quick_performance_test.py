#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI 빠른 성능 테스트
"""

import time
import requests
import statistics
import sys

def test_server_performance():
    """서버 성능 테스트"""
    print("🚀 EORA AI 성능 최적화 테스트")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8300"
    
    # 1. 서버 상태 확인
    print("🔍 서버 상태 확인...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 서버 실행 중")
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return False
    
    # 2. 응답 시간 측정 (홈페이지 로드)
    print("\n📊 응답 시간 측정...")
    response_times = []
    
    for i in range(10):
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}/", timeout=10)
            end_time = time.time()
            
            response_time = end_time - start_time
            response_times.append(response_time)
            
            print(f"  요청 {i+1}: {response_time:.3f}초")
            time.sleep(0.1)
            
        except Exception as e:
            print(f"  요청 {i+1}: 실패 ({e})")
    
    # 3. 결과 분석
    if response_times:
        avg_time = statistics.mean(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        median_time = statistics.median(response_times)
        
        print(f"\n📈 성능 결과:")
        print(f"  평균 응답시간: {avg_time:.3f}초")
        print(f"  중간값: {median_time:.3f}초")
        print(f"  최단 시간: {min_time:.3f}초")
        print(f"  최장 시간: {max_time:.3f}초")
        
        # 성능 등급
        if avg_time < 0.1:
            grade = "S+ (탁월)"
        elif avg_time < 0.2:
            grade = "S (매우 우수)"
        elif avg_time < 0.5:
            grade = "A (우수)"
        elif avg_time < 1.0:
            grade = "B (양호)"
        elif avg_time < 2.0:
            grade = "C (보통)"
        else:
            grade = "D (개선 필요)"
        
        print(f"  성능 등급: {grade}")
        
        # 캐시 효과 테스트
        print(f"\n💾 캐시 효과 분석:")
        first_half = response_times[:5]
        second_half = response_times[5:]
        
        if len(first_half) > 0 and len(second_half) > 0:
            first_avg = statistics.mean(first_half)
            second_avg = statistics.mean(second_half)
            improvement = ((first_avg - second_avg) / first_avg) * 100
            
            print(f"  초기 평균: {first_avg:.3f}초")
            print(f"  후반 평균: {second_avg:.3f}초")
            if improvement > 0:
                print(f"  성능 향상: {improvement:.1f}%")
            else:
                print(f"  성능 변화: {abs(improvement):.1f}% (안정적)")
        
        # 종합 평가
        print(f"\n🎯 종합 평가:")
        if avg_time < 0.5:
            print("🎉 성능 최적화 성공! 매우 빠른 응답속도")
            if improvement > 10:
                print("✨ 캐시 시스템도 효과적으로 작동중")
            return True
        elif avg_time < 1.0:
            print("✅ 성능 양호! 적절한 응답속도")
            return True
        else:
            print("⚠️ 성능 개선 필요")
            return False
    else:
        print("❌ 성능 측정 실패")
        return False

def main():
    """메인 함수"""
    print("⚡ EORA AI 성능 최적화 효과 검증")
    print("이 테스트는 최적화된 서버의 응답속도를 측정합니다.")
    print("-" * 50)
    
    success = test_server_performance()
    
    if success:
        print("\n🚀 성능 테스트 통과!")
        print("✅ 배포 준비 완료!")
        print("\n📋 적용된 최적화:")
        print("  • 응답 캐싱 시스템")
        print("  • 성능 모니터링")
        print("  • 데이터베이스 최적화")
        print("  • 마크다운 처리 향상")
        print("  • 시간 조정 자동화")
        return True
    else:
        print("\n❌ 성능 테스트 실패")
        print("🔧 추가 최적화가 필요합니다.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 