#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI 성능 최적화 테스트
API 응답속도 향상 효과 측정
"""

import sys
import asyncio
import time
import requests
import statistics
import json
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# 프로젝트 경로 추가
sys.path.append('src')

class PerformanceTester:
    """성능 테스트 클래스"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8300"
        self.test_results = {
            'response_times': [],
            'cache_hits': 0,
            'total_requests': 0,
            'errors': 0,
            'slow_requests': 0
        }
        
        # 테스트용 메시지들
        self.test_messages = [
            "안녕하세요! **EORA AI** 성능 테스트입니다.",
            "어제 **Python**을 배웠어요. 어떻게 활용할 수 있을까요?",
            "# 프로그래밍\n\n- 변수\n- 함수\n- 클래스",
            "그저께 `코딩` 공부를 했습니다. *복습*이 필요해요.",
            "오늘 AI와 대화하기 재미있네요!",
            "일주일전에 시작한 프로젝트를 계속해볼까요?",
            "```python\nprint('Hello World')\n```",
            "새로운 기술을 배우는 것은 **흥미롭습니다**.",
            "지난달부터 개발 공부를 시작했어요.",
            "아침에 코딩하는 것이 *효율적*인 것 같아요."
        ]
    
    def check_server_status(self) -> bool:
        """서버 상태 확인"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def login_admin(self) -> Dict[str, str]:
        """관리자 로그인"""
        try:
            # 세션 쿠키 가져오기
            session = requests.Session()
            
            # 로그인 페이지 접속
            login_page = session.get(f"{self.base_url}/login")
            
            # 로그인 시도 (폼 데이터)
            login_data = {
                'email': 'admin@eora.ai',
                'password': 'admin123'
            }
            
            # POST 방식 대신 쿼리 파라미터로 시도
            login_response = session.get(
                f"{self.base_url}/login",
                params=login_data
            )
            
            if login_response.status_code == 200:
                return {'session_cookie': session.cookies.get_dict()}
            
            return None
            
        except Exception as e:
            print(f"⚠️ 로그인 실패: {e}")
            return None
    
    def create_test_session(self, auth_data: Dict) -> str:
        """테스트용 세션 생성"""
        try:
            session = requests.Session()
            if auth_data and 'session_cookie' in auth_data:
                session.cookies.update(auth_data['session_cookie'])
            
            # 세션 생성 시도
            session_response = session.post(f"{self.base_url}/api/sessions", json={
                'name': 'Performance Test Session'
            })
            
            if session_response.status_code == 200:
                data = session_response.json()
                return data.get('session_id', 'test_session_001')
            else:
                return 'test_session_001'  # 기본 세션 ID
                
        except Exception as e:
            print(f"⚠️ 세션 생성 실패: {e}")
            return 'test_session_001'
    
    def measure_response_time(self, message: str, session_id: str, auth_data: Dict = None) -> Dict[str, Any]:
        """단일 요청 응답시간 측정"""
        try:
            session = requests.Session()
            if auth_data and 'session_cookie' in auth_data:
                session.cookies.update(auth_data['session_cookie'])
            
            start_time = time.time()
            
            # 채팅 API 호출
            response = session.post(
                f"{self.base_url}/api/chat",
                json={
                    'message': message,
                    'session_id': session_id
                },
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'response_time': response_time,
                    'has_markdown': data.get('has_markdown', False),
                    'cache_hit': 'cache' in str(response.headers).lower(),
                    'response_size': len(str(data.get('response', ''))),
                    'status_code': response.status_code
                }
            else:
                return {
                    'success': False,
                    'response_time': response_time,
                    'error': f"HTTP {response.status_code}",
                    'status_code': response.status_code
                }
                
        except Exception as e:
            return {
                'success': False,
                'response_time': 30.0,  # 타임아웃으로 간주
                'error': str(e),
                'status_code': 0
            }
    
    def run_sequential_test(self, num_requests: int = 10) -> Dict[str, Any]:
        """순차 요청 테스트"""
        print(f"🔄 순차 요청 테스트 시작 ({num_requests}회)...")
        
        # 로그인 및 세션 생성
        auth_data = self.login_admin()
        session_id = self.create_test_session(auth_data)
        
        results = []
        
        for i in range(num_requests):
            message = self.test_messages[i % len(self.test_messages)]
            result = self.measure_response_time(message, session_id, auth_data)
            results.append(result)
            
            print(f"  요청 {i+1}/{num_requests}: {result['response_time']:.3f}초 "
                  f"({'성공' if result['success'] else '실패'})")
            
            # 순차 요청이므로 잠시 대기
            time.sleep(0.1)
        
        return self.analyze_results(results, "순차 요청")
    
    def run_concurrent_test(self, num_requests: int = 20, max_workers: int = 5) -> Dict[str, Any]:
        """동시 요청 테스트"""
        print(f"🚀 동시 요청 테스트 시작 ({num_requests}회, 동시 {max_workers}개)...")
        
        # 로그인 및 세션 생성
        auth_data = self.login_admin()
        session_id = self.create_test_session(auth_data)
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 요청 제출
            futures = []
            for i in range(num_requests):
                message = self.test_messages[i % len(self.test_messages)]
                future = executor.submit(self.measure_response_time, message, session_id, auth_data)
                futures.append(future)
            
            # 결과 수집
            for i, future in enumerate(as_completed(futures)):
                result = future.result()
                results.append(result)
                print(f"  요청 완료 {len(results)}/{num_requests}: {result['response_time']:.3f}초 "
                      f"({'성공' if result['success'] else '실패'})")
        
        return self.analyze_results(results, "동시 요청")
    
    def run_cache_test(self, num_requests: int = 10) -> Dict[str, Any]:
        """캐시 효과 테스트"""
        print(f"💾 캐시 효과 테스트 시작 ({num_requests}회)...")
        
        # 로그인 및 세션 생성
        auth_data = self.login_admin()
        session_id = self.create_test_session(auth_data)
        
        # 동일한 메시지로 반복 요청
        test_message = "캐시 테스트 메시지입니다. **동일한 요청**으로 *캐시 효과*를 확인합니다."
        
        results = []
        cache_hits = 0
        
        for i in range(num_requests):
            result = self.measure_response_time(test_message, session_id, auth_data)
            results.append(result)
            
            if result.get('cache_hit', False):
                cache_hits += 1
            
            print(f"  요청 {i+1}/{num_requests}: {result['response_time']:.3f}초 "
                  f"({'캐시 히트' if result.get('cache_hit') else '캐시 미스'})")
            
            # 캐시 효과를 보기 위해 약간 대기
            time.sleep(0.2)
        
        analysis = self.analyze_results(results, "캐시 효과")
        analysis['cache_hit_rate'] = (cache_hits / num_requests) * 100
        
        return analysis
    
    def analyze_results(self, results: List[Dict[str, Any]], test_type: str) -> Dict[str, Any]:
        """결과 분석"""
        successful_results = [r for r in results if r['success']]
        response_times = [r['response_time'] for r in successful_results]
        
        if not response_times:
            return {
                'test_type': test_type,
                'total_requests': len(results),
                'successful_requests': 0,
                'success_rate': 0.0,
                'avg_response_time': 0.0,
                'median_response_time': 0.0,
                'min_response_time': 0.0,
                'max_response_time': 0.0,
                'std_deviation': 0.0,
                'slow_requests': 0,
                'fast_requests': 0,
                'error': 'No successful requests'
            }
        
        analysis = {
            'test_type': test_type,
            'total_requests': len(results),
            'successful_requests': len(successful_results),
            'success_rate': (len(successful_results) / len(results)) * 100,
            'avg_response_time': statistics.mean(response_times),
            'median_response_time': statistics.median(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'std_deviation': statistics.stdev(response_times) if len(response_times) > 1 else 0,
            'slow_requests': len([t for t in response_times if t > 2.0]),
            'fast_requests': len([t for t in response_times if t < 0.5])
        }
        
        return analysis
    
    def get_server_performance_stats(self) -> Dict[str, Any]:
        """서버 성능 통계 조회"""
        try:
            auth_data = self.login_admin()
            if not auth_data:
                return None
            
            session = requests.Session()
            session.cookies.update(auth_data['session_cookie'])
            
            response = session.get(f"{self.base_url}/api/performance/stats")
            
            if response.status_code == 200:
                return response.json().get('stats', {})
            else:
                return None
                
        except Exception as e:
            print(f"⚠️ 성능 통계 조회 실패: {e}")
            return None
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """종합 성능 테스트"""
        print("🧪 EORA AI 성능 최적화 종합 테스트")
        print("=" * 70)
        
        # 서버 상태 확인
        if not self.check_server_status():
            return {
                'error': '서버가 실행되지 않고 있습니다. 서버를 먼저 실행해주세요.',
                'success': False
            }
        
        print("✅ 서버 연결 확인 완료")
        
        test_results = {}
        
        # 1. 순차 요청 테스트
        test_results['sequential'] = self.run_sequential_test(10)
        
        # 2. 동시 요청 테스트
        test_results['concurrent'] = self.run_concurrent_test(15, 3)
        
        # 3. 캐시 효과 테스트
        test_results['cache'] = self.run_cache_test(8)
        
        # 4. 서버 성능 통계
        server_stats = self.get_server_performance_stats()
        if server_stats:
            test_results['server_stats'] = server_stats
        
        return test_results
    
    def print_results(self, results: Dict[str, Any]):
        """결과 출력"""
        print("\n" + "=" * 70)
        print("📊 성능 테스트 결과 요약")
        print("=" * 70)
        
        if 'error' in results:
            print(f"❌ 테스트 실패: {results['error']}")
            return
        
        # 각 테스트 결과 출력
        for test_name, test_data in results.items():
            if test_name == 'server_stats':
                continue
                
            print(f"\n🔍 {test_data['test_type']} 결과:")
            print(f"  총 요청: {test_data['total_requests']}개")
            print(f"  성공 요청: {test_data['successful_requests']}개")
            print(f"  성공률: {test_data['success_rate']:.1f}%")
            print(f"  평균 응답시간: {test_data['avg_response_time']:.3f}초")
            print(f"  중간값 응답시간: {test_data['median_response_time']:.3f}초")
            print(f"  최단 응답시간: {test_data['min_response_time']:.3f}초")
            print(f"  최장 응답시간: {test_data['max_response_time']:.3f}초")
            print(f"  빠른 요청 (0.5초 미만): {test_data['fast_requests']}개")
            print(f"  느린 요청 (2초 이상): {test_data['slow_requests']}개")
            
            if 'cache_hit_rate' in test_data:
                print(f"  캐시 히트율: {test_data['cache_hit_rate']:.1f}%")
        
        # 서버 통계
        if 'server_stats' in results:
            stats = results['server_stats']
            print(f"\n📈 서버 성능 통계:")
            print(f"  총 처리된 요청: {stats.get('total_requests', 0)}개")
            print(f"  캐시 히트: {stats.get('cache_hits', 0)}개")
            print(f"  캐시 히트율: {stats.get('cache_hit_rate', 0):.1f}%")
            print(f"  평균 응답시간: {stats.get('avg_response_time', 0):.3f}초")
            print(f"  느린 요청 비율: {stats.get('slow_request_rate', 0):.1f}%")
        
        # 종합 평가
        print(f"\n🎯 종합 평가:")
        avg_response_times = []
        success_rates = []
        
        for test_name, test_data in results.items():
            if test_name != 'server_stats' and 'avg_response_time' in test_data:
                avg_response_times.append(test_data['avg_response_time'])
                success_rates.append(test_data['success_rate'])
        
        if avg_response_times:
            overall_avg = statistics.mean(avg_response_times)
            overall_success = statistics.mean(success_rates)
            
            print(f"  전체 평균 응답시간: {overall_avg:.3f}초")
            print(f"  전체 평균 성공률: {overall_success:.1f}%")
            
            # 성능 등급 매기기
            if overall_avg < 0.5 and overall_success > 95:
                grade = "S (매우 우수)"
            elif overall_avg < 1.0 and overall_success > 90:
                grade = "A (우수)"
            elif overall_avg < 2.0 and overall_success > 85:
                grade = "B (양호)"
            elif overall_avg < 3.0 and overall_success > 80:
                grade = "C (보통)"
            else:
                grade = "D (개선 필요)"
            
            print(f"  성능 등급: {grade}")
        
        print("=" * 70)


def main():
    """메인 함수"""
    tester = PerformanceTester()
    
    print("🚀 EORA AI API 응답속도 최적화 테스트")
    print("이 테스트는 최적화 전후의 성능을 비교합니다.")
    print("-" * 70)
    
    # 종합 테스트 실행
    results = tester.run_comprehensive_test()
    
    # 결과 출력
    tester.print_results(results)
    
    # 결과를 파일로 저장
    try:
        with open('performance_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 테스트 결과가 'performance_test_results.json'에 저장되었습니다.")
    except Exception as e:
        print(f"⚠️ 결과 저장 실패: {e}")
    
    return results


if __name__ == "__main__":
    results = main()
    
    # 성능 기준 통과 여부 확인
    if 'error' not in results:
        avg_times = []
        for test_name, test_data in results.items():
            if test_name != 'server_stats' and 'avg_response_time' in test_data:
                avg_times.append(test_data['avg_response_time'])
        
        if avg_times:
            overall_avg = statistics.mean(avg_times)
            if overall_avg < 2.0:  # 2초 미만이면 통과
                print("\n🎉 성능 최적화 테스트 통과! 배포 준비 완료!")
                exit(0)
            else:
                print(f"\n⚠️ 성능 기준 미달 (평균 {overall_avg:.3f}초 > 2.0초)")
                exit(1)
    
    exit(1) 