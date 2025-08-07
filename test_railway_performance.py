#!/usr/bin/env python3
"""
Railway 성능 테스트 도구
최적화 전후 성능을 비교하여 개선 효과를 측정합니다.
"""

import requests
import time
import asyncio
import json
from datetime import datetime

class RailwayPerformanceTester:
    """Railway 배포 성능 테스터"""
    
    def __init__(self, base_url="https://web-production-40c0.up.railway.app"):
        self.base_url = base_url
        self.results = []
    
    def test_endpoint(self, endpoint, method="GET", data=None, timeout=30):
        """개별 엔드포인트 성능 테스트"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(url, timeout=timeout)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=timeout)
            
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)  # ms
            
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "success": response.status_code == 200,
                "timestamp": datetime.now().isoformat()
            }
            
            if response.status_code == 200:
                print(f"✅ {endpoint}: {response_time}ms")
            else:
                print(f"❌ {endpoint}: {response.status_code} ({response_time}ms)")
            
            return result
            
        except requests.exceptions.Timeout:
            print(f"⏰ {endpoint}: 타임아웃 ({timeout}초)")
            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": 408,
                "response_time_ms": timeout * 1000,
                "success": False,
                "error": "timeout",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ {endpoint}: 오류 - {str(e)}")
            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": 500,
                "response_time_ms": 0,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_comprehensive_test(self):
        """포괄적인 성능 테스트 실행"""
        print("🚀 Railway 성능 테스트 시작")
        print("=" * 50)
        
        # 테스트할 엔드포인트들
        test_cases = [
            # 기본 페이지들
            {"endpoint": "/", "method": "GET", "description": "홈페이지"},
            {"endpoint": "/api/status", "method": "GET", "description": "API 상태"},
            {"endpoint": "/api/health", "method": "GET", "description": "헬스체크"},
            {"endpoint": "/chat", "method": "GET", "description": "채팅 페이지"},
            
            # 세션 관리
            {"endpoint": "/api/sessions", "method": "GET", "description": "세션 목록"},
            {"endpoint": "/api/sessions", "method": "POST", "data": {"name": "성능 테스트 세션"}, "description": "세션 생성"},
            
            # 사용자 정보
            {"endpoint": "/api/user/points", "method": "GET", "description": "포인트 조회"},
            {"endpoint": "/api/user/stats", "method": "GET", "description": "사용자 통계"},
            
            # 채팅 테스트
            {"endpoint": "/api/chat", "method": "POST", "data": {
                "message": "성능 테스트 메시지입니다.",
                "session_id": "performance_test",
                "user_id": "test_user"
            }, "description": "채팅 API"},
        ]
        
        start_total = time.time()
        
        for test_case in test_cases:
            print(f"\n🔍 테스트: {test_case['description']}")
            result = self.test_endpoint(
                test_case["endpoint"],
                test_case.get("method", "GET"),
                test_case.get("data"),
                timeout=30
            )
            self.results.append(result)
            
            # 요청 간 간격
            time.sleep(1)
        
        end_total = time.time()
        total_time = round((end_total - start_total) * 1000, 2)
        
        print("\n" + "=" * 50)
        print("📊 성능 테스트 결과 요약")
        print("=" * 50)
        
        successful_tests = [r for r in self.results if r["success"]]
        failed_tests = [r for r in self.results if not r["success"]]
        
        print(f"✅ 성공: {len(successful_tests)}/{len(self.results)}")
        print(f"❌ 실패: {len(failed_tests)}/{len(self.results)}")
        print(f"⏱️ 총 소요시간: {total_time}ms")
        
        if successful_tests:
            avg_response = sum(r["response_time_ms"] for r in successful_tests) / len(successful_tests)
            min_response = min(r["response_time_ms"] for r in successful_tests)
            max_response = max(r["response_time_ms"] for r in successful_tests)
            
            print(f"📈 평균 응답시간: {avg_response:.2f}ms")
            print(f"🚀 최고 속도: {min_response}ms")
            print(f"🐌 최저 속도: {max_response}ms")
        
        # 실패한 테스트 상세 정보
        if failed_tests:
            print("\n❌ 실패한 테스트:")
            for test in failed_tests:
                error = test.get("error", "Unknown error")
                print(f"  - {test['endpoint']}: {error}")
        
        # 성능 평가
        print("\n🎯 성능 평가:")
        if avg_response < 1000:
            print("🏆 우수: 평균 응답시간 1초 미만")
        elif avg_response < 3000:
            print("✅ 양호: 평균 응답시간 3초 미만")
        elif avg_response < 5000:
            print("⚠️ 보통: 평균 응답시간 5초 미만")
        else:
            print("🔧 개선 필요: 평균 응답시간 5초 이상")
        
        return {
            "total_tests": len(self.results),
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "total_time_ms": total_time,
            "average_response_ms": avg_response if successful_tests else 0,
            "min_response_ms": min_response if successful_tests else 0,
            "max_response_ms": max_response if successful_tests else 0,
            "results": self.results
        }
    
    def save_results(self, filename="railway_performance_results.json"):
        """결과를 JSON 파일로 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "test_timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "results": self.results
            }, f, indent=2, ensure_ascii=False)
        print(f"📁 결과 저장: {filename}")

def main():
    """메인 실행 함수"""
    print("🚂 Railway 성능 최적화 효과 측정")
    print("=" * 50)
    
    tester = RailwayPerformanceTester()
    summary = tester.run_comprehensive_test()
    
    print("\n💾 결과 저장 중...")
    tester.save_results()
    
    print("\n🎉 성능 테스트 완료!")
    print(f"📊 요약: {summary['successful_tests']}/{summary['total_tests']} 성공")
    print(f"⚡ 평균 응답시간: {summary['average_response_ms']:.2f}ms")
    
    # 성능 비교 안내
    print("\n📋 최적화 전후 비교:")
    print("  최적화 전 예상:")
    print("    - 초기 로딩: 30초+")
    print("    - 대화 응답: 20-25초")
    print("    - 버튼 응답: 매우 느림")
    print("  최적화 후 목표:")
    print("    - 초기 로딩: 5초 미만")
    print("    - 대화 응답: 3-5초")
    print("    - 버튼 응답: 1초 미만")

if __name__ == "__main__":
    main() 